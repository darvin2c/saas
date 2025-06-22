# Script para ejecutar tests de microservicios SaaS en Windows
# Este script es equivalente a test.bat pero usando PowerShell

# Obtener la ruta del directorio actual donde se encuentra este script
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path

# Ejecutar test.py con los argumentos pasados a este script
& python "$scriptPath\tests.py" $args

# Si se presiona Ctrl+C, asegurarse de que se propague al proceso de Python
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
