import numpy as np
import re

from astropy.io import fits
from astropy.stats import sigma_clipped_stats

from photutils import DAOStarFinder, centroid_sources, centroid_com

import subprocess

def dao_busqueda(imagen, directorio_imagenes_reducidas="imagenes_reducidas", directorio_fotometria="fot", recalcular=True):
    """
    Función que busca fuentes (estrellas) en una imagen.

    Parametros
    ----------

    imagen: str
        Nombre del archivo que contiene la imagen en la que se hará la búsqueda.

    directorio_imagenes_reducidas: string, opcional
        Nombre del directorio donde se encuentran la imagen en que se hará la búsqueda.

    directorio_fotometria: string, opcional
        Nombre del directorio donde se guardarán los datos fotométricos.

    recalcular: boolean, opcional
        Debe ser igual a True si se desea recalcular las posiciones.

    """

    #Crear el directorio de la fotometria si no existe.
    subprocess.call(["mkdir",directorio_fotometria], stderr=subprocess.DEVNULL)

    #Determinar el nombre del archivo con las posiciones.
    pos_fname = re.sub(".fits?",".pos.dat",imagen)
    try:
        #Si se ha pedido recalcular, avanzar inmediatamente a la excepción.
        if recalcular:
            raise OSError

        #Tratar de leer el archivo. Si el archivo no existe, se levantará la excepción OSError, que llevará a calcular las posiciones.
        pos_data = np.loadtxt("{}/{}".format(directorio_fotometria,pos_fname))
        x = pos_data[:,0]
        y = pos_data[:,1]

    except OSError:

        print("Buscando fuentes en la imagen ",imagen)

        #Abrir la imagen.
        h = fits.open("{}/{}".format(directorio_imagenes_reducidas, imagen))

        #Calcular la mediana y desviación estándar haciendo reyección de 3 sigma para solo contabilizar el cielo.
        mean, median, std = sigma_clipped_stats(h[0].data, sigma=3.0)

        #Buscar las fuentes. Su brillo debe estar 20 veces sobre el ruido del cielo.
        daofind = DAOStarFinder(fwhm=3.0, threshold=20.*std)
        fuentes = daofind(h[0].data - median)
        x = fuentes['xcentroid']
        y = fuentes['ycentroid']
        h.close()

        #Solo vamos a querer fuentes lejos de los bordes.
        cond = (x>150) & (x<1850) & (y>150) & (y<1850)
        x = x[cond]
        y = y[cond]

        #Guardar las posiciones en el archivo correspondiente.
        np.savetxt("{}/{}".format(directorio_fotometria, pos_fname), np.array([x,y]).T)

    #Poner todas las posiciones en un solo arreglo y devolverlo.
    posiciones = np.vstack((x,y)).T
    return posiciones


def dao_recentrar(imagen, posiciones_referencia, directorio_imagenes_reducidas="imagenes_reducidas", directorio_fotometria="fot", caja_busqueda=21, recalcular=False):
    """
    Rutina para recentrar un set de posiciones de referencia. Estas posiciones de referencia deben haber sido calculadas con la función dao_busqueda.

    Parametros
    ----------

    imagen: str
        Nombre del archivo que contiene la imagen en la que se centrarán las fuentes.

    posiciones_referencia: numpy array
        Arreglo con las posiciones de las fuentes en la imagen de referencia. Debe ser generado por la función dao_busqueda.

    directorio_imagenes_reducidas: string, opcional
        Nombre del directorio donde se encuentran la imagen en que se hará la búsqueda.

    directorio_fotometria: string, opcional
        Nombre del directorio donde se guardarán los datos fotométricos.

    caja_busqeda: int, opcional
        Tamaño de la caja de búsqueda de las fuentes.

    recalcular: boolean, opcional
        Debe ser igual a True si se desea recalcular las posiciones.

    """

    print("Recentrando fuentes en la imagen",imagen)

    #Nombre donde estarían guardadas las posiciones recentradas.
    pos_fname = re.sub(".fits?",".pos.dat",imagen)

    try:
        #Si se ha pedido recalcular, avanzar inmediatamente a la excepción.
        if recalcular:
            raise OSError

        #Tratar de leer el archivo. Si el archivo no existe, se levantará la excepción OSError, que llevará a calcular las posiciones.
        pos_data = np.loadtxt("{}/{}".format(directorio_fotometria,pos_fname))
        x = pos_data[:,0]
        y = pos_data[:,1]

    except OSError:

        #Abrir la image,
        h = fits.open("{0:s}/{1:s}".format(directorio_imagenes_reducidas, imagen))

        #Tomar las posiciones de referencia y recentrar las fuentes alrededor de estas posiciones tomando una caja de tamaño caja_busqueda.
        x_ref = np.copy(posiciones_referencia[:,0])
        y_ref = np.copy(posiciones_referencia[:,1])
        x, y = centroid_sources(h[0].data, x_ref, y_ref, box_size=caja_busqueda, centroid_func=centroid_com)
        h.close()

        #Guardar las posiciones en el archivo correspondiente.
        np.savetxt("{}/{}".format(directorio_fotometria, pos_fname), np.array([x,y]).T)

    #Poner las posiciones en un solo arreglo y devolver el arreglo.
    posiciones = np.vstack((x,y)).T
    return posiciones
