from docx import Document

class DOCXReader:
    def __init__(self, ruta):
        self.ruta = ruta

    def leer(self):
        try:
            documento = Document(self.ruta)
            contenido = "\n".join([p.text for p in documento.paragraphs])
            return contenido
        except Exception as e:
            raise ValueError(f"Error al procesar el archivo DOCX: {e}")
