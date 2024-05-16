import tkinter as tk
from tkinter import ttk
import sounddevice as sd
import pyttsx3
import soundfile as sf

# Inicializar el motor de texto a voz
engine = pyttsx3.init()

# Obtener lista de dispositivos de audio disponibles
dispositivos_disponibles = sd.query_devices()

# Filtrar solo los dispositivos de salida
dispositivos_salida = [info['name'] for info in dispositivos_disponibles if info['max_output_channels'] > 0]

# Variables globales para almacenar el nombre del dispositivo seleccionado y la voz seleccionada
dispositivo_seleccionado = None
voz_seleccionada = None


def generar_audio():
    texto = entrada_texto.get()
    if voz_seleccionada is None:
        texto_bloque.config(state="normal")
        texto_bloque.delete(1.0, "end")
        texto_bloque.insert("end", "Por favor, selecciona una voz antes de generar el audio.")
        texto_bloque.config(state="disabled")
    else:
        # Configurar la voz
        engine.setProperty('voice', voz_seleccionada.id)
        # Generar audio a partir del texto
        engine.say(texto)
        engine.runAndWait()


def actualizar_mensaje(event=None):
    texto = entrada_texto.get()
    texto_bloque.config(state="normal")
    texto_bloque.delete(1.0, "end")
    texto_bloque.insert("end", texto)
    texto_bloque.config(state="disabled")


def seleccionar_dispositivo(event=None):
    global dispositivo_seleccionado
    dispositivo_seleccionado = combo_dispositivos.get()  # Obtener el nombre del dispositivo seleccionado desde el Combobox
    print("Dispositivo de salida seleccionado:", dispositivo_seleccionado)


def seleccionar_voz(event=None):
    global voz_seleccionada
    nombre_voz_seleccionada = combo_voz.get()
    for voz in voces_disponibles:
        if voz.name == nombre_voz_seleccionada:
            voz_seleccionada = voz
            actualizar_mensaje()  # Reflejar el texto escrito en el mensaje
            # Limpiar el mensaje al seleccionar una voz
            texto_bloque.config(state="normal")
            texto_bloque.delete(1.0, "end")
            texto_bloque.insert("end", entrada_texto.get())
            texto_bloque.config(state="disabled")
            break
    print("Voz seleccionada:", voz_seleccionada)


def transmitir_audio():
    # Capturar el audio generado por el texto a voz y transmitirlo al dispositivo seleccionado
    texto = entrada_texto.get()

    # Configurar el motor de texto a voz para que genere un archivo de audio en formato WAV
    engine.save_to_file(texto, 'temp.wav')  # Guardar el audio generado en un archivo temporal

    # Esperar hasta que se haya generado el archivo de audio
    engine.runAndWait()

    # Leer el archivo de audio
    audio_array, fs = sf.read('temp.wav', dtype='int16')

    # Transmitir el audio al dispositivo seleccionado
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


# Configuración de la interfaz gráfica
root = tk.Tk()
root.title("Transmitir Texto a Voz por Dispositivo de Salida")

frame = ttk.Frame(root)
frame.grid(row=0, column=0, padx=10, pady=10)

etiqueta_bloque = ttk.Label(frame, text="Mensaje:")
etiqueta_bloque.grid(row=0, column=0, sticky="w")

texto_bloque = tk.Text(frame, height=3, width=50, state="disabled")
texto_bloque.grid(row=0, column=1, padx=5, pady=5)

etiqueta_texto = ttk.Label(frame, text="Texto:")
etiqueta_texto.grid(row=1, column=0, sticky="w")

entrada_texto = ttk.Entry(frame, width=50)
entrada_texto.grid(row=1, column=1, padx=5, pady=5)
entrada_texto.bind("<KeyRelease>", actualizar_mensaje)

boton_generar_audio = ttk.Button(frame, text="Generar Audio", command=generar_audio)
boton_generar_audio.grid(row=1, column=2, padx=5, pady=5)

boton_transmitir_audio = ttk.Button(frame, text="Transmitir Audio", command=transmitir_audio)
boton_transmitir_audio.grid(row=2, column=2, padx=5, pady=5)

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

root.mainloop()
