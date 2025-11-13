# 🚀 Cómo Ejecutar el Análisis de Nvidia en Local

Esta guía te muestra cómo ejecutar el análisis completo de Nvidia en tu computadora local.

---

## ⚡ Método Rápido (Recomendado)

### **Linux / Mac:**
```bash
bash run_nvidia_analysis.sh
```

### **Windows:**
```cmd
run_nvidia_analysis.bat
```

El script automáticamente:
1. ✅ Verifica Python
2. ✅ Crea entorno virtual
3. ✅ Instala todas las dependencias
4. ✅ Te pregunta qué quieres ejecutar

---

## 📋 Requisitos Previos

### **1. Python 3.8 o superior**

Verifica tu versión:
```bash
python --version
# o
python3 --version
```

**Si no tienes Python:**
- **Windows:** Descarga desde [python.org](https://www.python.org/downloads/)
- **Mac:** `brew install python3` o desde python.org
- **Linux:** `sudo apt install python3 python3-pip` (Ubuntu/Debian)

### **2. pip (instalador de paquetes)**

Normalmente viene con Python. Verifica:
```bash
pip --version
```

---

## 🛠️ Instalación Manual (Paso a Paso)

Si prefieres hacerlo manualmente o si el script automático falla:

### **Paso 1: Clonar/Descargar el repositorio**
```bash
git clone <url-del-repo>
cd M-A
```

### **Paso 2: Crear entorno virtual (Recomendado)**

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

### **Paso 3: Instalar dependencias**
```bash
pip install -r requirements.txt
```

O instalar manualmente:
```bash
pip install numpy scipy pandas matplotlib seaborn jupyter
```

### **Paso 4: Verificar instalación**
```bash
python -c "import numpy, pandas, matplotlib, seaborn; print('✅ Todo OK')"
```

---

## 🎯 Formas de Ejecutar el Análisis

### **Opción 1: Script Python (Terminal)** 📜

Ejecuta el análisis completo en terminal:

```bash
python examples/nvidia_case_study.py
```

**Output:**
- ~1,100 líneas de análisis en texto
- Todas las 8 herramientas aplicadas
- Resultados numéricos completos
- Recomendación de inversión

**Tiempo:** ~30 segundos

**Guardar output:**
```bash
python examples/nvidia_case_study.py > mi_analisis.txt
```

---

### **Opción 2: Jupyter Notebook (Interactivo)** 📓⭐

La mejor opción si quieres ver gráficas y modificar assumptions:

```bash
jupyter notebook examples/nvidia_analysis_storytelling.ipynb
```

**Se abre en tu navegador con:**
- ✅ 8 gráficas profesionales pre-renderizadas
- ✅ Código editable
- ✅ Formato storytelling
- ✅ Explicaciones detalladas

**Para modificar:**
1. Cambia valores en las celdas
2. Ejecuta la celda (Shift + Enter)
3. Ve los resultados actualizados

---

### **Opción 3: HTML (Solo Ver)** 🌐

Si solo quieres ver el análisis sin instalar Jupyter:

**Opción A - Ya generado:**
```bash
# Abre en navegador
open examples/nvidia_analysis.html  # Mac
start examples/nvidia_analysis.html  # Windows
xdg-open examples/nvidia_analysis.html  # Linux
```

**Opción B - Generar nuevo:**
```bash
jupyter nbconvert --to html examples/nvidia_analysis_storytelling.ipynb
```

---

### **Opción 4: VS Code (Desarrollo)** 💻

Si usas VS Code:

1. Instala extensión "Jupyter" (Microsoft)
2. Abre `examples/nvidia_analysis_storytelling.ipynb`
3. Las gráficas se muestran automáticamente
4. Puedes ejecutar celda por celda

---

## 🎨 Personalizar el Análisis

### **Cambiar la empresa analizada:**

Edita `nvidia_case_study.py` o el notebook y cambia los datos:

```python
# En lugar de Nvidia
target_revenue = 60000  # Cambia por tu empresa
target_ebitda = 35000   # Cambia por tu empresa
target_net_income = 30000

# Cambiar comparables
multiples.add_comparable(
    name="Tu Competidor",
    enterprise_value=XXX,
    revenue=YYY,
    ebitda=ZZZ
)

# Cambiar assumptions DCF
wacc = 0.10  # Tu WACC
terminal_growth_rate = 0.03  # Tu growth rate
```

### **Modificar gráficas:**

En el notebook, cambia configuración de matplotlib:

```python
plt.figure(figsize=(14, 6))  # Tamaño
plt.style.use('seaborn-v0_8')  # Estilo
colors = ['red', 'blue', 'green']  # Colores
```

---

## 🐛 Solución de Problemas

### **Error: "ModuleNotFoundError: No module named 'numpy'"**

**Solución:**
```bash
pip install numpy scipy pandas matplotlib seaborn
```

### **Error: "command not found: jupyter"**

**Solución:**
```bash
pip install jupyter
```

### **Las gráficas no se ven en Jupyter**

**Solución:** Añade al inicio del notebook:
```python
%matplotlib inline
```

### **Error de permisos en Windows**

**Solución:** Ejecuta PowerShell/CMD como **Administrador**

### **Python 2.7 en lugar de Python 3**

**Solución:** Usa `python3` en lugar de `python`:
```bash
python3 examples/nvidia_case_study.py
```

### **Entorno virtual no se activa**

**Mac/Linux:**
```bash
source venv/bin/activate
```

**Windows CMD:**
```cmd
venv\Scripts\activate.bat
```

**Windows PowerShell:**
```powershell
venv\Scripts\Activate.ps1
```

Si da error de política de ejecución:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 📊 Qué Obtendrás

Al ejecutar el análisis completo verás:

### **1. Overview de Nvidia**
- Revenue mix: Data Center 55%, Gaming 45%
- Márgenes: 58% EBITDA (líder industria)
- Market cap $3T

### **2. DCF Valuation**
- Gordon Growth: $36/share
- Exit Multiple: $49/share
- Sensitivity analysis: Matriz WACC vs Terminal Growth

### **3. Trading Comparables**
- 5 peers: AMD, Intel, Qualcomm, Broadcom, TSMC
- EV/EBITDA: 84x (Nvidia) vs 14x (median peers)
- Premium justification analysis

### **4. Synergies Model**
- Escenario: Adquisición $15B
- Cost synergies: $520M run-rate
- Revenue synergies: $629M EBITDA
- NPV de sinergias: $7.1B

### **5. Financial Ratios**
- ROE: 71% (exceptional)
- EBITDA margin: 58%
- Net cash: $17B
- Crecimiento: 122% YoY

### **6. Due Diligence**
- Red flags: 0 (clean profile)
- Cash flow quality: Excellent
- EBITDA normalization

### **7. Integration Case (Mellanox)**
- ROI: 71% en 2 años
- Sinergias exceeded targets
- Value created: $5B

### **8. Recomendación Final**
- **RATING: HOLD/TRIM**
- Price targets: Bear $90 / Base $105 / Bull $150
- Veredicto: Empresa perfecta, precio extremo

---

## 📦 Estructura de Archivos

```
M-A/
├── run_nvidia_analysis.sh        # Script Linux/Mac
├── run_nvidia_analysis.bat       # Script Windows
├── requirements.txt              # Dependencias Python
├── examples/
│   ├── nvidia_case_study.py                      # Script Python
│   ├── nvidia_analysis_storytelling.ipynb        # Jupyter notebook
│   ├── nvidia_analysis.html                      # HTML pre-generado
│   ├── COMO_VER_NOTEBOOK.md                      # Guía visualización
│   └── README_NOTEBOOKS.md                       # Docs notebooks
├── models/                       # Modelos de valoración
│   ├── dcf.py
│   ├── multiples.py
│   ├── lbo.py
│   └── ...
└── analysis/                     # Análisis financiero
    ├── financial_ratios.py
    └── due_diligence.py
```

---

## ⏱️ Tiempos de Ejecución

- **Script Python:** ~30 segundos
- **Jupyter Notebook:** ~1 minuto (primera vez)
- **Generar HTML:** ~30 segundos
- **Instalación inicial:** ~2-3 minutos

---

## 💡 Tips y Trucos

### **1. Ejecutar en background (Linux/Mac)**
```bash
nohup python examples/nvidia_case_study.py > analisis.txt 2>&1 &
```

### **2. Comparar múltiples escenarios**
```bash
# Guardar diferentes versiones
python examples/nvidia_case_study.py > nvidia_conservador.txt
# Edita assumptions
python examples/nvidia_case_study.py > nvidia_optimista.txt
```

### **3. Exportar notebook a PDF**
```bash
jupyter nbconvert --to pdf examples/nvidia_analysis_storytelling.ipynb
```

### **4. Exportar notebook a slides**
```bash
jupyter nbconvert --to slides examples/nvidia_analysis_storytelling.ipynb
```

### **5. Ejecutar desde cualquier carpeta**
```bash
export PYTHONPATH=$PYTHONPATH:/ruta/a/M-A
python -m examples.nvidia_case_study
```

---

## 🎓 Próximos Pasos

Después de ejecutar el análisis:

1. **Estudia los resultados** - Lee el output completo
2. **Experimenta** - Cambia assumptions en el notebook
3. **Compara** - Analiza otras empresas usando las mismas herramientas
4. **Aprende** - Estudia el código de los modelos en `/models`
5. **Comparte** - Muestra el análisis a colegas

---

## 📚 Recursos Adicionales

- `QUICKSTART.md` - Inicio rápido de las herramientas
- `examples/README_NOTEBOOKS.md` - Docs completas de notebooks
- `examples/COMO_VER_NOTEBOOK.md` - 7 formas de ver notebooks

---

## 🆘 Soporte

Si tienes problemas:

1. **Revisa** esta guía completa
2. **Verifica** versión de Python (`python --version`)
3. **Reinstala** dependencias (`pip install -r requirements.txt`)
4. **Abre** un issue en GitHub con detalles del error

---

## ✅ Checklist de Verificación

Antes de ejecutar, asegúrate de:

- [ ] Python 3.8+ instalado
- [ ] pip funcionando
- [ ] Todas las dependencias instaladas
- [ ] Dentro de la carpeta M-A
- [ ] (Opcional) Entorno virtual activado

---

**¡Listo! Ahora tienes todo para ejecutar el análisis profesional de Nvidia en tu máquina local.** 🚀

¿Preguntas? Revisa la sección de troubleshooting o abre un issue.
