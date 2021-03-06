name = "transitos_dha1001"

#Importar todos los modulos de reduccion.
from .reduccion.master_bias import crear_masterbias
from .reduccion.master_dark import crear_masterdark
from .reduccion.master_flat import crear_masterflat
from .reduccion.science import reducir_imagenes_ciencia
from .reduccion.desplegar_imagenes import desplegar_imagen
from .reduccion.alinear import alinear_imagenes_ciencia

from .fotometria.dao import dao_busqueda, dao_recentrar, filtrar_posiciones
from .fotometria.phot import medir_fotometria
from .fotometria.curva_de_luz import curva_de_luz, graficar_curva_de_luz
