import os
from .FileReaderFactory import obtener_lector

def procesar_archivo(ruta):
    if not os.path.exists(ruta):  #archivo inexistente 
        raise FileNotFoundError(f"El archivo {ruta} no se encuentra en el sistema.")
    
    lector = obtener_lector(ruta)
    return lector.leer()
