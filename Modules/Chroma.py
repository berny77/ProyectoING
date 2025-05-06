import os
from chromadb import PersistentClient

class Chroma:
    def __init__(self, persist_directory="./chroma_db"):
        self.directorio_persistente = persist_directory

        os.makedirs(self.directorio_persistente, exist_ok=True)

        try:
            self.client = PersistentClient(path=self.directorio_persistente)
            print("Cliente de ChromaDB inicializado con persistencia")
        except Exception as e:
            print(f"Error al inicializar el cliente de ChromaDB: {e}")
            self.client = None

        self.verificar_colecciones()

    def verificar_colecciones(self):
        try:
            self.collection = self.client.get_or_create_collection("documentos")
            print("Colección 'documentos' lista para usar.")
        except Exception as e:
            print(f"Error al verificar las colecciones: {e}")
            self.collection = None

    def guardar_documento(self, contenido, nombre_documento, ruta_archivo):
        if not self.collection:
            print("No se puede guardar: colección no disponible.")
            return

        try:
            self.collection.add(
                documents=[contenido],
                metadatas=[{"nombre": nombre_documento}],
                ids=[nombre_documento]
            )
            print(f"Documento '{nombre_documento}' guardado en ChromaDB.")

            self.guardar_documento_local(ruta_archivo, nombre_documento)

        except Exception as e:
            print(f"Error al guardar el documento: {e}")

    def guardar_documento_local(self, ruta_archivo, nombre_documento):
        try:
            destino = os.path.join(self.directorio_persistente, nombre_documento)
            with open(ruta_archivo, 'rb') as archivo_origen, open(destino, 'wb') as archivo_destino:
                archivo_destino.write(archivo_origen.read())
            print(f"Documento '{nombre_documento}' guardado localmente.")
        except Exception as e:
            print(f"Error al guardar el archivo localmente: {e}")

    def obtener_documentos(self):
        if not self.collection:
            print("No se puede obtener: colección no disponible.")
            return [], []

        try:
            documentos = self.collection.get()
            if documentos and documentos['documents']:
                return documentos['documents'], documentos['metadatas']
            else:
                print("No hay documentos guardados.")
                return [], []
        except Exception as e:
            print(f"Error al obtener documentos: {e}")
            return [], []
