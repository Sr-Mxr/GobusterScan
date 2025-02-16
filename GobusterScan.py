import subprocess
import os
from pathlib import Path
import sys
import pyfiglet
from colorama import init, Fore, Style

# Inicializar colorama
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
    """Crea el directorio para guardar los resultados si no existe."""
    carpeta_predeterminada = os.path.expanduser("~/resultados_gobuster")
    print(f"\nLos resultados se guardarán en: {carpeta_predeterminada}")
    
    # Crear directorio si no existe
    if not os.path.exists(carpeta_predeterminada):
        os.makedirs(carpeta_predeterminada)
        
    return carpeta_predeterminada

def obtener_carpeta_personalizada(carpeta_predeterminada):
    """Permite al usuario elegir una carpeta personalizada para guardar resultados."""
    guardar = input("¿Quieres guardar los resultados en esta carpeta? (S/n): ").strip().lower()
    if guardar == "n":
        carpeta_personalizada = input("Ingresa la carpeta donde deseas guardar los resultados: ")
        return carpeta_personalizada if carpeta_personalizada else carpeta_predeterminada
    return carpeta_predeterminada


def ejecutar_gobuster():
    """
    Función principal que ejecuta Gobuster según las opciones seleccionadas por el usuario.
    """
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
        return
    
    url = input("Ingresa la URL o dominio a escanear: ")
    diccionario = input("Ingresa la ruta del diccionario de palabras (ej. /usr/share/wordlists/dirb/common.txt): ")
    
    comando = ["gobuster"]
    
    if opcion == "1":
        comando += ["dir", "-u", url, "-w", diccionario]
    elif opcion == "2":
        comando += ["dns", "-d", url, "-w", diccionario]
    elif opcion == "3":
        extensiones = input("Ingresa las extensiones a buscar (ej: php,txt,html): ")
        comando += ["dir", "-u", url, "-w", diccionario, "-x", extensiones]
    elif opcion == "4":
        usuario = input("Usuario: ")
        contrasena = input("Contraseña: ")
        comando += ["dir", "-u", url, "-w", diccionario, "--auth", f"{usuario}:{contrasena}"]
    elif opcion == "5":
        proxy = input("Ingresa el proxy (ej. http://127.0.0.1:8080): ")
        cabecera = input("Ingresa las cabeceras personalizadas (ej. 'User-Agent: Mozilla/5.0'): ")
        comando += ["dir", "-u", url, "-w", diccionario, "--proxy", proxy, "-H", cabecera]
    elif opcion == "6":
        comando += ["dir", "-u", url, "-w", diccionario, "-q"]
    elif opcion == "7":
        comando = input("Ingresa el comando completo de Gobuster: ").split()
    
    # Manejo de directorios y archivos de salida
    carpeta_salida = crear_directorio_resultados()
    carpeta_salida = obtener_carpeta_personalizada(carpeta_salida)
    
    archivo_salida = os.path.join(carpeta_salida, "gobuster_resultado.txt")
    comando += ["-o", archivo_salida]
    
    print("\nComando a ejecutar:", " ".join(comando))
    
    try:
        print("\nEjecutando Gobuster...")
        resultado = subprocess.run(comando, text=True, capture_output=True)
        
        if resultado.returncode == 0:
            print(f"\nEscaneo finalizado exitosamente.")
            print(f"Los resultados están en: {archivo_salida}")
            
            # Mostrar los resultados si el archivo existe
            if os.path.exists(archivo_salida):
                with open(archivo_salida, 'r') as f:
                    print("\nResultados del escaneo:")
                    print("-" * 50)
                    print(f.read())
                    print("-" * 50)
            else:
                print("¡Advertencia! El archivo de salida no fue creado correctamente.")
                
        else:
            print("\nError al ejecutar Gobuster:", resultado.stderr.strip())
            
    except KeyboardInterrupt:
        print("\n\n¡Escaneo interrumpido por el usuario!")
    except Exception as e:
        print(f"\n¡Error inesperado!: {str(e)}")

if __name__ == "__main__":
    try:
        ejecutar_gobuster()
    except KeyboardInterrupt:
        print("\n\n¡Programa terminado por el usuario!")
        sys.exit(0)
