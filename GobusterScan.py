import subprocess
import os
import sys
import threading
import queue
import time
from pathlib import Path
import pyfiglet
from colorama import init, Fore, Style
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn

# Inicialización
console = Console()
init()

def mostrar_banner():
    banner = pyfiglet.figlet_format("Gobuster Scanner", font="slant")
    print(Fore.RED + banner + Style.RESET_ALL)
    print(f"{Fore.CYAN}╔════════════════════════════════════════╗{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║                                       ║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║       G O B U S T E R S C A N         ║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║                                       ║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║                             by:mxr    ║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}╚════════════════════════════════════════╝{Style.RESET_ALL}")

def crear_directorio_resultados():
    carpeta_predeterminada = os.path.expanduser("~/resultados_gobuster")
    print(f"\nLos resultados se guardarán en: {carpeta_predeterminada}")
    
    if not os.path.exists(carpeta_predeterminada):
        os.makedirs(carpeta_predeterminada)
        
    return carpeta_predeterminada

def obtener_carpeta_personalizada(carpeta_predeterminada):
    guardar = input("¿Quieres guardar los resultados en esta carpeta? (S/n): ").strip().lower()
    if guardar == "n":
        carpeta_personalizada = input("Ingresa la carpeta donde deseas guardar los resultados: ")
        return carpeta_personalizada if carpeta_personalizada else carpeta_predeterminada
    return carpeta_predeterminada

class GobusterMonitor:
    def __init__(self):
        self.queue = queue.Queue()
        self.task_id = None
        
    def monitor_output(self, process):
        for line in iter(process.stdout.readline, ''):
            if line:
                self.queue.put(line.strip())
    
    def update_progress(self, progress, task_id):
        while True:
            try:
                line = self.queue.get_nowait()
                if "Found" in line:
                    progress.update(task_id, description=f"Encontrado: {line}")
                else:
                    progress.console.print(f"[yellow]Proceso:[/] {line}")
                self.queue.task_done()
            except queue.Empty:
                break

def ejecutar_gobuster():
    while True:
        mostrar_banner()
        print("\nElige el tipo de escaneo con Gobuster:")
        print("1. Escaneo de directorios")
        print("2. Escaneo de subdominios")
        print("3. Escaneo de archivos")
        print("4. Escaneo con autenticación")
        print("5. Escaneo con proxy y cabeceras personalizadas")
        print("6. Escaneo en modo silencioso")
        print("7. Escaneo personalizado")
        print("8. Salir")
        
        opcion = input("\nSelecciona una opción: ")
        
        if opcion == "8":
            print("\n¡Hasta luego!")
            break
        
        url = input("Ingresa la URL o dominio a escanear: ")
        diccionario = input("Ingresa la ruta del diccionario de palabras: ")
        
        comando = ["gobuster"]
        
        if opcion == "1":
            comando += ["dir", "-u", url, "--wordlist", diccionario]
        elif opcion == "2":
            comando += ["dns", "-d", url, "--wordlist", diccionario]
        elif opcion == "3":
            extensiones = input("Ingresa las extensiones a buscar (ej: php,txt,html): ")
            comando += ["dir", "-u", url, "--wordlist", diccionario, "-x", extensiones]
        elif opcion == "4":
            usuario = input("Usuario: ")
            contrasena = input("Contraseña: ")
            comando += ["dir", "-u", url, "--wordlist", diccionario, "--auth", f"{usuario}:{contrasena}"]
        elif opcion == "5":
            proxy = input("Ingresa el proxy (ej: http://127.0.0.1:8080): ")
            cabecera = input("Ingresa las cabeceras personalizadas: ")
            comando += ["dir", "-u", url, "--wordlist", diccionario, "--proxy", proxy, "-H", cabecera]
        elif opcion == "6":
            comando += ["dir", "-u", url, "--wordlist", diccionario, "-q"]
        elif opcion == "7":
            comando = input("Ingresa el comando completo de Gobuster: ").split()
        
        carpeta_salida = crear_directorio_resultados()
        carpeta_salida = obtener_carpeta_personalizada(carpeta_salida)
        
        archivo_salida = os.path.join(carpeta_salida, "gobuster_resultado.txt")
        comando += ["-o", archivo_salida]
        
        print("\nComando a ejecutar:", " ".join(comando))
        
        monitor = GobusterMonitor()
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}", justify="right"),
                BarColumn(bar_width=None),
                TaskProgressColumn(),
                TimeRemainingColumn(),
            ) as progress:
                monitor.task_id = progress.add_task("Inicializando...", total=100)
                
                process = subprocess.Popen(
                    comando,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1
                )
                
                monitor_thread = threading.Thread(target=monitor.monitor_output, args=(process,))
                monitor_thread.daemon = True
                monitor_thread.start()
                
                while process.poll() is None:
                    monitor.update_progress(progress, monitor.task_id)
                    time.sleep(0.1)
                
                if process.returncode == 0:
                    progress.console.print("\n[green]¡Escaneo completado![/]")
                    progress.console.print(f"[blue]Resultados guardados en:[/] {archivo_salida}")
                    
                    if os.path.exists(archivo_salida):
                        with open(archivo_salida, 'r') as f:
                            progress.console.print("\n[yellow]Resultados del escaneo:[/]")
                            progress.console.print("-" * 50)
                            progress.console.print(f.read())
                            progress.console.print("-" * 50)
                    else:
                        progress.console.print("[red]Error: No se pudo crear el archivo de salida[/]")
                
                input("\nPresiona Enter para continuar...")
        except KeyboardInterrupt:
            console.print("\n[cyan]¡Escaneo interrumpido por el usuario![/]")
        except Exception as e:
            console.print(f"\n[red]¡Error inesperado!: {str(e)}[/]")

if __name__ == "__main__":
    try:
        ejecutar_gobuster()
    except KeyboardInterrupt:
        console.print("\n[cyan]¡Programa terminado por el usuario![/]")
        sys.exit(0)
