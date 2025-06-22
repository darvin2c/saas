import os
import sys
import pytest
import subprocess
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.config import Settings
from dotenv import load_dotenv
from pathlib import Path

# Load test environment
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../.env.test'))

TEST_DATABASE_URL = os.getenv("DATABASE_URL")

# Create test engine and session
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override get_db dependency
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def run_alembic_migrations():
    """Ejecuta las migraciones de Alembic para configurar la base de datos de pruebas."""
    service_path = Path(__file__).parent.parent
    alembic_path = service_path / "alembic"
    
    if not alembic_path.exists():
        raise RuntimeError(f"No se encontró el directorio de migraciones en {alembic_path}")
    
    print("\n=== Configurando base de datos de pruebas con Alembic ===")
    print(f"URL de base de datos: {TEST_DATABASE_URL}")
    
    # Verificar conexión a la base de datos
    try:
        with engine.connect() as connection:
            # Verificar que podemos conectarnos
            result = connection.execute(text("SELECT 1")).fetchone()
            if result and result[0] == 1:
                print("Conexión a la base de datos exitosa")
            
            # Verificar si el esquema auth existe
            schema_exists = connection.execute(text(
                """SELECT EXISTS (
                    SELECT FROM information_schema.schemata 
                    WHERE schema_name = 'auth'
                )"""
            )).scalar()
            
            if schema_exists:
                print("\nℹ️ El esquema 'auth' ya existe")
                print("Eliminando y recreando el esquema completo...")
                
                # Primero, terminar todas las conexiones a la base de datos
                try:
                    connection.execute(text(
                        """SELECT pg_terminate_backend(pid) 
                           FROM pg_stat_activity 
                           WHERE datname = current_database() 
                           AND pid <> pg_backend_pid()"""
                    ))
                except Exception as e:
                    print(f"Advertencia al terminar conexiones: {e}")
                
                # Eliminar el esquema con CASCADE para eliminar todas las tablas
                try:
                    connection.execute(text('DROP SCHEMA auth CASCADE'))
                    print("  - Esquema 'auth' eliminado correctamente")
                except Exception as e:
                    print(f"  - Error al eliminar esquema 'auth': {e}")
                    # Intentar cerrar la conexión actual y crear una nueva
                    connection.close()
                    with engine.connect() as new_conn:
                        new_conn.execute(text('DROP SCHEMA IF EXISTS auth CASCADE'))
                        print("  - Esquema 'auth' eliminado en segundo intento")
                        new_conn.commit()
                    # Reconectar
                    connection = engine.connect()
            else:
                print("\nℹ️ El esquema 'auth' no existe, se creará uno nuevo")
            
            # Crear/recrear el esquema
            connection.execute(text('CREATE SCHEMA IF NOT EXISTS auth'))
            print("  - Esquema 'auth' creado correctamente")
            connection.commit()
            print("Esquema preparado correctamente")
            
    except Exception as e:
        print(f"Error al configurar el esquema: {e}")
        print("Asegúrate de que la base de datos esté en ejecución y accesible")
        print(f"URL de conexión: {TEST_DATABASE_URL}")
        raise
    
    # Ejecutar migraciones con Alembic
    try:
        print("\nEjecutando migraciones con Alembic...")
        
        # Verificar que alembic está instalado
        try:
            import alembic
            print(f"Versión de Alembic: {alembic.__version__}")
        except ImportError:
            print("Alembic no está instalado. Instalando...")
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "alembic"],
                check=True
            )
        
        # Configurar el entorno para Alembic
        env = os.environ.copy()
        env["DATABASE_URL"] = TEST_DATABASE_URL
        env["SCHEMA"] = "auth"
        
        # Ejecutar el comando alembic upgrade head
        print("Ejecutando: alembic upgrade head")
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            cwd=str(service_path),
            env=env,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("Migraciones ejecutadas exitosamente")
            if result.stdout.strip():
                print("Salida:")
                print(result.stdout)
            
            # Verificar que las tablas se crearon correctamente
            with engine.connect() as connection:
                tables = connection.execute(text(
                    "SELECT table_name FROM information_schema.tables WHERE table_schema = 'auth'"
                )).fetchall()
                
                if tables:
                    print(f"Se encontraron {len(tables)} tablas en el esquema 'auth':")
                    for table in tables:
                        print(f"  - {table[0]}")
                    return True
                else:
                    print("\n⚠️ No se encontraron tablas en el esquema 'auth' después de las migraciones")
                    print("Usando SQLAlchemy como fallback...")
                    Base.metadata.create_all(bind=engine)
                    print("Tablas creadas con SQLAlchemy")
                    return False
        else:
            # Verificar si el error es porque las tablas ya existen
            if "DuplicateTable" in result.stderr and "already exists" in result.stderr:
                print("\nℹ️ Las tablas ya existen en la base de datos")
                print("Este error es esperado si las migraciones ya se ejecutaron anteriormente")
                print("Continuando con las pruebas usando las tablas existentes...")
                return True
            else:
                print(f"Error al ejecutar migraciones (código {result.returncode})")
                print("Salida estándar:")
                print(result.stdout)
                print("Error estándar:")
                print(result.stderr)
                
                # Si las migraciones fallan por otro motivo, intentar crear las tablas directamente
                print("\nIntentando crear tablas directamente con SQLAlchemy...")
                Base.metadata.create_all(bind=engine)
                print("Tablas creadas con SQLAlchemy")
                return False
    except Exception as e:
        print(f"Error inesperado al ejecutar migraciones: {e}")
        # Fallback a SQLAlchemy
        print("\nCreando tablas directamente con SQLAlchemy debido al error...")
        Base.metadata.create_all(bind=engine)
        print("Tablas creadas con SQLAlchemy")
        return False

@pytest.fixture(scope="session", autouse=True)
def setup_database(request):
    # Forzar la salida de los mensajes de migración
    capmanager = request.config.pluginmanager.getplugin("capturemanager")
    if capmanager:
        capmanager.suspend_global_capture(in_=True)
        
    print("\n\n" + "=" * 80)
    print("CONFIGURANDO BASE DE DATOS PARA TESTS DE AUTH-SERVICE")
    print("=" * 80)
    
    # Usar migraciones de Alembic en lugar de crear tablas directamente
    success = run_alembic_migrations()
    
    if success:
        print("\n✅ Migraciones completadas exitosamente")
    else:
        print("\n⚠️ Hubo problemas con las migraciones, usando SQLAlchemy como fallback")
    
    print("=" * 80 + "\n")
    
    # Restaurar la captura si estaba activa
    if capmanager:
        capmanager.resume_global_capture()
    
    yield
    
    # No necesitamos limpiar los datos después de las pruebas
    # ya que recreamos el esquema completo al inicio
    
    # Mostrar mensaje de finalización
    if capmanager:
        capmanager.suspend_global_capture(in_=True)
    print("\n" + "=" * 80)
    print("TESTS COMPLETADOS - ESQUEMA LISTO PARA PRÓXIMA EJECUCIÓN")
    print("=" * 80)
    if capmanager:
        capmanager.resume_global_capture()

@pytest.fixture(scope="function")
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="function")
def client(setup_database):
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
