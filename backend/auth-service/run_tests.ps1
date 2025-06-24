# Script para ejecutar los tests del servicio de gateway desde PowerShell

# Obtener la ruta del directorio actual donde se encuentra este script
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$servicePath = $scriptPath

# Configurar el entorno usando rutas relativas
$env:PYTHONPATH = $servicePath

# Verificar si existe el entorno virtual, si no, crearlo
if (-not (Test-Path -Path "$servicePath\.venv")) {
    Write-Host "Creando entorno virtual en $servicePath\.venv..."
    python -m venv "$servicePath\.venv"
    
    if (-not $?) {
        Write-Error "ERROR: No se pudo crear el entorno virtual. Asegúrese de tener instalado Python 3.8+ y el módulo venv."
        exit 1
    }
    Write-Host "Entorno virtual creado correctamente."
}

# Determinar la ruta al ejecutable de Python
if (Test-Path -Path "$servicePath\.venv\Scripts\python.exe") {
    $pythonPath = "$servicePath\.venv\Scripts\python.exe"
} else {
    Write-Error "ERROR: No se encontró el ejecutable de Python en el entorno virtual."
    exit 1
}

# Verificar si existe requirements.txt
if (-not (Test-Path -Path "$servicePath\requirements.txt")) {
    Write-Error "ERROR: No se encontró el archivo requirements.txt en $servicePath"
    Write-Error "Por favor, cree un archivo requirements.txt con las dependencias necesarias para los tests"
    exit 1
}

# Instalar dependencias desde requirements.txt
Write-Host "Instalando dependencias desde requirements.txt..."
& $pythonPath -m pip install -r "$servicePath\requirements.txt"

# Mostrar variables de entorno para depuración
Write-Host "Variables de entorno configuradas:"
Write-Host "DATABASE_URL=$env:DATABASE_URL"
Write-Host "SECRET_KEY=****" # No mostrar la clave secreta completa por seguridad

# Verificar si se proporcionó un archivo de test específico
if ($args.Count -gt 0) {
    $testFile = $args[0]
    # Ejecutar el test específico con salida visible (-s)
    & $pythonPath -m pytest $testFile -v -s
}
else {
    # Ejecutar todos los tests con salida visible (-s)
    & $pythonPath -m pytest tests -v -s
}
