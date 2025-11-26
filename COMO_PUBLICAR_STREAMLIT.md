# 🎯 CÓMO PUBLICAR EN STREAMLIT - GUÍA SIMPLE

## ❌ Tu Error Anterior

Intentaste subir el archivo **`main.py`** (que es de FastAPI) a Streamlit.

**Problema:** Streamlit necesita un archivo Streamlit, no un archivo FastAPI.

**Solución:** Ya te creé el archivo correcto → `streamlit_app.py`

---

## ✅ PASOS PARA PUBLICAR (Super Simple)

### PASO 1: Subir archivos a GitHub

```bash
cd /home/user/M-A

# Agregar los nuevos archivos
git add streamlit_app.py
git add requirements_streamlit.txt
git add .streamlit/
git add STREAMLIT_DEPLOYMENT.md

# Hacer commit
git commit -m "Add Streamlit app for Financial RAG Agent"

# Subir a GitHub
git push
```

### PASO 2: Ir a Streamlit Cloud

1. Abre tu navegador
2. Ve a: **https://share.streamlit.io/**
3. Inicia sesión con GitHub

### PASO 3: Crear Nueva App

1. Click en **"New app"** (botón azul)

2. Llena el formulario:
   - **Repository:** `Bernalsoro/M-A`
   - **Branch:** `main` (o la que uses)
   - **Main file path:** `streamlit_app.py`
   - **App URL:** (elige un nombre, ej: `financial-rag-agent`)

3. Click en **"Deploy"** (botón rojo)

### PASO 4: Esperar

- Primera vez tarda 2-3 minutos
- Verás logs instalando cosas
- Cuando termine, verás tu app funcionando 🎉

---

## 🎨 Cómo Se Ve Tu App

```
┌─────────────────────────────────────────────────┐
│  📊 Financial RAG Agent                         │
│  AI-Powered Financial Analysis                  │
├─────────────────────────────────────────────────┤
│                                                 │
│  Sidebar:                    Main Area:         │
│  ┌──────────────┐           ┌───────────────┐  │
│  │ ⚙️ Config    │           │ 🤔 Ask        │  │
│  │              │           │    Question   │  │
│  │ Select:      │           │               │  │
│  │ • AAPL       │           │ [Text box]    │  │
│  │              │           │               │  │
│  │ 💡 Examples: │           │ [🚀 Ask]      │  │
│  │ • Compare... │           │               │  │
│  │ • Analyze... │           │ Answer here..  │  │
│  │              │           │               │  │
│  └──────────────┘           └───────────────┘  │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## 🔧 Si Te Sale Error

### Error: "ModuleNotFoundError"
**Solución:** Asegúrate que subiste la carpeta `financial-rag-agent/src/` completa

### Error: "No file found"
**Solución:** En Streamlit Cloud, verifica que el path sea exactamente `streamlit_app.py`

### Error: "Memory exceeded"
**Solución:** Espera que cargue completamente, es normal la primera vez

---

## ⚙️ Archivos Importantes

Estos son los archivos que DEBES tener en tu repo:

```
M-A/
├── streamlit_app.py              ✅ (YA CREADO)
├── requirements_streamlit.txt    ✅ (YA CREADO)
├── .streamlit/
│   └── config.toml              ✅ (YA CREADO)
└── financial-rag-agent/
    └── src/
        └── financial_rag_agent/
            ├── data/
            │   ├── sample_financials.csv  ✅
            │   └── sample_news.json       ✅
            └── [resto de carpetas]        ✅
```

---

## 📝 Diferencias: FastAPI vs Streamlit

| Aspecto | FastAPI (main.py) | Streamlit (streamlit_app.py) |
|---------|-------------------|------------------------------|
| **Qué es** | API REST (backend) | Web app con interfaz gráfica |
| **Cómo se ve** | JSON (sin interfaz) | Página web bonita |
| **Dónde publicar** | Heroku, Railway, AWS | Streamlit Cloud |
| **Para qué** | Otros programas lo usen | Personas lo usen |

**Analogía:**
- FastAPI = El motor de un carro (no lo ves, pero funciona)
- Streamlit = El carro completo con volante y asientos (lo usas directamente)

---

## 🎯 Resumen en 3 Líneas

1. **Ya tienes el archivo correcto:** `streamlit_app.py`
2. **Súbelo a GitHub:** `git add streamlit_app.py && git commit && git push`
3. **Publica en:** https://share.streamlit.io/ → New app → `streamlit_app.py`

---

## 🚨 MUY IMPORTANTE

**NO subas el archivo `main.py` a Streamlit Cloud**

- `main.py` = FastAPI (para APIs)
- `streamlit_app.py` = Streamlit (para web apps)

Son cosas diferentes.

---

## ✅ Checklist Antes de Publicar

Verifica que hiciste esto:

```bash
# 1. ¿Están los archivos en tu repo?
git status
# Debes ver: streamlit_app.py

# 2. ¿Los subiste a GitHub?
git push
# Debe decir: "Everything up-to-date" o "Branch updated"

# 3. ¿Existe la carpeta de datos?
ls financial-rag-agent/src/financial_rag_agent/data/
# Debes ver: sample_financials.csv, sample_news.json
```

Si todo está ✅, estás listo para publicar.

---

## 🎉 Después de Publicar

Tu app estará en:
```
https://[tu-nombre-app].streamlit.app
```

Podrás:
- Compartir el link con cualquiera
- Hacer preguntas sobre finanzas
- Ver cómo el agente trabaja
- Mostrar en entrevistas

---

## 💡 Tip Pro

Si quieres respuestas REALES de IA (no mock):

1. En Streamlit Cloud, click en tu app
2. Click "⚙️ Settings"
3. Click "Secrets"
4. Agrega:
```toml
OPENAI_API_KEY = "sk-..."
LLM_PROVIDER = "openai"
```

**Sin esto:** La app funciona pero con respuestas inventadas
**Con esto:** Respuestas reales de ChatGPT

---

## ❓ ¿Necesitas Ayuda?

Si algo no funciona:
1. Lee los logs en Streamlit Cloud (botón "Manage app")
2. Revisa que todos los archivos estén en GitHub
3. Verifica que el path sea exactamente `streamlit_app.py`

¡Listo! 🚀
