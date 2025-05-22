import os
from flask import Flask, request, jsonify
from flask_cors import CORS 

from Modules.Chroma import Chroma         
from Modules.Logic import procesar_archivo 

app = Flask(__name__)
CORS(app) 

chroma = Chroma()

UPLOAD_FOLDER = './tmp'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  


@app.route('/')
def inicio():
    return "API LISTA"


@app.route('/subir', methods=['POST'])
def subir_documento():
    if 'archivo' not in request.files:
        return jsonify({"error": "No se envió ningún archivo"}), 400

    archivo = request.files['archivo']
    if archivo.filename == '':
        return jsonify({"error": "Nombre de archivo vacío"}), 400

    try:
        nombre = archivo.filename
        ruta = os.path.join(UPLOAD_FOLDER, nombre)
        archivo.save(ruta)

        contenido = procesar_archivo(ruta)

        chroma.guardar_documento(contenido, nombre, ruta)

        return jsonify({"mensaje": f"Documento '{nombre}' guardado exitosamente"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/documentos', methods=['GET'])
def obtener_documentos():
    try:
        documentos, metadatos = chroma.obtener_documentos()

        lista = [
            {"nombre": meta.get("nombre", "sin nombre"), "contenido": doc[:500]}
            for doc, meta in zip(documentos, metadatos)
        ]
        return jsonify(lista)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/documento/<nombre>', methods=['GET'])
def ver_documento(nombre):
    try:
        documentos, metadatos = chroma.obtener_documentos()
        for doc, meta in zip(documentos, metadatos):
            if meta.get("nombre") == nombre:
                return jsonify({
                    "nombre": nombre,
                    "contenido": doc,
                    "metadatos": meta
                })
        return jsonify({"error": f"Documento '{nombre}' no encontrado"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/documento/<nombre>', methods=['DELETE'])
def eliminar_documento(nombre):
    try:
        chroma.eliminar_documento(nombre)
        return jsonify({"mensaje": f"Documento '{nombre}' eliminado exitosamente"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@app.route('/buscar', methods=['GET'])
def buscar_documentos():
    palabra = request.args.get('q', '').lower()
    
    if not palabra:
        return jsonify({"error": "Se requiere un parámetro de búsqueda (q)"}), 400

    try:
        documentos, metadatos = chroma.obtener_documentos()
        resultados = []

        for doc, meta in zip(documentos, metadatos):
            if palabra in doc.lower():
                resultados.append({
                    "nombre": meta.get("nombre", "sin nombre"),
                    "contenido": doc[:500] 
                })

        return jsonify(resultados)
    except Exception as e:
        return jsonify({"error": str(e)}), 500