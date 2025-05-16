import os
from flask import Flask, request, jsonify

from Modules.Chroma import Chroma          # Para manejar la base vectorial
from Modules.Logic import procesar_archivo # Para procesar el contenido del archivo

# instancia de la aplicación Flask
app = Flask(__name__)

# Inicializa ChromaDB
chroma = Chroma()

# Define una carpeta temporal para guardar archivos cargados
UPLOAD_FOLDER = './tmp'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Crea la carpeta si no existe


@app.route('/')
def inicio():
    return " API Flask para documentos con ChromaDB"


@app.route('/subir', methods=['POST'])
def subir_documento():
    
    if 'archivo' not in request.files:
        return jsonify({"error": "No se envió ningún archivo"}), 400

    archivo = request.files['archivo']
    if archivo.filename == '':
        return jsonify({"error": "Nombre de archivo vacío"}), 400

    try:
        # Guarda el archivo recibido en la carpeta temporal
        nombre = archivo.filename
        ruta = os.path.join(UPLOAD_FOLDER, nombre)
        archivo.save(ruta)

        # lee y genera embeddings
        contenido = procesar_archivo(ruta)

        # Guarda el contenido vectorizado en ChromaDB y también copia local
        chroma.guardar_documento(contenido, nombre, ruta)

        return jsonify({"mensaje": f"Documento '{nombre}' guardado exitosamente"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/documentos', methods=['GET'])
def obtener_documentos():
    try:
        # Recupera documentos y sus metadatos desde ChromaDB
        documentos, metadatos = chroma.obtener_documentos()

        lista = [
            {"nombre": meta.get("nombre", "sin nombre"), "contenido": doc[:500]}
            for doc, meta in zip(documentos, metadatos)
        ]
        return jsonify(lista)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Punto de entrada principal: arranca la app en modo debug en el puerto 5000
if __name__ == '__main__':
    app.run(debug=True, port=5000)
