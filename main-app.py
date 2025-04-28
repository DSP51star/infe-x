import os
import json
import random
import time
import socket
import speedtest
import subprocess
import platform
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import requests
import importlib.util
import sys

# --- Funciones de los comandos ---

def help_command():
    print("""
Comandos disponibles:
  - help                          -> Muestra los comandos
  - set_game                      -> Descarga e imprime un archivo
  - path                          -> Muestra tu IP, tu red WiFi y velocidad de internet
  - set instalation -w from infex -> Instalación ficticia con ventana
  - cls                           -> Limpia la consola (reinicia la terminal)
  - descargar_plugin              -> Descarga y ejecuta un plugin desde la web
""")

def set_game_command():
    url = "https://raw.githubusercontent.com/DSP51star/infe-x/main/complements/comp1.txt"
    print("Descargando archivo...")
    response = requests.get(url)
    if response.status_code == 200:
        content = response.text
        print("\nContenido del archivo descargado:\n")
        print(content)
    else:
        print("Error al descargar el archivo.")

# --- Funciones para obtener la IP y la red WiFi ---
def obtener_wifi():
    sistema = platform.system()
    try:
        if sistema == "Windows":
            resultado = subprocess.check_output(["netsh", "wlan", "show", "interfaces"], text=True)
            for linea in resultado.split("\n"):
                if "SSID" in linea and "BSSID" not in linea:
                    return linea.split(":")[1].strip()
            return "No se pudo obtener el nombre del WiFi"
        
        elif sistema == "Linux":
            resultado = subprocess.check_output(["iwgetid", "-r"], text=True)
            return resultado.strip()
        
        elif sistema == "Darwin":  # macOS
            resultado = subprocess.check_output(
                ["/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport", "-I"],
                text=True
            )
            for linea in resultado.split("\n"):
                if " SSID:" in linea:
                    return linea.split(":")[1].strip()
            return "No se pudo obtener el nombre del WiFi"
        
        else:
            return "Sistema no compatible"
    
    except Exception as e:
        return f"Error al obtener el nombre del WiFi: {e}"

# --- Mostrar barra de progreso ---
def mostrar_barra_progreso(nombre, velocidad, total_mb, color_code):
    barra_largo = 40  # Largo total de la barra
    mb_descargado = 0
    start_time = time.time()
    
    while mb_descargado < total_mb:
        time.sleep(0.05)  # Simular transferencia de datos
        
        mb_descargado += velocidad * 0.05
        mb_descargado = min(mb_descargado, total_mb)

        porcentaje = mb_descargado / total_mb
        barra_completa = int(barra_largo * porcentaje)
        
        barra = "━" * barra_completa + " " * (barra_largo - barra_completa)
        eta = max(0, (total_mb - mb_descargado) / velocidad)

        sys.stdout.write(
            f"\r{color_code}{barra} {mb_descargado:.1f}/{total_mb} MB {velocidad:.1f} MB/s eta 0:00:{int(eta):02d}\033[0m"
        )
        sys.stdout.flush()

    print()  # Nueva línea al terminar

# --- Función principal del comando path ---
def path_command():
    try:
        ip = socket.gethostbyname(socket.gethostname())
        print(f"\nTu IP: {ip}")

        ssid = obtener_wifi()
        print(f"Conectado a la red WiFi: {ssid}")

        print("\nMidiendo velocidad de internet...")
        print("Esto puede tardar unos segundos, por favor espere...")

        try:
            st = speedtest.Speedtest()
            download_speed = st.download() / 1_000_000  # en Mbps
            upload_speed = st.upload() / 1_000_000       # en Mbps
            print("\nResultados de la prueba:")

        except Exception as e:
            print(f"\n[!] No se pudo medir la velocidad real ({e})")
            print("[!] Mostrando velocidades simuladas...\n")
            download_speed = random.uniform(50, 100)  # Simulación de descarga
            upload_speed = random.uniform(10, 20)     # Simulación de subida

        # Mostrar las barras:
        print("\nVelocidad de descarga:")
        mostrar_barra_progreso("Descarga", download_speed, 100, "\033[92m")  # Verde

        print("\nVelocidad de subida:")
        mostrar_barra_progreso("Subida", upload_speed, 100, "\033[91m")      # Rojo

        print(f"\nVelocidad de descarga: {download_speed:.2f} Mbps")
        print(f"Velocidad de subida: {upload_speed:.2f} Mbps")

    except Exception as e:
        print(f"Error obteniendo datos de red: {e}")

# --- Función para guardar datos ---
def guardar_datos(ID, ONID):
    data = {"ID": ID, "ONID": ONID}
    
    script_dir = os.path.dirname(os.path.realpath(__file__))
    folder_path = os.path.join(script_dir, "data")
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    ruta_archivo = os.path.join(folder_path, "datos.json")
    
    try:
        with open(ruta_archivo, "w") as file:
            json.dump(data, file, indent=4)
        print(f"Datos guardados en '{ruta_archivo}'.")
    except Exception as e:
        print(f"Error guardando datos: {e}")

# --- Funciones de la ventana de instalación ---
def set_installation_command():
    global root, label, barra, entry_id, entry_onid

    print("Instalando en 'Descargas'...")
    time.sleep(1)
    
    root = tk.Tk()
    root.title("Instalador de Infex")

    label = tk.Label(root, text="Opciones de instalación")
    label.pack(pady=10)

    tk.Label(root, text="Introduce tu ID:").pack()
    entry_id = tk.Entry(root)
    entry_id.pack(pady=5)

    tk.Label(root, text="Introduce tu ONID:").pack()
    entry_onid = tk.Entry(root)
    entry_onid.pack(pady=5)

    barra = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
    
    def accion_confirmar():
        ID = entry_id.get()
        ONID = entry_onid.get()
        if ID and ONID:
            barra.pack(pady=10)
            threading.Thread(target=lambda: progreso_final(ID, ONID)).start()
        else:
            messagebox.showwarning("Campos vacíos", "Por favor, completa ID y ONID.")

    boton_confirmar = tk.Button(root, text="Confirmar e Inyectar", command=accion_confirmar)
    boton_confirmar.pack(pady=10)

    root.mainloop()

def progreso_final(ID, ONID):
    for i in range(101):
        barra["value"] = i
        root.update_idletasks()
        time.sleep(0.05)
    contador_10s(ID, ONID)

def contador_10s(ID, ONID):
    for i in range(10, 0, -1):
        label.config(text=f"Finalizando en {i} segundos...")
        root.update_idletasks()
        time.sleep(1)
    root.after(0, root.destroy)
    letras_y_numeros(ID, ONID)

def letras_y_numeros(ID, ONID):
    print("\n--- Proceso finalizado ---\n")
    end_time = time.time() + 5
    while time.time() < end_time:
        print(''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for _ in range(20)))
        time.sleep(0.2)
    guardar_datos(ID, ONID)

# --- Funciones de plugins ---
comandos_plugins = {}

def descargar_y_listar_plugins():
    url = "https://raw.githubusercontent.com/DSP51star/infe-x/main/complements/comp2.py"
    print("Descargando el plugin...")

    if not os.path.exists("plugins"):
        os.makedirs("plugins")

    ruta_plugin = os.path.join("plugins", "comp2.py")
    
    try:
        response = requests.get(url)
        response.raise_for_status()

        with open(ruta_plugin, "w") as f:
            f.write(response.text)
        print("Archivo descargado correctamente en la carpeta 'plugins'.")

        print("\n--- Listando comandos disponibles de los plugins ---")
        cargar_comandos_plugins()

    except requests.exceptions.RequestException as e:
        print(f"Error al descargar el archivo: {e}")
    except Exception as e:
        print(f"Error al manejar el plugin: {e}")

def cargar_comandos_plugins():
    global comandos_plugins
    plugin_dir = "plugins"
    
    for archivo in os.listdir(plugin_dir):
        if archivo.endswith(".py"):
            ruta_plugin = os.path.join(plugin_dir, archivo)
            try:
                spec = importlib.util.spec_from_file_location(archivo[:-3], ruta_plugin)
                plugin = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(plugin)

                comandos_plugins[archivo] = {}
                for atributo in dir(plugin):
                    if not atributo.startswith("_"):
                        comandos_plugins[archivo][atributo] = getattr(plugin, atributo)

                print(f"\nComandos del plugin '{archivo}':")
                for comando in comandos_plugins[archivo]:
                    print(f"  - {comando}")

            except Exception as e:
                print(f"Error al cargar el plugin {archivo}: {e}")

def ejecutar_comando_plugin(plugin, comando):
    if plugin in comandos_plugins and comando in comandos_plugins[plugin]:
        comandos_plugins[plugin][comando]()
    else:
        print("Comando o plugin no encontrado.")

# --- Función para limpiar la consola ---
def clear_console_command():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("Consola limpia.")

# --- Función principal de la consola ---
def main():
    print("Bienvenido a la consola Infex. Escribe 'help' para ver los comandos disponibles.")
    while True:
        comando = input("\n> ").strip().lower()
        if comando == "help":
            help_command()
        elif comando == "set_game":
            set_game_command()
        elif comando == "path":
            path_command()
        elif comando == "set instalation -w from infex":
            set_installation_command()
        elif comando == "descargar_plugin":
            descargar_y_listar_plugins()
        elif comando.startswith("plugin"):
            try:
                _, plugin, funcion = comando.split()
                ejecutar_comando_plugin(plugin + ".py", funcion)
            except ValueError:
                print("Formato incorrecto. Usa: plugin nombre_plugin nombre_funcion")
        elif comando == "cls":
            clear_console_command()
        else:
            print("Comando no reconocido. Escribe 'help' para ver los comandos.")

if __name__ == "__main__":
    main()
