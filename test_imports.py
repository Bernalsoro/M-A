#!/usr/bin/env python3
"""
Script de diagnóstico para verificar que los imports funcionan.
Ejecuta esto ANTES de correr nvidia_case_study.py
"""

import sys
import os
from pathlib import Path

def test_environment():
    """Verifica el entorno de ejecución."""

    print("=" * 70)
    print("  TEST DE CONFIGURACIÓN - Caso Nvidia")
    print("=" * 70)
    print()

    # 1. Verificar Python
    print("✓ Python Version:", sys.version.split()[0])
    print()

    # 2. Verificar directorio actual
    current_dir = Path.cwd()
    print(f"📁 Directorio actual: {current_dir}")
    print()

    # 3. Verificar estructura de carpetas
    print("📂 Verificando estructura de carpetas:")
    required_dirs = ['models', 'analysis', 'examples', 'utils']
    all_exist = True

    for dir_name in required_dirs:
        dir_path = current_dir / dir_name
        exists = dir_path.exists() and dir_path.is_dir()
        symbol = "✅" if exists else "❌"
        print(f"   {symbol} {dir_name}/")
        if not exists:
            all_exist = False
    print()

    # 4. Verificar archivos clave
    print("📄 Verificando archivos clave:")
    key_files = [
        'examples/nvidia_case_study.py',
        'examples/nvidia_standalone.py',
        'models/dcf.py',
        'models/multiples.py',
        'analysis/financial_ratios.py'
    ]

    for file_path in key_files:
        full_path = current_dir / file_path
        exists = full_path.exists() and full_path.is_file()
        symbol = "✅" if exists else "❌"
        print(f"   {symbol} {file_path}")
    print()

    # 5. Test imports
    print("🔧 Probando imports de módulos:")

    # Añadir directorio actual al path (como hace nvidia_case_study.py)
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))

    imports_ok = True
    modules_to_test = [
        ('models.dcf', 'DCFModel'),
        ('models.multiples', 'MultiplesAnalysis'),
        ('models.synergies', 'SynergiesModel'),
        ('analysis.financial_ratios', 'FinancialRatiosAnalysis'),
    ]

    for module_name, class_name in modules_to_test:
        try:
            module = __import__(module_name, fromlist=[class_name])
            getattr(module, class_name)
            print(f"   ✅ {module_name}.{class_name}")
        except ImportError as e:
            print(f"   ❌ {module_name}.{class_name} - ERROR: {e}")
            imports_ok = False
        except AttributeError as e:
            print(f"   ❌ {module_name}.{class_name} - ERROR: {e}")
            imports_ok = False
    print()

    # 6. Verificar librerías externas
    print("📦 Verificando librerías externas:")
    external_libs = [
        'numpy',
        'pandas',
        'scipy',
        'matplotlib',
        'seaborn'
    ]

    libs_ok = True
    for lib in external_libs:
        try:
            __import__(lib)
            print(f"   ✅ {lib}")
        except ImportError:
            print(f"   ❌ {lib} - NO INSTALADO")
            libs_ok = False
    print()

    # 7. DIAGNÓSTICO FINAL
    print("=" * 70)
    print("  DIAGNÓSTICO")
    print("=" * 70)
    print()

    if not all_exist:
        print("❌ PROBLEMA: No estás en el directorio correcto")
        print()
        print("SOLUCIÓN:")
        print("   cd /ruta/a/M-A")
        print("   python test_imports.py")
        print()
        print("Debes ejecutar este script desde el directorio M-A/ (raíz del proyecto)")
        return False

    if not imports_ok:
        print("❌ PROBLEMA: Los módulos del proyecto no se pueden importar")
        print()
        print("SOLUCIÓN:")
        print("   Verifica que estás en el directorio M-A/ (raíz)")
        print("   Y que las carpetas models/ y analysis/ existen")
        return False

    if not libs_ok:
        print("❌ PROBLEMA: Faltan librerías externas")
        print()
        print("SOLUCIÓN:")
        print("   pip install -r requirements.txt")
        print()
        print("O instala manualmente:")
        print("   pip install numpy pandas scipy matplotlib seaborn")
        return False

    # TODO OK
    print("✅ ¡TODO CORRECTO!")
    print()
    print("Puedes ejecutar el análisis de Nvidia con:")
    print()
    print("   OPCIÓN 1 (Completo - 8 modelos):")
    print("   python examples/nvidia_case_study.py")
    print()
    print("   OPCIÓN 2 (Simple - standalone):")
    print("   cd examples && python nvidia_standalone.py")
    print()

    return True


if __name__ == "__main__":
    success = test_environment()
    sys.exit(0 if success else 1)
