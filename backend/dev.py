#!/usr/bin/env python
"""
Script de desarrollo para ejecutar todos los microservicios del proyecto SaaS.
Este script inicia cada servicio en su propio proceso, utilizando sus respectivos entornos virtuales.
"""

import os
import sys
import subprocess
import time
import signal
import platform
import argparse
from pathlib import Path

# Configuración de rutas base
BASE_DIR = Path(__file__).parent
SERVICES = {
    "auth-service": {
        "path": BASE_DIR / "auth-service",
        "port": 8001,
        "command": "uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload"
    },
    "gateway-service": {
        "path": BASE_DIR / "gateway-service",
        "port": 8000,
        "command": "uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
    },
    "dentist-service": {
        "path": BASE_DIR / "dentist-service",
        "port": 8002,
        "command": "uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload"
    }
}

# Almacenar procesos para poder terminarlos después
processes = {}

def is_windows():
    """Verifica si el sistema operativo es Windows."""
    return platform.system().lower() == "windows"

def get_venv_activate_command(service_path):
    """Obtiene el comando para activar el entorno virtual según el sistema operativo."""
    if is_windows():
        return str(service_path / ".venv" / "Scripts" / "activate.bat")
    return f"source {service_path}/.venv/bin/activate"

def get_run_command(service_name):
    """Construye el comando completo para ejecutar un servicio con su entorno virtual."""
    service = SERVICES[service_name]
    service_path = service["path"]
    
    if is_windows():
        # En Windows, usamos un comando compuesto con cmd /c
        return f'cmd /c "{get_venv_activate_command(service_path)} && {service["command"]}"'
    else:
        # En Unix, usamos bash -c
        return f'bash -c "{get_venv_activate_command(service_path)} && {service["command"]}"'

def start_service(service_name):
    """Inicia un servicio específico en un proceso separado."""
    if service_name not in SERVICES:
        print(f"Error: El servicio '{service_name}' no está configurado.")
        return False
    
    service = SERVICES[service_name]
    service_path = service["path"]
    
    # Verificar si el servicio existe y tiene un entorno virtual
    if not service_path.exists():
        print(f"Error: El directorio del servicio '{service_name}' no existe en {service_path}")
        return False
    
    if not (service_path / ".venv").exists():
        print(f"Error: El entorno virtual para '{service_name}' no existe en {service_path / '.venv'}")
        return False
    
    # Verificar si el servicio ya está en ejecución
    if service_name in processes and processes[service_name].poll() is None:
        print(f"El servicio '{service_name}' ya está en ejecución.")
        return True
    
    # Construir y ejecutar el comando
    cmd = get_run_command(service_name)
    print(f"Iniciando {service_name} en puerto {service['port']}...")
    
    try:
        # Usar shell=True para que funcione la activación del entorno virtual
        process = subprocess.Popen(
            cmd,
            shell=True,
            cwd=str(service_path),
            # Redirigir salida estándar y error al proceso actual
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Guardar referencia al proceso
        processes[service_name] = process
        
        # Esperar un momento para verificar que el proceso inició correctamente
        time.sleep(2)
        if process.poll() is not None:
            # El proceso terminó prematuramente
            stdout, stderr = process.communicate()
            print(f"Error al iniciar {service_name}:")
            print(stderr)
            return False
        
        print(f"{service_name} iniciado correctamente (PID: {process.pid})")
        
        # Iniciar hilos para mostrar la salida del proceso en tiempo real
        def print_output(stream, prefix):
            for line in stream:
                print(f"[{prefix}] {line.strip()}")
        
        import threading
        threading.Thread(target=print_output, args=(process.stdout, service_name), daemon=True).start()
        threading.Thread(target=print_output, args=(process.stderr, f"{service_name} ERROR"), daemon=True).start()
        
        return True
    
    except Exception as e:
        print(f"Error al iniciar {service_name}: {str(e)}")
        return False

def stop_service(service_name):
    """Detiene un servicio específico."""
    if service_name not in processes:
        print(f"El servicio '{service_name}' no está en ejecución.")
        return
    
    process = processes[service_name]
    if process.poll() is None:  # El proceso sigue en ejecución
        print(f"Deteniendo {service_name}...")
        
        if is_windows():
            # En Windows, usamos taskkill para matar el proceso y sus hijos
            subprocess.run(f"taskkill /F /T /PID {process.pid}", shell=True)
        else:
            # En Unix, enviamos señal SIGTERM
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        
        # Esperar a que termine
        try:
            process.wait(timeout=5)
            print(f"{service_name} detenido correctamente.")
        except subprocess.TimeoutExpired:
            print(f"No se pudo detener {service_name} correctamente. Forzando terminación...")
            if is_windows():
                subprocess.run(f"taskkill /F /T /PID {process.pid}", shell=True)
            else:
                os.killpg(os.getpgid(process.pid), signal.SIGKILL)
    
    # Eliminar del diccionario de procesos
    del processes[service_name]

def stop_all_services():
    """Detiene todos los servicios en ejecución."""
    for service_name in list(processes.keys()):
        stop_service(service_name)

def main():
    """Función principal que procesa los argumentos y ejecuta los comandos."""
    parser = argparse.ArgumentParser(description="Script de desarrollo para microservicios SaaS")
    parser.add_argument("--start", nargs="*", help="Iniciar servicios específicos o todos si no se especifica ninguno")
    parser.add_argument("--stop", nargs="*", help="Detener servicios específicos o todos si no se especifica ninguno")
    parser.add_argument("--list", action="store_true", help="Listar servicios disponibles")
    
    args = parser.parse_args()
    
    if args.list:
        print("Servicios disponibles:")
        for name, service in SERVICES.items():
            print(f"  - {name} (puerto: {service['port']})")
        return
    
    if args.stop is not None:
        if not args.stop:  # Lista vacía, detener todos
            stop_all_services()
        else:
            for service_name in args.stop:
                if service_name in SERVICES:
                    stop_service(service_name)
                else:
                    print(f"Servicio desconocido: {service_name}")
    
    if args.start is not None:
        if not args.start:  # Lista vacía, iniciar todos
            for service_name in SERVICES:
                start_service(service_name)
        else:
            for service_name in args.start:
                if service_name in SERVICES:
                    start_service(service_name)
                else:
                    print(f"Servicio desconocido: {service_name}")
    
    # Si no se especificó ninguna acción, mostrar ayuda
    if not (args.list or args.start is not None or args.stop is not None):
        parser.print_help()
        return
    
    # Si hay procesos en ejecución, mantener el script activo
    if processes:
        try:
            print("\nPresiona Ctrl+C para detener todos los servicios...\n")
            # Mantener el script en ejecución mientras haya procesos activos
            while any(p.poll() is None for p in processes.values()):
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nDeteniendo todos los servicios...")
            stop_all_services()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nDeteniendo todos los servicios...")
        stop_all_services()
