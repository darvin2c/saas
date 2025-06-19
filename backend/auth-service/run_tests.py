#!/usr/bin/env python
"""
Script para ejecutar los tests del servicio de autenticación.
"""
import os
import sys
import pytest

# Asegurarse de que el directorio actual esté en el PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def main():
    """
    Función principal para ejecutar los tests.
    """
    # Configurar argumentos para pytest
    args = [
        "-v",  # Modo verbose
        "--no-header",  # Sin cabecera
        "--tb=native",  # Formato de traceback nativo
        "--no-summary",  # Sin resumen
    ]
    
    # Si se proporciona un archivo específico, ejecutar solo ese test
    if len(sys.argv) > 1:
        test_file = sys.argv[1]
        if not test_file.startswith("tests/"):
            test_file = f"tests/{test_file}"
        args.append(test_file)
    else:
        # Por defecto, ejecutar todos los tests
        args.append("tests/")
    
    # Ejecutar pytest con los argumentos configurados
    exit_code = pytest.main(args)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
