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
            
            # Verificar si el esquema dentist existe
            result = connection.execute(text(
                "SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'dentist'"
            )).fetchone()
            
            if not result:
                print("Creando esquema 'dentist'...")
                connection.execute(text("CREATE SCHEMA IF NOT EXISTS dentist"))
                connection.commit()
                print("Esquema 'dentist' creado correctamente")
            else:
                print("El esquema 'dentist' ya existe")
    except Exception as e:
        print(f"Error al verificar/crear el esquema: {e}")
        raise
    
    # Ejecutar migraciones de Alembic
    try:
        # Configurar el entorno para que use el directorio del servicio de dentistas
        env = os.environ.copy()
        env["PYTHONPATH"] = str(service_path)
        
        # Ejecutar upgrade head
        print("Ejecutando migraciones de Alembic...")
        alembic_ini = service_path / "alembic.ini"
        
        result = subprocess.run(
            ["alembic", "-c", str(alembic_ini), "upgrade", "head"],
            env=env,
            cwd=str(service_path),
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"Error al ejecutar migraciones: {result.stderr}")
            raise RuntimeError(f"Error al ejecutar migraciones de Alembic: {result.stderr}")
        
        print("Migraciones aplicadas correctamente")
        print(result.stdout)
        
    except Exception as e:
        print(f"Error al ejecutar migraciones: {e}")
        raise

@pytest.fixture(scope="session")
def setup_database(request):
    """Configura la base de datos para las pruebas."""
    # Ejecutar migraciones
    run_alembic_migrations()
    
    # Limpiar datos al finalizar
    def teardown():
        print("\n=== Limpiando base de datos de pruebas ===")
        try:
            with engine.connect() as connection:
                # Truncar todas las tablas en el esquema dentist
                connection.execute(text("TRUNCATE TABLE dentist.patients CASCADE"))
                connection.commit()
                print("Tablas limpiadas correctamente")
        except Exception as e:
            print(f"Error al limpiar tablas: {e}")
    
    request.addfinalizer(teardown)
    return None

@pytest.fixture
def db_session(setup_database):
    """Proporciona una sesión de base de datos para las pruebas."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def client(setup_database):
    """Proporciona un cliente de prueba para la API."""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
