#!/usr/bin/env python
"""Script para crear y configurar la base de datos PostgreSQL para los tests.
Este script crea la base de datos si no existe, o la limpia si ya existe,
y crea los esquemas necesarios para cada servicio. Las migraciones deben ser
ejecutadas por cada servicio individualmente.
"""

import os
import sys
import subprocess
import platform
import time
from pathlib import Path

# Configuración de la base de datos
DB_USER = "postgres"
DB_PASSWORD = "postgres"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "saas_test"  # Usamos un nombre específico para la base de datos de tests
DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Configuración de esquemas y servicios
SCHEMAS = {
    "auth-service": {
        "schema": "auth",
        "path": Path(__file__).parent / "auth-service",
        "migrations_dir": "alembic"
    },
    "gateway-service": {
        "schema": "gateway",
        "path": Path(__file__).parent / "gateway-service",
        "migrations_dir": "alembic"
    },
    "dentist-service": {
        "schema": "dentist",
        "path": Path(__file__).parent / "dentist-service",
        "migrations_dir": "alembic"
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

def run_command(cmd, cwd=None, timeout=60):
    """Ejecuta un comando con un timeout para evitar bloqueos."""
    print(f"Ejecutando: {cmd}")
    try:
        # Usar subprocess.run en lugar de Popen para mayor simplicidad y control
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=str(cwd) if cwd else None,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,  # Añadir timeout para evitar bloqueos indefinidos
            encoding='utf-8'
        )
        
        # Mostrar la salida
        if result.stdout:
            print(result.stdout)
        
        # Si hay error, mostrar la salida de error
        if result.returncode != 0 and result.stderr:
            print(f"ERROR: {result.stderr}")
        
        return result.returncode == 0
    
    except subprocess.TimeoutExpired:
        print(f"ERROR: El comando se excedió del tiempo límite ({timeout} segundos) y fue abortado.")
        return False
    except Exception as e:
        print(f"Error al ejecutar el comando: {str(e)}")
        return False

def check_postgres():
    """Verifica si PostgreSQL está en ejecución."""
    print("Verificando conexión a PostgreSQL...")
    
    try:
        import psycopg2
        conn = psycopg2.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            connect_timeout=5,
            dbname="postgres"  # Conectamos a la base de datos por defecto
        )
        conn.close()
        print("Conexión a PostgreSQL exitosa!")
        return True
    except Exception as e:
        print(f"Error al conectar a PostgreSQL: {str(e)}")
        print("Asegúrate de que PostgreSQL esté en ejecución y accesible.")
        return False

def setup_database():
    """Crea la base de datos si no existe o la limpia si ya existe."""
    print(f"Configurando base de datos '{DB_NAME}' para tests...")
    
    try:
        import psycopg2
        # Conectar a la base de datos 'postgres' para crear o limpiar nuestra base de datos
        conn = psycopg2.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            dbname="postgres"
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Verificar si la base de datos ya existe
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}'")
        exists = cursor.fetchone()
        
        if exists:
            print(f"La base de datos '{DB_NAME}' ya existe. Limpiando...")
            
            # Cerrar todas las conexiones a la base de datos
            cursor.execute(f"""
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = '{DB_NAME}'
                AND pid <> pg_backend_pid()
            """)
            
            # Eliminar la base de datos
            cursor.execute(f"DROP DATABASE {DB_NAME}")
            print(f"Base de datos '{DB_NAME}' eliminada.")
        
        # Crear la base de datos
        cursor.execute(f"CREATE DATABASE {DB_NAME}")
        print(f"Base de datos '{DB_NAME}' creada exitosamente!")
        
        cursor.close()
        conn.close()
        
        # Ahora conectamos a la nueva base de datos para crear los esquemas
        conn = psycopg2.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Crear esquemas para cada servicio
        for service_name, config in SCHEMAS.items():
            schema = config["schema"]
            print(f"Creando esquema '{schema}' para {service_name}...")
            cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")
        
        cursor.close()
        conn.close()
        
        return True
    except Exception as e:
        print(f"Error al configurar la base de datos: {str(e)}")
        return False

# La función run_migrations ha sido eliminada ya que cada servicio ejecutará sus propias migraciones

def main():
    """Función principal."""
    print("\n" + "="*80)
    print("CONFIGURACIÓN DE BASE DE DATOS PARA TESTS")
    print("="*80 + "\n")
    
    # Verificar que psycopg2 esté instalado
    try:
        import psycopg2
    except ImportError:
        print("Error: El módulo psycopg2 no está instalado.")
        print("Instálalo con: pip install psycopg2-binary")
        return 1
    
    # Verificar PostgreSQL
    if not check_postgres():
        print("No se pudo conectar a PostgreSQL. Abortando.")
        return 1
    
    # Configurar base de datos
    if not setup_database():
        print("No se pudo configurar la base de datos. Abortando.")
        return 1
    
    # Ya no ejecutamos migraciones, cada servicio lo hará por su cuenta
    
    print("\n" + "="*80)
    print("CONFIGURACIÓN DE BASE DE DATOS PARA TESTS COMPLETADA EXITOSAMENTE")
    print("="*80 + "\n")
    
    print(f"Base de datos: {DB_NAME}")
    print(f"URL de conexión: {DB_URL}")
    print("\nEsquemas creados:")
    for service_name, config in SCHEMAS.items():
        print(f"  - {config['schema']} (para {service_name})")
    print("\nNota: Las migraciones deben ser ejecutadas por cada servicio individualmente.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
