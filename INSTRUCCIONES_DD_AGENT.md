# 🚀 Cómo Probar el DealRoom DD Agent

## 📋 Paso 1: Generar los PDFs de Prueba

Primero, vamos a crear un **data room ficticio** con documentación realista de una empresa SaaS llamada "TechFlow Solutions SL".

### 1.1 Instalar dependencia adicional

```bash
pip install reportlab
```

### 1.2 Ejecutar el generador de PDFs

```bash
cd /home/user/M-A
python generate_sample_dataroom.py
```

Esto creará una carpeta `sample_dataroom/` con 4 PDFs:

1. **Executive Summary** - Overview del negocio, posición competitiva, KPIs
2. **Financial Statements** - P&L y Balance Sheet 2022-2024
3. **Legal Due Diligence Report** - Estructura corporativa, IP, contratos, compliance
4. **Commercial Due Diligence** - Análisis de clientes, retention, competencia, TAM

---

## 🤖 Paso 2: Instalar Dependencias del DD Agent

```bash
pip install sentence-transformers openai pypdf numpy
```

O simplemente:

```bash
pip install -r requirements.txt
```

---

## 🎯 Paso 3: Ejecutar la Aplicación Streamlit

```bash
streamlit run app.py
```

Esto abrirá la app en tu navegador (normalmente `http://localhost:8501`).

---

## 🔑 Paso 4: Configurar el DD Agent

En la **barra lateral izquierda** del navegador:

### 4.1 Navegar a la página del DD Agent

- Verás que ahora aparece una nueva página: **"🤖 DealRoom DD Agent"**
- Haz click en ella para acceder

### 4.2 Introducir tu API Key de OpenAI

1. En la barra lateral, busca la sección **"🔑 OpenAI API Key"**
2. Introduce tu API key (la que dijiste que ya tienes)
3. El campo es tipo password (no se verá el texto por seguridad)

> **Nota**: La API key NO se guarda en ningún sitio, solo existe durante la sesión activa.

### 4.3 Subir los PDFs del Data Room

1. En la sección **"📁 Data Room"**, haz click en **"Browse files"**
2. Navega a la carpeta `sample_dataroom/`
3. Selecciona los 4 PDFs (puedes seleccionarlos todos a la vez con Ctrl/Cmd + Click)
4. Haz click en "Open"

Verás un mensaje: ✅ **"4 documento(s) cargado(s)"**

### 4.4 Seleccionar modo de análisis

En **"🎯 Modo de Análisis"**, elige uno de los 4 modos:

- **Summary** - Para resumen ejecutivo del target
- **Risks** - Para identificar red flags
- **Questions** - Para generar preguntas para management
- **Free question** - Para hacer tu propia pregunta

---

## 🧪 Paso 5: Probar los Diferentes Modos

### Test 1: Summary Mode

1. Selecciona **"Summary"** en el dropdown
2. Haz click en **"▶️ Run Due Diligence Agent"**
3. Espera ~20-30 segundos
4. Verás un resumen ejecutivo estructurado con:
   - Overview del negocio
   - Posición competitiva
   - KPIs financieros
   - Tendencias
   - Referencias [SOURCE 1], [SOURCE 2], etc.

5. Expande **"📚 Fuentes utilizadas"** para ver los fragmentos exactos de los PDFs que usó el agente

### Test 2: Risks Mode

1. Selecciona **"Risks"**
2. Haz click en **"▶️ Run Due Diligence Agent"**
3. Verás un análisis categorizado:
   - Riesgos financieros
   - Riesgos legales
   - Riesgos operativos
   - Riesgos comerciales
   - Red flags identificados

**Ejemplos de lo que debería encontrar:**
- Concentración de clientes (top 10 = 35% ARR)
- Cliente grande con cláusula de terminación sin causa
- Ausencia de retention agreements para key employees
- CAC creciente (+22% YoY)
- Churn alto en Basic tier (18%)

### Test 3: Questions Mode

1. Selecciona **"Questions"**
2. Haz click en **"▶️ Run Due Diligence Agent"**
3. Verás una lista priorizada de preguntas para el equipo directivo, organizadas por bloques:
   - Financiero
   - Operativo
   - Comercial
   - Legal/Contratos
   - ESG (si aplica)

**Ejemplos de preguntas que debería generar:**
- ¿Cuál es el plan de retención para el 2° cliente más grande (Logística del Sur)?
- ¿Cómo planean revertir el incremento del CAC?
- ¿Qué estrategia tienen para reducir churn en Basic tier?

### Test 4: Free Question Mode

1. Selecciona **"Free question"**
2. En el campo de texto que aparece, escribe una pregunta personalizada. **Ejemplos:**

   **Pregunta 1:**
   ```
   ¿Cuál es la estructura de costes de TechFlow y cómo ha evolucionado en los últimos 3 años?
   ```

   **Pregunta 2:**
   ```
   Analiza la dependencia de proveedores tecnológicos y el riesgo asociado.
   ```

   **Pregunta 3:**
   ```
   ¿Qué clientes representan el mayor riesgo de churn y por qué?
   ```

   **Pregunta 4:**
   ```
   Resume todos los problemas legales y de compliance identificados, priorizados por severidad.
   ```

3. Haz click en **"▶️ Run Due Diligence Agent"**
4. El agente responderá específicamente a tu pregunta basándose en la documentación

---

## 🎯 Qué Esperar en Cada Análisis

### ✅ Buenas Señales (el agente funciona bien si...)

1. **Cita fuentes específicas**: Ves referencias como `[SOURCE 3 | file=03_Legal_Due_Diligence_Report.pdf, page=2]`
2. **Respuestas contextualizadas**: La información viene de los PDFs, no de conocimiento general
3. **Estructura profesional**: Respuestas organizadas con headers, bullet points, priorización
4. **Identifica red flags reales**: Como el tema del cliente con cláusula de terminación, CAC creciente, etc.
5. **Admite limitaciones**: Si preguntaste algo que no está en los docs, debería decir "no hay suficiente información"

### ⚠️ Problemas Potenciales

| Problema | Causa Probable | Solución |
|----------|----------------|----------|
| "Error calling OpenAI API" | API key inválida o sin créditos | Verifica tu API key en OpenAI dashboard |
| "No se pudo extraer texto" | PDFs corruptos | Regenera los PDFs con el script |
| "No chunks relevantes" | Query muy específica para docs genéricos | Reformula la pregunta más amplia |
| Respuesta muy genérica | Chunking no capturó info relevante | Normal en algunos casos, refina la pregunta |

---

## 💡 Preguntas Sugeridas para Impresionar en Entrevistas

Cuando muestres el DD Agent en una entrevista, usa estas queries para demostrar capacidades:

### Para CFOs / Finance Teams:
```
Analiza la calidad de los ingresos recurrentes y la predictibilidad del cash flow.
```

### Para M&A Analysts:
```
¿Cuáles son los principales value drivers y deal breakers identificados en la documentación?
```

### Para Legal/Compliance:
```
Resume todos los riesgos regulatorios y de compliance, incluyendo GDPR y protección de datos.
```

### Para Commercial Teams:
```
Analiza la defensibilidad competitiva y el moat de TechFlow frente a players internacionales.
```

### Para Strategy:
```
¿Qué oportunidades de expansión y crecimiento inorgánico identificas en la documentación?
```

---

## 📊 Arquitectura Técnica (para explicar en entrevistas)

### Pipeline RAG en 6 pasos:

```
1. PDF Upload
   ↓
2. Text Extraction (PyPDF)
   - Página por página
   - ~900 chars/chunk con 100 overlap
   ↓
3. Embeddings (Sentence Transformers)
   - Modelo: all-MiniLM-L6-v2
   - Dimensión: 384
   ↓
4. Vector Search (Cosine Similarity)
   - Top-10 chunks más relevantes
   - Scores normalizados 0-1
   ↓
5. Prompt Construction
   - System: "Eres analista M&A senior..."
   - Context: [SOURCE n | metadata] + texto
   - Query: Modo específico o free question
   ↓
6. LLM Generation (GPT-4o-mini)
   - Temperature: 0.3 (balance precisión/creatividad)
   - Max tokens: 2000
   - Output: Análisis estructurado + referencias
```

### Métricas de Performance:

- **Latencia típica**: 20-30 segundos para 4 PDFs (~80 páginas)
  - Embedding: ~5 segundos
  - Búsqueda: <1 segundo
  - LLM: 15-20 segundos
- **Coste por query**: ~$0.01-0.03 (usando gpt-4o-mini)
- **Precisión**: High (porque solo usa contexto provisto, no alucina)

---

## 🎤 Cómo Presentar en Entrevista

### Script sugerido:

> *"Construí este DD Agent para automatizar el análisis preliminar de documentación en procesos de M&A.
> El sistema usa **RAG (Retrieval-Augmented Generation)** para combinar búsqueda semántica con LLMs.*
>
> *Déjame mostrarte cómo funciona: [subes los PDFs]*
>
> *Primero voy a ejecutar un análisis de riesgos... [ejecutas Risks mode]*
>
> *Como ves, identifica automáticamente red flags como:*
> - *Concentración de clientes*
> - *Problemas de compliance GDPR*
> - *Ausencia de retention para empleados clave*
>
> *Y lo mejor: cada afirmación está **citada con fuente exacta** [expandir Sources], lo cual es crítico
> para auditoría y transparencia en procesos reales de DD.*
>
> *También puedo hacer preguntas ad-hoc... [demostrar Free Question]*
>
> *Este sistema demuestra capacidades end-to-end:*
> - *Ingeniería de datos (extracción, chunking, embeddings)*
> - *Machine Learning (vector search, similarity)*
> - *Prompt Engineering (system prompts especializados)*
> - *Product thinking (UX, validaciones, error handling)*
>
> *Y todo construido en ~500 líneas de Python modular y testeable."*

---

## 🐛 Troubleshooting

### Problema: "Module 'pypdf' not found"

**Solución:**
```bash
pip install pypdf
# O alternativamente:
pip install PyPDF2
```

### Problema: "Sentence transformers downloading model..."

**Explicación:** La primera vez que ejecutes el DD Agent, descargará el modelo `all-MiniLM-L6-v2` (~80MB). Esto solo pasa una vez.

**Tip para entrevistas:** Ejecuta el agente UNA VEZ antes de la demo para que el modelo ya esté cached.

### Problema: OpenAI API muy lenta (>60 segundos)

**Posibles causas:**
- Rate limits en tu API key
- Usar GPT-4 en lugar de gpt-4o-mini

**Solución:** En el código (`pages/1_🤖_DealRoom_DD_Agent.py`), busca la función `call_llm()` y verifica que `model="gpt-4o-mini"` (no gpt-4 completo).

---

## 📈 Próximos Pasos (Mejoras que Puedes Mencionar)

Cuando te pregunten "¿Cómo mejorarías esto?", menciona:

1. **Persistencia**: Integrar Chroma/Pinecone para no recalcular embeddings
2. **Multi-formato**: Soportar Word, Excel, PowerPoint
3. **Comparative analysis**: Comparar múltiples targets side-by-side
4. **Auto-extraction**: Extraer KPIs automáticamente (revenue, margins, etc.) y crear dashboard
5. **Collaborative**: Multi-user con comentarios y anotaciones
6. **Export**: Generar reportes en PDF/Word con el análisis
7. **Evaluation**: A/B testing de diferentes prompts y modelos de embedding

---

## ✅ Checklist Pre-Demo (Entrevista)

- [ ] PDFs generados en `sample_dataroom/`
- [ ] Dependencias instaladas (`pip install -r requirements.txt`)
- [ ] Modelo de embeddings ya descargado (ejecutar el agente 1 vez antes)
- [ ] API key de OpenAI válida y con créditos
- [ ] Internet estable (para llamadas a OpenAI API)
- [ ] Streamlit funcionando (`streamlit run app.py`)
- [ ] Has probado los 4 modos al menos una vez
- [ ] Conoces bien la arquitectura técnica (ver diagrama arriba)
- [ ] Tienes preparadas 2-3 preguntas "wow" para demostrar

---

## 🎯 Resultados Esperados

Al final de la demo, deberías poder demostrar:

✅ **Technical Skills:**
- RAG pipeline completo
- Vector search
- Prompt engineering
- Error handling robusto

✅ **Domain Knowledge:**
- Terminología M&A (ARR, NRR, CAC, LTV, red flags, DD)
- Comprensión de documentación de data rooms
- Qué preguntas importan en cada fase de DD

✅ **Product Thinking:**
- UX intuitiva
- Validaciones claras
- Trazabilidad de fuentes
- Workflow estructurado (4 modos)

✅ **Software Engineering:**
- Código limpio y modular
- Funciones reutilizables
- Caching apropiado
- Documentación clara

---

**¡Buena suerte con las demos! 🚀**

Si tienes algún problema, revisa los logs de Streamlit en la consola o el troubleshooting de arriba.
