# Cómo Ejecutar el Caso de Nvidia en Local

## Problema Común: Error de Imports

Si ves este error:
```
ModuleNotFoundError: No module named 'models'
```

Es porque Python no encuentra las carpetas `models/` y `analysis/`.

---

## ✅ SOLUCIÓN 1: Ejecutar desde la raíz del proyecto (RECOMENDADO)

```bash
# 1. Asegúrate de estar en el directorio M-A (raíz del proyecto)
cd M-A

# 2. Verifica que estás en el lugar correcto
ls
# Deberías ver: models/, analysis/, examples/, utils/

# 3. Ejecuta el script
python examples/nvidia_case_study.py
```

**¿Por qué funciona?**
- El script hace `sys.path.append(str(Path(__file__).parent.parent))`
- Esto añade el directorio padre de `examples/` (que es `M-A/`) al path de Python
- Python entonces encuentra `models/` y `analysis/`

---

## ✅ SOLUCIÓN 2: Usar la versión standalone (SIN dependencias de paths)

```bash
# 1. Ve a la carpeta examples
cd M-A/examples

# 2. Ejecuta la versión standalone
python nvidia_standalone.py
```

**Ventaja:** No necesita imports de `models/`, todo está en un solo archivo.

---

## ✅ SOLUCIÓN 3: Instalar como paquete (Avanzado)

```bash
# Desde el directorio M-A/
pip install -e .
```

Esto instala el paquete en modo desarrollo y los imports funcionarán desde cualquier lugar.

---

## 🧪 Verificar tu setup

Ejecuta este comando para verificar:

```bash
cd M-A
python -c "import sys; from pathlib import Path; sys.path.insert(0, '.'); from models.dcf import DCFModel; print('✅ Imports funcionan correctamente')"
```

Si ves "✅ Imports funcionan correctamente", estás listo.

---

## 📋 Comandos Paso a Paso

### Opción A: Análisis Completo (8 modelos)

```bash
# Prerequisito: Instalar dependencias
pip install numpy scipy pandas matplotlib seaborn

# Ejecutar desde raíz
cd /ruta/a/M-A
python examples/nvidia_case_study.py
```

### Opción B: Versión Simple (standalone)

```bash
# Prerequisito: Instalar solo 4 librerías
pip install numpy pandas matplotlib seaborn

# Ejecutar desde examples/
cd /ruta/a/M-A/examples
python nvidia_standalone.py
```

---

## 🆘 Errores Comunes

### Error: `ModuleNotFoundError: No module named 'numpy'`
**Solución:**
```bash
pip install numpy scipy pandas matplotlib seaborn
```

### Error: `ModuleNotFoundError: No module named 'models'`
**Solución:**
```bash
# Asegúrate de estar en el directorio correcto
cd M-A  # (la raíz, NO en examples/)
python examples/nvidia_case_study.py
```

### Error: `No such file or directory: 'examples/nvidia_case_study.py'`
**Solución:**
```bash
# Estás en el directorio equivocado. Ve a la raíz:
cd ..
python examples/nvidia_case_study.py
```

---

## 🎯 Estructura de Directorios Esperada

```
M-A/                          ← DEBES ESTAR AQUÍ para ejecutar
├── models/                   ← Python busca aquí
│   ├── dcf.py
│   ├── multiples.py
│   └── ...
├── analysis/                 ← Python busca aquí
│   ├── financial_ratios.py
│   └── due_diligence.py
├── examples/
│   ├── nvidia_case_study.py      ← Script completo
│   └── nvidia_standalone.py      ← Script independiente
└── requirements.txt
```

---

## ✅ Checklist de Verificación

- [ ] Estoy en el directorio `M-A/` (raíz)
- [ ] Ejecuté `ls` y veo las carpetas `models/`, `analysis/`, `examples/`
- [ ] Instalé las dependencias: `pip install -r requirements.txt`
- [ ] Ejecuto: `python examples/nvidia_case_study.py`

---

## 🚀 Comando Final (Todo en uno)

```bash
# Linux/Mac
cd M-A && pip install -r requirements.txt && python examples/nvidia_case_study.py

# Windows
cd M-A
pip install -r requirements.txt
python examples\nvidia_case_study.py
```

---

Si aún tienes problemas, usa **nvidia_standalone.py** que no tiene dependencias de paths.
