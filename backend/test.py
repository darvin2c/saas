#!/usr/bin/env python
"""
Script centralizado para ejecutar tests de todos los microservicios del proyecto SaaS.
Este script permite ejecutar tests de servicios específicos o de todos los servicios a la vez.
"""

import os
import sys
import subprocess
import argparse
import platform
from pathlib import Path
import time

# Configuración de rutas base
BASE_DIR = Path(__file__).parent
SERVICES = {
    "auth-service": {
        "path": BASE_DIR / "auth-service",
        "test_command": "python -m pytest tests/ -v"
    },
    "gateway-service": {
        "path": BASE_DIR / "gateway-service",
        "test_command": "python -m pytest tests/ -v"
    },
    "dentist-service": {
        "path": BASE_DIR / "dentist-service",
        "test_command": "python -m pytest tests/ -v"
    }
}

def is_windows():
    """Verifica si el sistema operativo es Windows."""
    return platform.system().lower() == "windows"

def get_venv_activate_command(service_path):
    """Obtiene el comando para activar el entorno virtual según el sistema operativo."""
    if is_windows():
        return str(service_path / ".venv" / "Scripts" / "activate.bat")
    return f"source {service_path}/.venv/bin/activate"

def get_test_command(service_name, test_file=None):
    """Construye el comando completo para ejecutar los tests de un servicio."""
    service = SERVICES[service_name]
    service_path = service["path"]
    test_cmd = service["test_command"]
    
    # Si se especifica un archivo de test específico, agregarlo al comando
    if test_file:
        if not test_file.startswith("tests/"):
            test_file = f"tests/{test_file}"
        test_cmd = test_cmd.replace("tests/", test_file)
    
    # Agregar PYTHONPATH para que los tests puedan importar los módulos del servicio
    pythonpath_cmd = f"set PYTHONPATH={service_path}" if is_windows() else f"export PYTHONPATH={service_path}"
    
    if is_windows():
        # En Windows, usamos un comando compuesto con cmd /c
        return f'cmd /c "{get_venv_activate_command(service_path)} && {pythonpath_cmd} && {test_cmd}"'
    else:
        # En Unix, usamos bash -c
        return f'bash -c "{get_venv_activate_command(service_path)} && {pythonpath_cmd} && {test_cmd}"'

def run_tests_for_service(service_name, test_file=None, verbose=False):
    """Ejecuta los tests para un servicio específico."""
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
    
    # Verificar si el directorio de tests existe
    if not (service_path / "tests").exists():
        print(f"Error: El directorio de tests para '{service_name}' no existe en {service_path / 'tests'}")
        return False
    
    # Construir y ejecutar el comando
    cmd = get_test_command(service_name, test_file)
    
    print(f"\n{'='*80}")
    print(f"Ejecutando tests para {service_name}...")
    print(f"{'='*80}\n")
    
    start_time = time.time()
    
    try:
        # Ejecutar el comando y mostrar la salida en tiempo real
        process = subprocess.Popen(
            cmd,
            shell=True,
            cwd=str(service_path),
            # No redirigimos stdout/stderr para que se muestren en la consola actual
        )
        
        # Esperar a que termine el proceso
        exit_code = process.wait()
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n{'='*80}")
        print(f"Tests para {service_name} completados en {duration:.2f} segundos.")
        print(f"Resultado: {'ÉXITO' if exit_code == 0 else 'FALLO'}")
        print(f"{'='*80}\n")
        
        return exit_code == 0
    
    except Exception as e:
        print(f"Error al ejecutar tests para {service_name}: {str(e)}")
        return False

def run_all_tests(verbose=False):
    """Ejecuta los tests para todos los servicios configurados."""
    results = {}
    all_success = True
    
    for service_name in SERVICES:
        success = run_tests_for_service(service_name, verbose=verbose)
        results[service_name] = success
        if not success:
            all_success = False
    
    # Mostrar resumen
    print("\n" + "="*80)
    print("RESUMEN DE TESTS")
    print("="*80)
    
    for service_name, success in results.items():
        status = "ÉXITO" if success else "FALLO"
        print(f"{service_name}: {status}")
    
    print("="*80)
    print(f"Resultado general: {'ÉXITO' if all_success else 'FALLO'}")
    print("="*80 + "\n")
    
    return all_success

def main():
    """Función principal que procesa los argumentos y ejecuta los tests."""
    parser = argparse.ArgumentParser(description="Script centralizado para ejecutar tests de microservicios SaaS")
    parser.add_argument("--service", help="Nombre del servicio para el que ejecutar tests (por defecto: todos)")
    parser.add_argument("--file", help="Archivo de test específico a ejecutar (opcional)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Modo verbose")
    parser.add_argument("--list", action="store_true", help="Listar servicios disponibles")
    
    args = parser.parse_args()
    
    if args.list:
        print("Servicios disponibles para tests:")
        for name in SERVICES:
            print(f"  - {name}")
        return 0
    
    if args.service:
        if args.service not in SERVICES:
            print(f"Error: Servicio '{args.service}' no encontrado.")
            print("Servicios disponibles:")
            for name in SERVICES:
                print(f"  - {name}")
            return 1
        
        success = run_tests_for_service(args.service, args.file, args.verbose)
        return 0 if success else 1
    else:
        success = run_all_tests(args.verbose)
        return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
