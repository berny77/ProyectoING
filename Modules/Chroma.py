import os
from chromadb import HttpClient

#api de chroma
class Chroma:
    def __init__(self, persist_directory="./chroma_db"):
        self.directorio_persistente = persist_directory
        os.makedirs(self.directorio_persistente, exist_ok=True)

        try:
            CHROMA_HOST = os.getenv("CHROMADB_HOST", "localhost")  # Cambia CHROMA por CHROMADB
            CHROMA_PORT = os.getenv("CHROMADB_PORT", "8000")


            self.client = HttpClient(host=CHROMA_HOST, port=int(CHROMA_PORT))
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



    def eliminar_documento(self, nombre_documento):
        """Elimina un documento de ChromaDB y del almacenamiento local."""
        if not self.collection:
            print("Colección no disponible.")
            return

        try:
            # Eliminar de la colección ChromaDB
            self.collection.delete(ids=[nombre_documento])
            print(f"Documento '{nombre_documento}' eliminado de ChromaDB.")

            # Eliminar del almacenamiento local
            ruta_local = os.path.join(self.directorio_persistente, nombre_documento)
            if os.path.exists(ruta_local):
                os.remove(ruta_local)
                print(f"Documento '{nombre_documento}' eliminado localmente.")
            else:
                print(f"No se encontró el archivo local '{nombre_documento}' para eliminar.")
        except Exception as e:
            print(f"Error al eliminar el documento '{nombre_documento}': {e}")





def buscar_documentos(self, texto_consulta, cantidad_resultados=3):
    """
    Busca documentos en ChromaDB similares al texto de consulta.

    :param texto_consulta: Texto para buscar en la base de datos.
    :param cantidad_resultados: Número máximo de resultados a devolver.
    :return: Lista de diccionarios con documentos y sus metadatos.
    """
    if not self.collection:
        return []

    try:
        resultados = self.collection.query(
            query_texts=[texto_consulta],
            n_results=cantidad_resultados
        )
        documentos = resultados.get('documents', [[]])[0]  # lista de strings
        metadatos = resultados.get('metadatas', [[]])[0]  # lista de dicts

        combinados = [
            {"contenido": doc, "metadatos": meta}
            for doc, meta in zip(documentos, metadatos)
        ]
        return combinados

    except Exception as e:
        return []
