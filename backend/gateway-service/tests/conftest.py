import pytest
import sys
import os
from pathlib import Path

# Añadir el directorio raíz del proyecto al path para que las importaciones funcionen
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configuración global para pytest
def pytest_configure(config):
    """Configuración inicial para pytest."""
    # Asegurarse de que estamos usando el entorno virtual correcto
    print(f"Python path: {sys.executable}")
    print(f"Current working directory: {os.getcwd()}")
