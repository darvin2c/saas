param (
    [switch]$Coverage
)

# Verificar si existe el directorio del entorno virtual
if (-not (Test-Path -Path ".venv")) {
    Write-Host "Creando entorno virtual..."
    python -m venv .venv
    if (-not $?) {
        Write-Host "Error al crear el entorno virtual" -ForegroundColor Red
        exit 1
    }
}

# Verificar si existe el ejecutable de Python en el entorno virtual
if (-not (Test-Path -Path ".venv\Scripts\python.exe")) {
    Write-Host "Error: No se encontró el ejecutable de Python en el entorno virtual" -ForegroundColor Red
    exit 1
}

# Verificar si existe el archivo requirements.txt
if (-not (Test-Path -Path "requirements.txt")) {
    Write-Host "Error: No se encontró el archivo requirements.txt" -ForegroundColor Red
    exit 1
}

# Activar el entorno virtual e instalar dependencias
Write-Host "Instalando dependencias..."
.venv\Scripts\python.exe -m pip install -r requirements.txt
if (-not $?) {
    Write-Host "Error al instalar dependencias" -ForegroundColor Red
    exit 1
}

# Configurar variables de entorno para pruebas
$env:DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/saas_test"
$env:SECRET_KEY = "test_secret_key"

# Ejecutar pruebas
if ($Coverage) {
    Write-Host "Ejecutando pruebas con cobertura..."
    .venv\Scripts\python.exe -m pytest tests --cov=app --cov-report=term-missing -v
}
else {
    Write-Host "Ejecutando pruebas..."
    .venv\Scripts\python.exe -m pytest tests -v
}
