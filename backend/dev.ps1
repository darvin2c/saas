# Script de desarrollo para facilitar la ejecución de los microservicios
# Compatible con Windows y Linux

# Obtener la ruta del directorio actual donde se encuentra este script
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path

# Usar Join-Path para crear rutas compatibles con el sistema operativo
$devPyPath = Join-Path -Path $scriptPath -ChildPath "dev.py"

# Ejecutar dev.py con los argumentos pasados a este script
& python $devPyPath $args

# Si se presiona Ctrl+C, asegurarse de que se propague al proceso de Python
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
