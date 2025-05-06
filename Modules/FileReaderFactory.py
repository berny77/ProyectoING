import os
from Readers.PDFReader import PDFReader
from Readers.DOCXReader import DOCXReader
from Readers.TXTReader import TXTReader
from Readers.ExcelReader import ExcelReader

def obtener_lector(ruta):
    if not os.path.exists(ruta):  #revisar extensiones 
        raise FileNotFoundError(f"El archivo {ruta} no se encuentra en el sistema.")
    
    ext = os.path.splitext(ruta)[1].lower()
    if ext == '.pdf':
        return PDFReader(ruta)
    elif ext == '.docx':
        return DOCXReader(ruta)
    elif ext == '.txt':
        return TXTReader(ruta)
    elif ext in ['.xls', '.xlsx']:
        return ExcelReader(ruta)
    else:
        raise ValueError(f"Tipo de archivo no compatible: {ext}")
