import tkinter as tk
from tkinter import ttk
import sounddevice as sd
import pyttsx3
import soundfile as sf
from translate import Translator
import threading
import time
from PIL import Image, ImageTk

# Inicializar el motor de texto a voz
engine = pyttsx3.init()

# Obtener lista de dispositivos de audio disponibles
dispositivos_disponibles = sd.query_devices()

# Filtrar solo los dispositivos de salida
dispositivos_salida = [info['name'] for info in dispositivos_disponibles if info['max_output_channels'] > 0]

# Variables globales para almacenar el nombre del dispositivo seleccionado y la voz seleccionada
dispositivo_seleccionado = None
voz_seleccionada = None
idioma_origen = "en"
idioma_destino = "es"
ultimo_tiempo_actualizacion = time.time()  # Variable global para almacenar el tiempo de la última actualización

# Variable global para mantener el estado de la reproducción de audio
reproduccion_en_curso = False

# Función para generar el audio
def generar_audio():
    global reproduccion_en_curso
    if voz_seleccionada is None:
        texto_bloque.config(state="normal")
        texto_bloque.delete(1.0, "end")
        texto_bloque.insert("end", "Por favor, selecciona una voz antes de generar el audio.")
        texto_bloque.config(state="disabled")
    else:
        texto = texto_bloque.get(1.0, "end-1c")  # Obtener texto traducido del cuadro de mensaje
        engine.setProperty('voice', voz_seleccionada.id)
        engine.save_to_file(texto, 'temp.wav')  # Guardar el audio generado en un archivo temporal
        engine.runAndWait()
        reproduccion_en_curso = True
        threading.Thread(target=reproducir_audio).start()

# Función para reproducir el audio
def reproducir_audio():
    global reproduccion_en_curso
    texto = texto_bloque.get(1.0, "end-1c")  # Obtener texto traducido del cuadro de mensaje
    audio_array, fs = sf.read('temp.wav', dtype='int16')
    sd.play(audio_array, fs)
    sd.wait()
    reproduccion_en_curso = False

# Función para pausar la reproducción de audio
def pausar_reproduccion():
    sd.stop()

# Función para transmitir el audio
def transmitir_audio():
    global reproduccion_en_curso
    if not reproduccion_en_curso:
        texto = texto_bloque.get(1.0, "end-1c")  # Obtener texto traducido del cuadro de mensaje
        engine.save_to_file(texto, 'temp.wav')  # Guardar el audio generado en un archivo temporal
        engine.runAndWait()
        threading.Thread(target=transmitir_audio_thread).start()

# Función para transmitir el audio en un hilo separado
def transmitir_audio_thread():
    texto = texto_bloque.get(1.0, "end-1c")  # Obtener texto traducido del cuadro de mensaje
    audio_array, fs = sf.read('temp.wav', dtype='int16')
    if dispositivo_seleccionado is not None:
        for info in dispositivos_disponibles:
            if info['name'] == dispositivo_seleccionado:
                device_id = info['name']
                break
        else:
            print("Dispositivo de salida no encontrado:", dispositivo_seleccionado)
            return
        sd.play(audio_array, fs, device=device_id)
        sd.wait()

# Función para pausar la transmisión de audio
def pausar_transmision():
    sd.stop()

# Función para traducir y actualizar el texto
def traducir_y_actualizar():
    global idioma_origen, idioma_destino, ultimo_tiempo_actualizacion
    if time.time() - ultimo_tiempo_actualizacion > 0.01:  # Actualizar solo si ha pasado medio segundo desde la última actualización
        ultimo_tiempo_actualizacion = time.time()
        idioma_origen = combo_idioma_origen.get().lower()
        idioma_destino = combo_idioma_destino.get().lower()
        texto = entrada_texto.get()  # Obtener texto del cuadro de entrada
        translator = Translator(from_lang=idioma_origen, to_lang=idioma_destino)
        translation = translator.translate(texto)
        texto_bloque.config(state="normal")
        texto_bloque.delete(1.0, "end")
        texto_bloque.insert("end", translation)
        texto_bloque.config(state="disabled")
        print("Idioma de entrada:", idioma_origen)
        print("Idioma de salida:", idioma_destino)
        print("Texto traducido:", translation)

# Función para actualizar la traducción
def actualizar_traduccion(event=None):
    threading.Thread(target=traducir_y_actualizar).start()

# Función para seleccionar el dispositivo de salida
def seleccionar_dispositivo(event=None):
    global dispositivo_seleccionado
    dispositivo_seleccionado = combo_dispositivos.get()  # Obtener el nombre del dispositivo seleccionado desde el Combobox
    print("Dispositivo de salida seleccionado:", dispositivo_seleccionado)

# Función para seleccionar la voz
def seleccionar_voz(event=None):
    global voz_seleccionada
    nombre_voz_seleccionada = combo_voz.get()
    for voz in voces_disponibles:
        if voz.name == nombre_voz_seleccionada:
            voz_seleccionada = voz
            break
    print("Voz seleccionada:", voz_seleccionada)

# Hilo para traducir y actualizar cada tres segundos
def hilo_traducir_cada_tres_segundos():
    while True:
        traducir_y_actualizar()
        time.sleep(3)

# Iniciar el hilo que llama a traducir_y_actualizar() cada tres segundos
threading.Thread(target=hilo_traducir_cada_tres_segundos).start()

# Configuración de la interfaz gráfica
root = tk.Tk()
root.title("TalkALTive")

# Cambiar ícono de la ventana
icono = ImageTk.PhotoImage(Image.open("logo.png"))  # Reemplaza "custom_icon.png" con la ruta de tu archivo de ícono
root.iconphoto(False, icono)

# Personalización de estilos
style = ttk.Style(root)

frame = ttk.Frame(root)
frame.grid(row=0, column=0, padx=10, pady=10)

texto_bloque = tk.Text(frame, height=6, width=50, state="disabled")
texto_bloque.grid(row=0, column=1, padx=5, pady=5)

etiqueta_texto = ttk.Label(frame, text="Mensaje:")
etiqueta_texto.grid(row=1, column=0, sticky="w")

entrada_texto = ttk.Entry(frame,  width=50,  font=('Helvetica', 14))
entrada_texto.grid(row=1, column=1, padx=5, pady=5)
entrada_texto.bind("<KeyRelease>", actualizar_traduccion)  # Actualizar traducción al escribir

boton_generar_audio = ttk.Button(frame, text="Reproducir Audio", command=generar_audio)
boton_generar_audio.grid(row=1, column=2, padx=5, pady=5)

boton_transmitir_audio = ttk.Button(frame, text="Transmitir Audio", command=transmitir_audio)
boton_transmitir_audio.grid(row=2, column=2, padx=5, pady=5)

boton_pausar_reproduccion = ttk.Button(frame, text="Pausar Reproducción", command=pausar_reproduccion)
boton_pausar_reproduccion.grid(row=1, column=3, padx=5, pady=5)

boton_pausar_transmision = ttk.Button(frame, text="Pausar Transmisión", command=pausar_transmision)
boton_pausar_transmision.grid(row=2, column=3, padx=5, pady=5)

etiqueta_dispositivos = ttk.Label(frame, text="Seleccionar Dispositivo de Salida:")
etiqueta_dispositivos.grid(row=2, column=0, sticky="w")

combo_dispositivos = ttk.Combobox(frame, values=dispositivos_salida, state="readonly", width=48)
combo_dispositivos.grid(row=2, column=1, padx=5, pady=5)
# Configurar valor inicial del Combobox como None
combo_dispositivos.set('')
combo_dispositivos.bind("<<ComboboxSelected>>", seleccionar_dispositivo)

etiqueta_voz = ttk.Label(frame, text="Seleccionar Voz:")
etiqueta_voz.grid(row=3, column=0, sticky="w")

# Obtener lista de voces disponibles
voces_disponibles = engine.getProperty('voices')
voces_nombres = [voz.name for voz in voces_disponibles]

combo_voz = ttk.Combobox(frame, values=voces_nombres, state="readonly", width=48)
combo_voz.grid(row=3, column=1, padx=5, pady=5)
# Configurar valor inicial del Combobox como None
combo_voz.set('')
combo_voz.bind("<<ComboboxSelected>>", seleccionar_voz)

etiqueta_idioma_origen = ttk.Label(frame, text="Idioma de Origen:")
etiqueta_idioma_origen.grid(row=4, column=0, sticky="w")

combo_idioma_origen = ttk.Combobox(frame, values=["es", "en", "fr", "it", "pt", "de", "ru"], state="readonly", width=10)
combo_idioma_origen.grid(row=4, column=1, padx=5, pady=5)

etiqueta_idioma_destino = ttk.Label(frame, text="Idioma de Destino:")
etiqueta_idioma_destino.grid(row=5, column=0, sticky="w")

combo_idioma_destino = ttk.Combobox(frame, values=["es", "en", "fr", "it", "pt", "de", "ru"], state="readonly", width=10)
combo_idioma_destino.grid(row=5, column=1, padx=5, pady=5)

traducir_y_actualizar()  # Llamar a la función por primera vez
root.mainloop()
