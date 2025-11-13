@echo off
REM =============================================================================
REM NVIDIA M&A ANALYSIS - SETUP Y EJECUCIÓN COMPLETA (WINDOWS)
REM =============================================================================
REM
REM Este script instala todo lo necesario y ejecuta el análisis completo de Nvidia
REM
REM Uso: run_nvidia_analysis.bat
REM

echo.
echo ========================================================================
echo   NVIDIA M&A ANALYSIS - Setup e Instalacion
echo ========================================================================
echo.

REM Verificar Python
echo Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no encontrado. Instala Python 3.8+ desde python.org
    pause
    exit /b 1
)

python --version
echo Python encontrado correctamente
echo.

REM Crear entorno virtual
echo Configurando entorno virtual...
if not exist "venv" (
    python -m venv venv
    echo Entorno virtual creado
) else (
    echo Entorno virtual ya existe
)

REM Activar entorno virtual
call venv\Scripts\activate.bat

echo.
echo ========================================================================
echo   Instalando Dependencias
echo ========================================================================
echo.

echo Instalando paquetes Python (esto puede tardar 1-2 minutos)...
python -m pip install --upgrade pip --quiet

REM Dependencias core
pip install numpy>=1.21.0 --quiet
pip install scipy>=1.7.0 --quiet
pip install pandas>=1.3.0 --quiet

REM Visualización
pip install matplotlib>=3.4.3 --quiet
pip install seaborn>=0.11.2 --quiet

REM Jupyter
pip install jupyter --quiet
pip install ipykernel --quiet
pip install nbconvert --quiet
pip install nbformat --quiet

echo Todas las dependencias instaladas correctamente
echo.

echo ========================================================================
echo   Verificando Instalacion
echo ========================================================================
echo.

python -c "import numpy; print('NumPy', numpy.__version__)"
python -c "import pandas; print('Pandas', pandas.__version__)"
python -c "import matplotlib; print('Matplotlib', matplotlib.__version__)"
python -c "import seaborn; print('Seaborn', seaborn.__version__)"
python -c "import jupyter; print('Jupyter instalado')"

echo.
echo Todas las verificaciones pasaron correctamente
echo.

echo ========================================================================
echo   Ejecutando Análisis de Nvidia
echo ========================================================================
echo.

echo Que deseas ejecutar?
echo.
echo 1) Script Python (output a consola)
echo 2) Jupyter Notebook (interactivo en navegador)
echo 3) Generar HTML del análisis
echo 4) TODO (Script + HTML + abrir Jupyter)
echo.
set /p option="Selecciona una opcion (1-4): "

if "%option%"=="1" (
    echo.
    echo Ejecutando análisis completo...
    echo.
    python examples\nvidia_case_study.py
    echo.
    echo Análisis completado!
    pause
) else if "%option%"=="2" (
    echo.
    echo Abriendo Jupyter Notebook...
    echo.
    echo El navegador se abrirá automáticamente.
    echo Navega a: nvidia_analysis_storytelling.ipynb
    echo.
    jupyter notebook examples\
) else if "%option%"=="3" (
    echo.
    echo Generando HTML...
    echo.
    jupyter nbconvert --to html examples\nvidia_analysis_storytelling.ipynb --output nvidia_analysis.html
    echo.
    echo HTML generado: examples\nvidia_analysis.html
    echo Abre este archivo en tu navegador
    pause
) else if "%option%"=="4" (
    echo.
    echo Ejecutando TODO...
    echo.

    echo 1/3 - Ejecutando script Python...
    python examples\nvidia_case_study.py > nvidia_analysis_output.txt
    echo Output guardado en: nvidia_analysis_output.txt
    echo.

    echo 2/3 - Generando HTML...
    jupyter nbconvert --to html examples\nvidia_analysis_storytelling.ipynb --output nvidia_analysis.html
    echo HTML generado: examples\nvidia_analysis.html
    echo.

    echo 3/3 - Abriendo Jupyter Notebook...
    echo Navega a: nvidia_analysis_storytelling.ipynb
    echo.
    start jupyter notebook examples\
) else (
    echo Opcion invalida
    pause
    exit /b 1
)

echo.
echo ========================================================================
echo   COMPLETADO
echo ========================================================================
echo.
echo Archivos disponibles:
echo    - examples\nvidia_case_study.py (script Python)
echo    - examples\nvidia_analysis_storytelling.ipynb (Jupyter)
echo    - examples\nvidia_analysis.html (HTML para navegador)
echo.
echo Para mas informacion:
echo    - examples\COMO_VER_NOTEBOOK.md
echo    - examples\README_NOTEBOOKS.md
echo.
echo Disfruta del análisis!
echo.
pause
