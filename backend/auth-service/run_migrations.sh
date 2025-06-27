#!/bin/bash
# Script para ejecutar las migraciones de base de datos del servicio de autenticación

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
    echo "Por favor, cree un archivo requirements.txt con las dependencias necesarias"
    exit 1
fi

# Instalar dependencias desde requirements.txt
echo "Instalando dependencias desde requirements.txt..."
"$PYTHON_PATH" -m pip install -r "$SERVICE_PATH/requirements.txt"

# Verificar si se ha proporcionado DATABASE_URL como variable de entorno
if [ -z "$DATABASE_URL" ]; then
    echo "ADVERTENCIA: No se encontró variable DATABASE_URL."
    echo "Por favor, proporcione la variable DATABASE_URL como variable de entorno."
    exit 1
fi

# Mostrar información sobre la operación
echo "Ejecutando migraciones de base de datos..."
echo "DATABASE_URL=${DATABASE_URL//:*@/:****@}" # Ocultar contraseña en la salida

# Verificar el comando proporcionado o usar 'upgrade head' por defecto
COMMAND=${1:-"upgrade head"}

# Ejecutar el comando de Alembic
echo "Ejecutando: alembic $COMMAND"
# Dividir el comando en palabras para pasarlas como argumentos separados
read -ra ALEMBIC_ARGS <<< "$COMMAND"
"$PYTHON_PATH" -m alembic "${ALEMBIC_ARGS[@]}"

# Verificar si la ejecución fue exitosa
if [ $? -eq 0 ]; then
    echo "Migraciones completadas exitosamente."
else
    echo "ERROR: Falló la ejecución de las migraciones."
    exit 1
fi
