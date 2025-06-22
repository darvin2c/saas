#!/bin/bash
# Script de desarrollo para facilitar la ejecución de los microservicios
# Compatible con Linux

# Obtener la ruta del directorio actual donde se encuentra este script
SCRIPT_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Crear ruta al script Python
DEV_PY_PATH="$SCRIPT_PATH/dev.py"

# Ejecutar dev.py con los argumentos pasados a este script
python "$DEV_PY_PATH" "$@"

# Propagar el código de salida
exit $?
