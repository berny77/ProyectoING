import PyPDF2

class PDFReader:
    def __init__(self, ruta):
        self.ruta = ruta

    def leer(self):
        try:
            contenido = ""
            with open(self.ruta, 'rb') as archivo:
                lector = PyPDF2.PdfReader(archivo)
                for pagina in lector.pages:
                    contenido += pagina.extract_text() + "\n"
            return contenido
        except Exception as e:
            raise ValueError(f"Error al procesar el archivo PDF: {e}")
