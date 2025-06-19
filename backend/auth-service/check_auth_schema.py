#!/usr/bin/env python
import psycopg2
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Obtener la URL de la base de datos
DATABASE_URL = os.getenv("DATABASE_URL")

def check_auth_schema():
    """
    Verifica la conexión a la base de datos y lista las tablas en el esquema auth.
    """
    try:
        # Conectar a la base de datos
        conn = psycopg2.connect(DATABASE_URL)
        
        # Crear un cursor
        cur = conn.cursor()
        
        # Verificar si existe el esquema auth
        cur.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'auth';")
        schema_exists = cur.fetchone()
        
        if schema_exists:
            print("✅ El esquema 'auth' existe en la base de datos.")
            
            # Listar todas las tablas en el esquema auth
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'auth' 
                ORDER BY table_name;
            """)
            
            tables = cur.fetchall()
            
            if tables:
                print("\nTablas en el esquema 'auth':")
                for table in tables:
                    print(f"  - {table[0]}")
                
                # Para cada tabla, mostrar sus columnas
                for table in tables:
                    cur.execute(f"""
                        SELECT column_name, data_type 
                        FROM information_schema.columns 
                        WHERE table_schema = 'auth' AND table_name = '{table[0]}' 
                        ORDER BY ordinal_position;
                    """)
                    
                    columns = cur.fetchall()
                    
                    print(f"\nColumnas de la tabla '{table[0]}':")
                    for column in columns:
                        print(f"  - {column[0]} ({column[1]})")
            else:
                print("❌ No hay tablas en el esquema 'auth'.")
        else:
            print("❌ El esquema 'auth' no existe en la base de datos.")
            
        # Verificar la tabla alembic_version y su ubicación
        cur.execute("""
            SELECT table_schema, table_name 
            FROM information_schema.tables 
            WHERE table_name = 'alembic_version';
        """)
        
        alembic_version = cur.fetchone()
        
        if alembic_version:
            print(f"\nLa tabla 'alembic_version' existe en el esquema '{alembic_version[0]}'.")
            
            # Mostrar el contenido de la tabla alembic_version
            cur.execute(f"SELECT version_num FROM {alembic_version[0]}.alembic_version;")
            version = cur.fetchone()
            
            if version:
                print(f"Versión actual de la migración: {version[0]}")
            else:
                print("La tabla 'alembic_version' está vacía.")
        else:
            print("\n❌ La tabla 'alembic_version' no existe en la base de datos.")
        
        # Cerrar el cursor y la conexión
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error al conectar a la base de datos: {e}")

if __name__ == "__main__":
    check_auth_schema()
