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

# Variable global para almacenar el nombre del dispositivo seleccionado
dispositivo_seleccionado = None


def generar_audio():
    texto = entrada_texto.get()
    # Generar audio a partir del texto
    engine.say(texto)
    engine.runAndWait()


def seleccionar_dispositivo():
    global dispositivo_seleccionado
    dispositivo_seleccionado = combo_dispositivos.get()  # Obtener el nombre del dispositivo seleccionado desde el Combobox
    print("Dispositivo de salida seleccionado:", dispositivo_seleccionado)


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

etiqueta_texto = ttk.Label(frame, text="Texto:")
etiqueta_texto.grid(row=0, column=0, sticky="w")

entrada_texto = ttk.Entry(frame, width=40)
entrada_texto.grid(row=0, column=1, padx=5, pady=5)

boton_generar_audio = ttk.Button(frame, text="Generar Audio", command=generar_audio)
boton_generar_audio.grid(row=0, column=2, padx=5, pady=5)

etiqueta_dispositivos = ttk.Label(frame, text="Seleccionar Dispositivo de Salida:")
etiqueta_dispositivos.grid(row=1, column=0, sticky="w")

combo_dispositivos = ttk.Combobox(frame, values=dispositivos_salida, state="readonly")
combo_dispositivos.grid(row=1, column=1, padx=5, pady=5)
combo_dispositivos.current(0)  # Seleccionar el primer dispositivo por defecto

boton_seleccionar_dispositivo = ttk.Button(frame, text="Seleccionar", command=seleccionar_dispositivo)
boton_seleccionar_dispositivo.grid(row=1, column=2, padx=5, pady=5)

boton_transmitir_audio = ttk.Button(frame, text="Transmitir Audio", command=transmitir_audio)
boton_transmitir_audio.grid(row=2, column=1, padx=5, pady=5)

root.mainloop()
