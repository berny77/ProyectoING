import os
from chromadb import PersistentClient

#Api de chroma
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
        """Crea o accede a la colección de documentos."""
        if not self.client:
            print("Cliente de ChromaDB no disponible.")
            self.collection = None
            return

        try:
            self.collection = self.client.get_or_create_collection(name="documentos")
            print("Colección 'documentos' lista para usar.")
        except Exception as e:
            print(f"Error al obtener/crear colección: {e}")
            self.collection = None

    def guardar_documento(self, contenido, nombre_documento, ruta_archivo):
        """Guarda el documento tanto en ChromaDB como localmente."""
        if not self.collection:
            print("Colección no disponible.")
            return

        try:
            self.collection.add( #hace la coleccion
                documents=[contenido],
                metadatas=[{"nombre": nombre_documento}],
                ids=[nombre_documento]
            )
            print(f"Documento '{nombre_documento}' guardado en ChromaDB.")
            self.guardar_documento_local(ruta_archivo, nombre_documento)
        except Exception as e:
            print(f"Error al guardar en ChromaDB: {e}")
        self.imprimir_vectores()


    def guardar_documento_local(self, ruta_archivo, nombre_documento):
        """Guarda una copia local del documento en el directorio de persistencia."""
        try:
            destino = os.path.join(self.directorio_persistente, nombre_documento)
            with open(ruta_archivo, 'rb') as archivo_origen, open(destino, 'wb') as archivo_destino:
                archivo_destino.write(archivo_origen.read())
            print(f"Documento '{nombre_documento}' guardado localmente en: {destino}")
        except Exception as e:
            print(f"Error al guardar el archivo localmente: {e}")

    def obtener_documentos(self):
        """Recupera todos los documentos almacenados junto con sus metadatos."""
        if not self.collection:
            print("Colección no disponible.")
            return [], []

        try:
            resultado = self.collection.get()
            documentos = resultado.get('documents', [])
            metadatos = resultado.get('metadatas', [])
            print(f"Se recuperaron {len(documentos)} documento(s) desde ChromaDB.")
            return documentos, metadatos
        except Exception as e:
            print(f"Error al obtener documentos: {e}")
            return [], []
        
    def imprimir_vectores(self):
        if not self.collection:
            print("Colección no disponible.")
            return

        try:
            resultado = self.collection.get(include=['documents', 'embeddings', 'metadatas'])

            documentos = resultado.get('documents', [])
            embeddings = resultado.get('embeddings', [])
            metadatos = resultado.get('metadatas', [])

            for i, (doc, emb, meta) in enumerate(zip(documentos, embeddings, metadatos)):
                print(f"Documento {i+1}: {meta.get('nombre', 'Sin nombre')}")
                print(f"Contenido (resumen): {doc[:100]}...")
                print(f"Vector (embedding): {emb[:5]}... (total {len(emb)} dimensiones)")
                print("-" * 80)

        except Exception as e:
            print(f"Error al obtener vectores: {e}")

