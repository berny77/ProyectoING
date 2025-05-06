class TXTReader:
    def __init__(self, ruta):
        self.ruta = ruta

    def leer(self):
        try:
            with open(self.ruta, 'r', encoding='utf-8') as archivo:
                return archivo.read()
        except Exception as e:
            raise ValueError(f"Error al procesar el archivo TXT: {e}")
