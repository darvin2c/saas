#!/bin/bash
# Script para ejecutar los tests del servicio de gateway desde Shell

# Obtener la ruta del directorio actual donde se encuentra este script
SCRIPT_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_PATH="$SCRIPT_PATH"

# Configurar el entorno usando rutas relativas
export PYTHONPATH="$SERVICE_PATH"

# Verificar si existe el entorno virtual, si no, crearlo
if [ ! -d "$SERVICE_PATH/.venv" ]; then
    echo "Creando entorno virtual en $SERVICE_PATH/.venv..."
    python -m venv "$SERVICE_PATH/.venv"
    
    if [ $? -ne 0 ]; then
        echo "ERROR: No se pudo crear el entorno virtual. Asegúrese de tener instalado Python 3.8+ y el módulo venv."
        exit 1
    fi
    echo "Entorno virtual creado correctamente."
fi

# Determinar la ruta al ejecutable de Python
if [ -f "$SERVICE_PATH/.venv/bin/python" ]; then
    PYTHON_PATH="$SERVICE_PATH/.venv/bin/python"
else
    echo "ERROR: No se encontró el ejecutable de Python en el entorno virtual."
    exit 1
fi

# Verificar si existe requirements.txt
if [ ! -f "$SERVICE_PATH/requirements.txt" ]; then
    echo "ERROR: No se encontró el archivo requirements.txt en $SERVICE_PATH"
    echo "Por favor, cree un archivo requirements.txt con las dependencias necesarias para los tests"
    exit 1
fi

# Instalar dependencias desde requirements.txt
echo "Instalando dependencias desde requirements.txt..."
"$PYTHON_PATH" -m pip install -r "$SERVICE_PATH/requirements.txt"

# Configurar variables de entorno
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/saas_test"
export SECRET_KEY="test_secret_key_for_testing_purposes_only"

# Mostrar variables de entorno para depuración
echo "Variables de entorno configuradas:"
echo "DATABASE_URL=$DATABASE_URL"
echo "SECRET_KEY=****" # No mostrar la clave secreta completa por seguridad

# Verificar si se proporcionó un archivo de test específico
if [ $# -gt 0 ]; then
    TEST_FILE="$1"
    # Ejecutar el test específico con salida visible (-s)
    "$PYTHON_PATH" -m pytest "$TEST_FILE" -v -s
else
    # Ejecutar todos los tests con salida visible (-s)
    "$PYTHON_PATH" -m pytest tests -v -s
fi
