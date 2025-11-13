#!/bin/bash

# =============================================================================
# NVIDIA M&A ANALYSIS - SETUP Y EJECUCIÓN COMPLETA
# =============================================================================
#
# Este script instala todo lo necesario y ejecuta el análisis completo de Nvidia
#
# Uso: bash run_nvidia_analysis.sh
#

set -e  # Exit on error

echo ""
echo "════════════════════════════════════════════════════════════════════"
echo "  NVIDIA M&A ANALYSIS - Setup e Instalación"
echo "════════════════════════════════════════════════════════════════════"
echo ""

# Verificar Python
echo "🔍 Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no encontrado. Por favor instala Python 3.8+"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Python $PYTHON_VERSION encontrado"
echo ""

# Crear entorno virtual (opcional pero recomendado)
echo "📦 Configurando entorno virtual..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Entorno virtual creado"
else
    echo "✅ Entorno virtual ya existe"
fi

# Activar entorno virtual
echo "🔧 Activando entorno virtual..."
source venv/bin/activate || . venv/Scripts/activate 2>/dev/null

echo ""
echo "════════════════════════════════════════════════════════════════════"
echo "  Instalando Dependencias"
echo "════════════════════════════════════════════════════════════════════"
echo ""

# Instalar dependencias
echo "📥 Instalando paquetes Python (esto puede tardar 1-2 minutos)..."
pip install --upgrade pip -q

# Dependencias core
pip install numpy>=1.21.0 -q
pip install scipy>=1.7.0 -q
pip install pandas>=1.3.0 -q

# Visualización
pip install matplotlib>=3.4.3 -q
pip install seaborn>=0.11.2 -q

# Jupyter
pip install jupyter -q
pip install ipykernel -q
pip install nbconvert -q
pip install nbformat -q

echo "✅ Todas las dependencias instaladas correctamente"
echo ""

echo "════════════════════════════════════════════════════════════════════"
echo "  Verificando Instalación"
echo "════════════════════════════════════════════════════════════════════"
echo ""

# Verificar imports
python3 << 'VERIFY'
import sys
try:
    import numpy
    print(f"✅ NumPy {numpy.__version__}")
except ImportError:
    print("❌ NumPy no instalado")
    sys.exit(1)

try:
    import pandas
    print(f"✅ Pandas {pandas.__version__}")
except ImportError:
    print("❌ Pandas no instalado")
    sys.exit(1)

try:
    import matplotlib
    print(f"✅ Matplotlib {matplotlib.__version__}")
except ImportError:
    print("❌ Matplotlib no instalado")
    sys.exit(1)

try:
    import seaborn
    print(f"✅ Seaborn {seaborn.__version__}")
except ImportError:
    print("❌ Seaborn no instalado")
    sys.exit(1)

try:
    import jupyter
    print(f"✅ Jupyter instalado")
except ImportError:
    print("❌ Jupyter no instalado")
    sys.exit(1)

print("\n✅ Todas las verificaciones pasaron correctamente")
VERIFY

echo ""
echo "════════════════════════════════════════════════════════════════════"
echo "  Ejecutando Análisis de Nvidia"
echo "════════════════════════════════════════════════════════════════════"
echo ""

# Preguntar qué quiere ejecutar
echo "¿Qué deseas ejecutar?"
echo ""
echo "1) Script Python (output a consola)"
echo "2) Jupyter Notebook (interactivo en navegador)"
echo "3) Generar HTML del análisis"
echo "4) TODO (Script + HTML + abrir Jupyter)"
echo ""
read -p "Selecciona una opción (1-4): " option

case $option in
    1)
        echo ""
        echo "🚀 Ejecutando análisis completo..."
        echo ""
        python3 examples/nvidia_case_study.py
        echo ""
        echo "✅ Análisis completado!"
        ;;
    2)
        echo ""
        echo "🚀 Abriendo Jupyter Notebook..."
        echo ""
        echo "El navegador se abrirá automáticamente."
        echo "Navega a: nvidia_analysis_storytelling.ipynb"
        echo ""
        jupyter notebook examples/
        ;;
    3)
        echo ""
        echo "🚀 Generando HTML..."
        echo ""
        jupyter nbconvert --to html examples/nvidia_analysis_storytelling.ipynb --output nvidia_analysis.html
        echo ""
        echo "✅ HTML generado: examples/nvidia_analysis.html"
        echo "   Abre este archivo en tu navegador"
        ;;
    4)
        echo ""
        echo "🚀 Ejecutando TODO..."
        echo ""

        # 1. Script
        echo "1/3 - Ejecutando script Python..."
        python3 examples/nvidia_case_study.py > nvidia_analysis_output.txt
        echo "✅ Output guardado en: nvidia_analysis_output.txt"
        echo ""

        # 2. HTML
        echo "2/3 - Generando HTML..."
        jupyter nbconvert --to html examples/nvidia_analysis_storytelling.ipynb --output nvidia_analysis.html
        echo "✅ HTML generado: examples/nvidia_analysis.html"
        echo ""

        # 3. Abrir Jupyter
        echo "3/3 - Abriendo Jupyter Notebook..."
        echo "   Navega a: nvidia_analysis_storytelling.ipynb"
        echo ""
        jupyter notebook examples/
        ;;
    *)
        echo "Opción inválida"
        exit 1
        ;;
esac

echo ""
echo "════════════════════════════════════════════════════════════════════"
echo "  ✅ COMPLETADO"
echo "════════════════════════════════════════════════════════════════════"
echo ""
echo "📁 Archivos disponibles:"
echo "   - examples/nvidia_case_study.py (script Python)"
echo "   - examples/nvidia_analysis_storytelling.ipynb (Jupyter)"
echo "   - examples/nvidia_analysis.html (HTML para navegador)"
echo ""
echo "📖 Para más información:"
echo "   - examples/COMO_VER_NOTEBOOK.md"
echo "   - examples/README_NOTEBOOKS.md"
echo ""
echo "🎉 ¡Disfruta del análisis!"
echo ""
