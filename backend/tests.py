#!/usr/bin/env python
"""Script centralizado para ejecutar tests de todos los microservicios del proyecto SaaS.
Este script permite ejecutar tests de servicios específicos o de todos los servicios a la vez."""

import os
import sys
import subprocess
import argparse
import platform
import time
import stat
from pathlib import Path

# Configuración de rutas base
BASE_DIR = Path(__file__).parent
SERVICES = {
    "auth-service": {
        "path": BASE_DIR / "auth-service",
    },
    "gateway-service": {
        "path": BASE_DIR / "gateway-service",
    },
    "dentist-service": {
        "path": BASE_DIR / "dentist-service",
    }
}

def is_windows():
    """Verifica si el sistema operativo es Windows."""
    return platform.system().lower() == "windows"

def setup_test_database():
    """Configura la base de datos de pruebas antes de ejecutar los tests."""
    print("\n" + "="*80)
    print("CONFIGURANDO BASE DE DATOS DE PRUEBAS")
    print("="*80 + "\n")
    
    setup_script = BASE_DIR / "setup_test_db.py"
    if not setup_script.exists():
        print(f"Error: No se encontró el script de configuración de base de datos en {setup_script}")
        return False
    
    try:
        cmd = f"{sys.executable} {setup_script}"
        print(f"Ejecutando: {cmd}")
        
        process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Mostrar la salida en tiempo real
        for line in process.stdout:
            print(line, end='')
        
        exit_code = process.wait()
        
        if exit_code == 0:
            print("\n✅ Base de datos configurada correctamente")
            return True
        else:
            print(f"\n❌ Error al configurar la base de datos (código {exit_code})")
            return False
    
    except Exception as e:
        print(f"Error al configurar la base de datos: {str(e)}")
        return False

def run_tests_for_service(service_name, test_file=None, verbose=False):
    """Ejecuta los tests para un servicio específico."""
    if service_name not in SERVICES:
        print(f"Error: El servicio '{service_name}' no está configurado.")
        return False
    
    service = SERVICES[service_name]
    service_path = service["path"]
    
    # Verificar si el servicio existe
    if not service_path.exists():
        print(f"Error: El directorio del servicio '{service_name}' no existe en {service_path}")
        return False
    
    # Verificar si existe el script run_tests.ps1 o run_tests.sh
    run_script = None
    if is_windows() and (service_path / "run_tests.ps1").exists():
        run_script = service_path / "run_tests.ps1"
        cmd_prefix = "powershell -ExecutionPolicy Bypass -File"
    elif not is_windows() and (service_path / "run_tests.sh").exists():
        run_script = service_path / "run_tests.sh"
        # Asegurar que el script tenga permisos de ejecución
        try:
            current_permissions = run_script.stat().st_mode
            run_script.chmod(current_permissions | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
            print(f"Python path: {sys.executable}")
            print(f"Current working directory: {service_path}")
        except Exception as e:
            print(f"Advertencia: No se pudieron establecer permisos de ejecución: {e}")
        cmd_prefix = "bash"
    
    if not run_script:
        print(f"Error: No se encontró un script run_tests para '{service_name}'")
        return False
    
    # Construir el comando
    cmd = f"{cmd_prefix} \"{run_script}\""
    if test_file:
        if not test_file.startswith("tests/"):
            test_file = f"tests/{test_file}"
        cmd += f" {test_file}"
    
    print(f"\n{'='*80}")
    print(f"Ejecutando tests para {service_name}...")
    print(f"{'='*80}\n")
    
    start_time = time.time()
    
    try:
        # Ejecutar el comando directamente sin capturar la salida
        # Esto evita problemas de codificación de caracteres
        process = subprocess.run(
            cmd,
            shell=True,
            cwd=str(service_path),
            check=False
        )
        
        exit_code = process.returncode
        
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
        # Verificar si el servicio existe y tiene un script run_tests
        service_path = SERVICES[service_name]["path"]
        if not service_path.exists():
            print(f"Omitiendo {service_name}: El directorio no existe")
            continue
            
        run_script_exists = False
        if is_windows() and (service_path / "run_tests.ps1").exists():
            run_script_exists = True
        elif not is_windows() and (service_path / "run_tests.sh").exists():
            run_script_exists = True
            
        if not run_script_exists:
            print(f"Omitiendo {service_name}: No se encontró un script run_tests")
            continue
        
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
    
    return all_success

def main():
    """Función principal que procesa los argumentos y ejecuta los tests."""
    parser = argparse.ArgumentParser(description='Ejecutar tests para los microservicios del proyecto SaaS.')
    parser.add_argument('service', nargs='?', help='Nombre del servicio para el que ejecutar los tests')
    parser.add_argument('--test-file', '-t', help='Archivo de test específico a ejecutar')
    parser.add_argument('--skip-db-setup', '-s', action='store_true', help='Omitir la configuración de la base de datos')
    parser.add_argument('--verbose', '-v', action='store_true', help='Mostrar información detallada')
    
    args = parser.parse_args()
    
    # Configurar la base de datos si no se omite
    if not args.skip_db_setup:
        if not setup_test_database():
            print("Error al configurar la base de datos. Abortando.")
            return 1
    
    # Ejecutar los tests
    if args.service:
        if args.service not in SERVICES:
            print(f"Error: El servicio '{args.service}' no está configurado.")
            print(f"Servicios disponibles: {', '.join(SERVICES.keys())}")
            return 1
        
        success = run_tests_for_service(args.service, args.test_file, args.verbose)
    else:
        success = run_all_tests(args.verbose)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
