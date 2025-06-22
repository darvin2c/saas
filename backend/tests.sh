#!/bin/bash
# Script para ejecutar tests de microservicios SaaS
# Compatible con Linux

# Obtener la ruta del directorio actual donde se encuentra este script
SCRIPT_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Crear ruta al script Python
TESTS_PY_PATH="$SCRIPT_PATH/tests.py"

# Asegurar que el script tests.py tenga permisos de ejecución
chmod +x "$TESTS_PY_PATH" 2>/dev/null || true

# Ejecutar test.py con los argumentos pasados a este script
python "$TESTS_PY_PATH" "$@"

# Propagar el código de salida
exit $?
