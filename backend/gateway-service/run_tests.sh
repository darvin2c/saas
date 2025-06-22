#!/bin/bash
# Script para ejecutar los tests del servicio de gateway desde Shell

# Obtener la ruta del directorio actual donde se encuentra este script
SCRIPT_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_PATH="$SCRIPT_PATH"

# Configurar el entorno usando rutas relativas
export PYTHONPATH="$SERVICE_PATH"

# Determinar la ruta al ejecutable de Python
if [ -f "$SERVICE_PATH/.venv/bin/python" ]; then
    PYTHON_PATH="$SERVICE_PATH/.venv/bin/python"
else
    # Usar el Python del sistema si no existe el entorno virtual
    PYTHON_PATH="python"
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

# Verificar si se proporcionó un archivo de test específico
if [ $# -gt 0 ]; then
    TEST_FILE="$1"
    # Ejecutar el test específico con salida visible (-s)
    "$PYTHON_PATH" -m pytest "$TEST_FILE" -v -s
else
    # Ejecutar todos los tests con salida visible (-s)
    "$PYTHON_PATH" -m pytest tests -v -s
fi
