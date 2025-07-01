#!/bin/bash

# Verificar si existe el directorio del entorno virtual
if [ ! -d ".venv" ]; then
    echo "Creando entorno virtual..."
    python -m venv .venv
    if [ $? -ne 0 ]; then
        echo "Error al crear el entorno virtual"
        exit 1
    fi
fi

# Verificar si existe el ejecutable de Python en el entorno virtual
if [ ! -f ".venv/bin/python" ]; then
    echo "Error: No se encontró el ejecutable de Python en el entorno virtual"
    exit 1
fi

# Verificar si existe el archivo requirements.txt
if [ ! -f "requirements.txt" ]; then
    echo "Error: No se encontró el archivo requirements.txt"
    exit 1
fi

# Activar el entorno virtual e instalar dependencias
echo "Instalando dependencias..."
.venv/bin/pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Error al instalar dependencias"
    exit 1
fi

# Configurar variables de entorno para pruebas
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/dentist_service_test"
export SECRET_KEY="test_secret_key"

# Ejecutar pruebas
if [ "$1" == "--coverage" ]; then
    echo "Ejecutando pruebas con cobertura..."
    .venv/bin/python -m pytest tests --cov=app --cov-report=term-missing -v
else
    echo "Ejecutando pruebas..."
    .venv/bin/python -m pytest tests -v
fi
