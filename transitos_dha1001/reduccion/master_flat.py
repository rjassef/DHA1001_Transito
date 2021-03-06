import numpy as np
from astropy.io import fits

from astropy.stats import sigma_clipped_stats

def crear_masterflat(imagenes, nombre_flat="MasterFlat.fits",
                     nombre_dark="MasterDark.fits",
                     nombre_bias="MasterBias.fits",
                     directorio_imagenes_originales="raw", directorio_imagenes_reducidas="red",
                     recalcular=True):
    """
    Rutina para crear el Master Flat. Esta rutina combina las imagenes de flat, después de sustraer el bias y dark, tomadas por la camara del telescopio MAS de 50cm en El Sauce y genera el cuadro de dark que vamos a usar en la reducción de las otras imágenes.

    Parámetros
    ----------

    imagenes: lista
        Lista de las imagenes que vamos a combinar.

    nombre_flat: string, opcional
        Nombre de la imagen de salida que va a tener el cuadro de Flat combinado.

    nombre_dark: string, opcional
        Nombre de la imagen que tiene el cuadro de dark combinado.

    nombre_bias: string, opcional
        Nombre de la imagen que tiene el cuadro de bias combinado.

    directorio_imagenes_originales: string, opcional
        Directorio donde están las imágenes tomadas por el telescopio.

    directorio_imagenes_reducidas: string, opcional
        Directorio donde vamos a guardar las imagenes reducidas.

    recalcular: boolean, opcional
        Debe ser True para que la imagen sea recalculada si ya existe.

    """

    #Tratemos de abrir la imagen. Si no existe, o si se ha pedido recalcularla, proseguir con la combinación.
    try:
        if recalcular:
            raise FileNotFoundError
        master_flat = fits.open("{}/{}".format(directorio_imagenes_reducidas, nombre_flat))
        master_flat.close()
        return
    except FileNotFoundError:
        pass

    #Abrir el master dark y el master bias.
    if nombre_bias is not None:
        master_bias = fits.open("{}/{}".format(directorio_imagenes_reducidas, nombre_bias))
    if nombre_dark is not None:
        master_dark = fits.open("{}/{}".format(directorio_imagenes_reducidas, nombre_dark))

    #Lista donde vamos a guardar los arrays con las imagenes de flats sin dark y sin bias.
    all_flats = []

    #Iteramos por todas las imagenes sustrayendo el dark y el bias.
    for imagen in imagenes:
        fname = "{}/{}".format(directorio_imagenes_originales, imagen)
        h = fits.open(fname)

        #Sustrer el bias y el dark.
        h[0].data = np.float64(h[0].data)
        if nombre_bias is not None:
            h[0].data -= master_bias[0].data
        if nombre_dark is not None:
            h[0].data -= master_dark[0].data

        #Normalizamos las imagenes para que todas tengan la misma mediana.
        norm = np.median(h[0].data)
        h[0].data /= norm

        #Guardamos la imagen de flat normalizada.
        all_flats.append(h[0].data)


    #Vamos a calcular la mediana haciendo una reyección estadística de 3 sigma en cada pixel.
    flat_promedio, flat_mediana, flat_dispersion = sigma_clipped_stats(all_flats, axis=0)
    master_flat = flat_mediana

    #Finalmente, si hay algun pixel con flujo 0 o negativo (lo que es solo debido a fluctuaciones estadísticas), lo vamos a reemplazar por el menor valor positivo en la imagen. Esto no tiene un impacto medible, pues deberían ser muy poco pixeles, pero evita errores en los cálculos.
    min_val = np.min(master_flat[master_flat>0])
    master_flat[master_flat<=0] = min_val

    #Guardamos el flat.
    fits.writeto("{}/{}".format(directorio_imagenes_reducidas, nombre_flat), master_flat, overwrite=True)

    return
