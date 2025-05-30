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

        chroma.guardar_documento(contenido, nombre)  # Eliminar el argumento `ruta`

        # Mostrar el estado actual de la base de datos después de guardar el documento
        documentos_armados = chroma.armar_documentos()
        print(f"Estado actual de la base de datos Chroma después de guardar '{nombre}':")
        for doc_nombre, doc_contenido in documentos_armados.items():
            print(f"- Documento: {doc_nombre}, contenido parcial: {doc_contenido[:200]}...")

        return jsonify({"mensaje": f"Documento '{nombre}' guardado exitosamente"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500




@app.route('/documentos', methods=['GET'])
def obtener_documentos():
    try:
        documentos_armados = chroma.armar_documentos()

        lista = [
            {"nombre": nombre, "contenido": doc[:500]}
            for nombre, doc in documentos_armados.items()
        ]
        return jsonify(lista)
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/documento/<nombre>', methods=['GET'])
def ver_documento(nombre):
    try:
        # Utilizar reconstruir_documento para obtener el documento completo
        documento_completo = chroma.reconstruir_documento(nombre)
        if documento_completo:
            return jsonify({
                "nombre": nombre,
                "contenido": documento_completo
            })
        else:
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

@app.route('/preguntar', methods=['POST'])
def responder():
    try:
        datos = request.get_json()
        pregunta = datos.get("pregunta", "").strip()

        if not pregunta:
            return jsonify({"error": "No se recibió una pregunta válida."}), 400

        respuesta = chroma.responder_pregunta(pregunta)

        if respuesta:
            return jsonify({"respuesta": respuesta})
        else:
            return jsonify({"respuesta": "No se encontró información relevante sobre tu pregunta."})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    





    
@app.route('/buscar_coincidencias', methods=['POST'])
def buscar_coincidencias():
    try:
        datos = request.get_json()
        termino = datos.get("termino", "").strip()

        if not termino:
            return jsonify({"error": "No se recibió un término de búsqueda válido."}), 400

        # Llamar al método buscar_coincidencias con el término proporcionado
        coincidencias = chroma.buscar_coincidencias(termino)

        if coincidencias:
            return jsonify(coincidencias)
        else:
            return jsonify({"mensaje": "No se encontraron coincidencias relevantes."}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
