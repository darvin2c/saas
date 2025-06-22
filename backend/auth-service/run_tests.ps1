# Script para ejecutar los tests del servicio de autenticación desde PowerShell

# Configurar el entorno
$env:PYTHONPATH = "c:\projects\saas\backend\auth-service"

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
