# Script de desarrollo para Windows que facilita la ejecución de los microservicios
# Este script es equivalente a dev.bat pero usando PowerShell

# Obtener la ruta del directorio actual donde se encuentra este script
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path

# Ejecutar dev.py con los argumentos pasados a este script
& python "$scriptPath\dev.py" $args

# Si se presiona Ctrl+C, asegurarse de que se propague al proceso de Python
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
