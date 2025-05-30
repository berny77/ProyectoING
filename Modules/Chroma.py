import os
from chromadb import HttpClient
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class Chroma:
    def __init__(self, persist_directory="./chroma_db"):
        self.directorio_persistente = persist_directory
        os.makedirs(self.directorio_persistente, exist_ok=True)

        try:
            CHROMA_HOST = os.getenv("CHROMADB_HOST", "chromadb")
            CHROMA_PORT = os.getenv("CHROMADB_PORT", "8000")
            self.client = HttpClient(host=CHROMA_HOST, port=int(CHROMA_PORT))
        except Exception as e:
            self.client = None

        self.verificar_colecciones()

        try:
            self.nlp = spacy.load("es_core_news_sm")
        except Exception as e:
            print(f"Error al cargar el modelo de Spacy: {e}")
            self.nlp = None

    def verificar_colecciones(self):
        if not self.client:
            print("No hay cliente para crear o recuperar la colección.")
            self.collection = None
            return

        try:
            self.collection = self.client.get_or_create_collection(name="documentos")
            print("Colección 'documentos' lista.")
        except Exception as e:
            print(f"Error al crear o recuperar la colección: {e}")
            self.collection = None



    def buscar_coincidencias(self, termino: str, umbral_similitud=0.2):
        if not self.collection:
            return []

        try:
            resultado = self.collection.get()
            documentos = resultado.get("documents", [])
            metadatos = resultado.get("metadatas", [])

            if not documentos:
                print("No se encontraron documentos en la base de datos.")
                return []

            vectorizer = TfidfVectorizer().fit_transform([termino] + documentos)
            vectors = vectorizer.toarray()

            similitudes = cosine_similarity(vectors[0:1], vectors[1:]).flatten()

            coincidencias = []
            for doc, meta, similitud in zip(documentos, metadatos, similitudes):
                if similitud >= umbral_similitud:
                    coincidencias.append({
                        "nombre": meta.get("nombre", "sin nombre"),
                        "contenido": doc,
                        "metadatos": meta,
                        "similitud": float(similitud)
                    })

            # Ordenar las coincidencias por similitud descendente
            coincidencias.sort(key=lambda x: x["similitud"], reverse=True)

            for coincidencia in coincidencias:
                print(f"Coincidencia encontrada en '{coincidencia['nombre']}' con similitud {coincidencia['similitud']}:")
                print(coincidencia['contenido'])
                print("---")

            return coincidencias

        except Exception as e:
            print(f"Error al buscar coincidencias: {e}")
            return []










    def dividir_en_chunks(self, texto):
        # Dividir el texto en párrafos usando saltos de línea
        parrafos = texto.split('\n')
        # Filtrar párrafos vacíos
        parrafos = [p for p in parrafos if p.strip() != ""]
        return parrafos

    def guardar_documento(self, contenido, nombre_documento):
        if not self.collection:
            print("No hay colección disponible para guardar el documento.")
            return

        try:
            print(f"Iniciando guardado del documento '{nombre_documento}'...")
            chunks = self.dividir_en_chunks(contenido)
            print(f"Documento dividido en {len(chunks)} fragmento(s).")

            documents = []
            metadatas = []
            ids = []

            for i, fragmento in enumerate(chunks):
                fragment_id = f"{nombre_documento}_chunk_{i+1}"
                documents.append(fragmento)
                metadatas.append({
                    "nombre": nombre_documento,
                    "chunk_index": i + 1,
                    "total_chunks": len(chunks)
                })
                ids.append(fragment_id)
                print(f"Preparado fragmento {i+1} con id '{fragment_id}'.")

            self.collection.add(documents=documents, metadatas=metadatas, ids=ids)
            print(f"Documento '{nombre_documento}' guardado correctamente con {len(chunks)} fragmento(s).")

        except Exception as e:
            print(f"Error al guardar el documento '{nombre_documento}': {e}")

    def reconstruir_documento(self, nombre_documento):
        if not self.collection:
            return None

        try:
            resultado = self.collection.get()
            documentos = resultado.get("documents", [])
            metadatos = resultado.get("metadatas", [])

            fragmentos = [
                (meta["chunk_index"], doc)
                for doc, meta in zip(documentos, metadatos)
                if meta.get("nombre") == nombre_documento
            ]

            if not fragmentos:
                return None

            fragmentos.sort(key=lambda x: x[0])
            texto_completo = "\n".join([frag[1] for frag in fragmentos])
            return texto_completo

        except Exception as e:
            return None

    def eliminar_documento(self, nombre_documento):
        if not self.collection:
            return

        try:
            resultado = self.collection.get()
            metadatos = resultado.get("metadatas", [])
            ids_a_eliminar = [
                resultado["ids"][i]
                for i, meta in enumerate(metadatos)
                if meta.get("nombre") == nombre_documento
            ]

            if ids_a_eliminar:
                self.collection.delete(ids=ids_a_eliminar)

        except Exception as e:
            pass

    def imprimir_base_datos_completa(self):
        if not self.collection:
            print("No hay colección para mostrar.")
            return

        try:
            resultado = self.collection.get(include=['documents', 'metadatas', 'ids', 'embeddings'])

            documentos = resultado.get('documents', [])
            metadatos = resultado.get('metadatas', [])
            ids = resultado.get('ids', [])
            embeddings = resultado.get('embeddings', [])

            print(f"Total registros en la base de datos: {len(documentos)}")
            print("---------------------------------------------------")

            for i, (doc, meta, id_, emb) in enumerate(zip(documentos, metadatos, ids, embeddings)):
                print(f"Registro #{i+1}")
                print(f"ID: {id_}")
                print(f"Documento: {doc}")
                print(f"Metadatos: {meta}")
                print(f"Embedding (primeros 5 valores): {emb[:5] if emb else 'No disponible'}")
                print("---------------------------------------------------")

        except Exception as e:
            print(f"Error al imprimir la base de datos: {e}")

    def armar_documentos(self):
        if not self.collection:
            return {}

        try:
            resultado = self.collection.get()
            documentos = resultado.get("documents", [])
            metadatos = resultado.get("metadatas", [])

            documentos_armados = {}

            fragmentos_por_doc = {}
            for doc, meta in zip(documentos, metadatos):
                nombre = meta.get("nombre")
                index = meta.get("chunk_index", 0)
                if nombre not in fragmentos_por_doc:
                    fragmentos_por_doc[nombre] = []
                fragmentos_por_doc[nombre].append((index, doc))

            for nombre, fragmentos in fragmentos_por_doc.items():
                fragmentos.sort(key=lambda x: x[0])
                texto_completo = "\n".join([frag[1] for frag in fragmentos])
                documentos_armados[nombre] = texto_completo

            return documentos_armados

        except Exception as e:
            return {}