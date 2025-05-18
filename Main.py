from Modules.GUI import GUI
from Modules.app import app
import threading

def iniciar_flask():
    app.run(debug=True, port=5000, use_reloader=False)

if __name__ == "__main__":

    flask_thread = threading.Thread(target=iniciar_flask)
    flask_thread.daemon = True  
    flask_thread.start()

    interfaz = GUI()
    interfaz.mostrar_ventana()
