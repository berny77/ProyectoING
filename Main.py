import os
from tkinter import Tk, filedialog, Button, Label, Toplevel, Scrollbar, Text, Frame
from Modules.Logic import procesar_archivo
from Modules.Chroma import Chroma 

chroma_db = Chroma()

def elegir_archivo():
    archivo = filedialog.askopenfilename(
        title="Selecciona un archivo",
        filetypes=[("Todos los archivos", "*.*"), ("Documentos", "*.pdf *.docx *.txt *.xlsx *.png *.jpg")]
    )
    if archivo:
        print(f"Ruta del archivo seleccionado: {archivo}")
        if os.path.exists(archivo):
            try:
                contenido = procesar_archivo(archivo)
                nombre_documento = os.path.basename(archivo)

                chroma_db.guardar_documento(contenido, nombre_documento, archivo)

            except Exception as e:
                print(f"Error al procesar el archivo: {e}")
        else:
            print(f"El archivo no se encuentra en la ruta: {archivo}")

def mostrar_documentos():
    """Función para mostrar los documentos almacenados en ChromaDB"""
    documentos, metadatos = chroma_db.obtener_documentos()  # Llamada a la clase Chroma

    # Verificar si se obtuvieron documentos
    if not documentos:
        print("No se encontraron documentos en la base de datos.")
        return [], []

    nombres_documentos = [metadata.get('nombre', 'Sin nombre') for metadata in metadatos]
    return documentos, nombres_documentos


def ver_informacion(nombre_documento, contenido):
    """Función para ver la información del documento en una ventana nueva"""
    ventana_info = Toplevel()
    ventana_info.title(nombre_documento)

    pantalla_ancho = ventana_info.winfo_screenwidth()
    pantalla_alto = ventana_info.winfo_screenheight()

    ancho_ventana_info = 600
    alto_ventana_info = 400

    x = (pantalla_ancho // 2) - (ancho_ventana_info // 2)
    y = (pantalla_alto // 2) - (alto_ventana_info // 2)

    ventana_info.geometry(f"{ancho_ventana_info}x{alto_ventana_info}+{x}+{y}")

    text_box = Text(ventana_info, wrap="word", height=20, width=60)
    text_box.insert("1.0", contenido)
    text_box.config(state="disabled")
    text_box.pack(padx=10, pady=10)

    scrollbar = Scrollbar(ventana_info, command=text_box.yview)
    scrollbar.pack(side="right", fill="y")
    text_box.config(yscrollcommand=scrollbar.set)

def ver_informacion_completa():
    """Función para mostrar toda la información de los documentos almacenados"""
    documentos, metadatos = chroma_db.obtener_documentos()
    
    # Mostrar en consola
    print("=== Información completa desde ChromaDB ===")
    for i, doc in enumerate(documentos):
        nombre = metadatos[i].get('nombre', 'Sin nombre')
        print(f"\nDocumento {i+1}: {nombre}")
        print(f"Contenido (primeros 500 caracteres):\n{doc[:500]}")
    print("===========================================")

    # Crear una ventana nueva para mostrar los documentos
    ventana_info_completa = Toplevel()
    ventana_info_completa.title("Información Completa de Documentos")

    pantalla_ancho = ventana_info_completa.winfo_screenwidth()
    pantalla_alto = ventana_info_completa.winfo_screenheight()

    ancho_ventana_info = 600
    alto_ventana_info = 400

    x = (pantalla_ancho // 2) - (ancho_ventana_info // 2)
    y = (pantalla_alto // 2) - (alto_ventana_info // 2)

    ventana_info_completa.geometry(f"{ancho_ventana_info}x{alto_ventana_info}+{x}+{y}")

    text_box = Text(ventana_info_completa, wrap="word", height=20, width=60)
    text_box.config(state="normal")
    
    if documentos:
        for i, doc in enumerate(documentos):
            nombre = metadatos[i].get('nombre', 'Sin nombre')
            contenido = doc[:500]
            text_box.insert("end", f"Documento {i+1}: {nombre}\n{contenido}\n\n")
    else:
        text_box.insert("end", "No hay documentos almacenados.")
    
    text_box.config(state="disabled")
    text_box.pack(padx=10, pady=10)

    scrollbar = Scrollbar(ventana_info_completa, command=text_box.yview)
    scrollbar.pack(side="right", fill="y")
    text_box.config(yscrollcommand=scrollbar.set)


def mostrar_ventana():
    """Configuración de la ventana principal con Tkinter"""
    root = Tk()
    root.title("Gestión de Documentos")
    ancho_ventana = 800
    alto_ventana = 600

    pantalla_ancho = root.winfo_screenwidth()
    pantalla_alto = root.winfo_screenheight()

    x = (pantalla_ancho // 2) - (ancho_ventana // 2)
    y = (pantalla_alto // 2) - (alto_ventana // 2)

    root.geometry(f"{ancho_ventana}x{alto_ventana}+{x}+{y}")

    label_titulo = Label(root, text="Gestión de Documentos", font=("Helvetica", 16))
    label_titulo.pack(pady=10)

    boton_abrir = Button(root, text="Abrir Documento", command=elegir_archivo)
    boton_abrir.pack(pady=10)

    def ver_documentos():
        documentos, nombres_documentos = mostrar_documentos()

        for widget in root.winfo_children():
            if isinstance(widget, Frame):
                widget.destroy()
            elif isinstance(widget, Label) and widget.cget("text") == "No hay documentos guardados.":
                widget.destroy()

        if nombres_documentos:
            for i, doc in enumerate(nombres_documentos):
                frame = Frame(root)
                frame.pack(pady=5)

                label_doc = Label(frame, text=doc, font=("Helvetica", 12))
                label_doc.pack(side="left", padx=10)

                boton_info = Button(frame, text="Ver Información", command=lambda i=i: ver_informacion(nombres_documentos[i], documentos[i]))
                boton_info.pack(side="left", padx=10)
        else:
            mensaje = Label(root, text="No hay documentos guardados.", font=("Helvetica", 12))
            mensaje.pack(pady=10)

    boton_ver = Button(root, text="Ver Documentos", command=ver_documentos)
    boton_ver.pack(pady=10)

    boton_ver_todos = Button(root, text="Ver Información Completa", command=ver_informacion_completa)
    boton_ver_todos.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    mostrar_ventana()
