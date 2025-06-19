#!/usr/bin/env python
"""
Script para ejecutar un test específico del servicio de autenticación.
"""
import os
import sys
import pytest

# Asegurarse de que el directorio actual esté en el PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def main():
    """
    Función principal para ejecutar un test específico.
    """
    # Verificar que se proporcionó un nombre de test
    if len(sys.argv) < 2:
        print("Error: Debe proporcionar el nombre del test a ejecutar.")
        print("Uso: python run_single_test.py <nombre_del_test>")
        sys.exit(1)
    
    # Obtener el nombre del test
    test_name = sys.argv[1]
    
    # Configurar argumentos para pytest
    args = [
        "-v",  # Modo verbose
        "--no-header",  # Sin cabecera
        "--tb=native",  # Formato de traceback nativo
        "--no-summary",  # Sin resumen
        "-k", test_name  # Filtrar por nombre de test
    ]
    
    # Si se proporciona un archivo específico, ejecutar solo ese test
    if len(sys.argv) > 2:
        test_file = sys.argv[2]
        if not test_file.startswith("tests/"):
            test_file = f"tests/{test_file}"
        args.append(test_file)
    else:
        # Por defecto, buscar en todos los tests
        args.append("tests/")
    
    # Ejecutar pytest con los argumentos configurados
    exit_code = pytest.main(args)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
