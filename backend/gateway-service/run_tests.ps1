# Script para ejecutar los tests del servicio de gateway desde PowerShell

# Obtener la ruta del directorio actual donde se encuentra este script
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$servicePath = $scriptPath

# Configurar el entorno usando rutas relativas
$env:PYTHONPATH = $servicePath

# Verificar si se proporcionó un archivo de test específico
if ($args.Count -gt 0) {
    $testFile = $args[0]
    # Ejecutar el test específico con salida visible (-s)
    .\.venv\Scripts\python -m pytest $testFile -v -s
}
else {
    # Ejecutar todos los tests con salida visible (-s)
    .\.venv\Scripts\python -m pytest tests -v -s
}
