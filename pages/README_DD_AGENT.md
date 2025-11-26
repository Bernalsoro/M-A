# 🤖 DealRoom DD Agent – AI Due Diligence Assistant

## 📋 Descripción

Herramienta de análisis de Due Diligence basada en IA que utiliza **RAG (Retrieval-Augmented Generation)** para analizar documentación de targets en procesos de M&A.

## 🎯 Funcionalidades

### Modos de Análisis

1. **Summary** - Resumen ejecutivo del target
   - Modelo de negocio y posición competitiva
   - KPIs financieros principales
   - Tendencias recientes

2. **Risks** - Mapa de riesgos y red flags
   - Riesgos financieros
   - Riesgos legales
   - Riesgos operativos
   - Aspectos ESG

3. **Questions** - Lista de preguntas para management
   - Preguntas financieras
   - Preguntas operativas
   - Preguntas comerciales
   - Preguntas legales/contratos
   - Preguntas ESG

4. **Free Question** - Pregunta personalizada
   - Análisis ad-hoc sobre la documentación

## 🛠️ Tecnologías

- **Streamlit**: Interfaz web interactiva
- **Sentence Transformers**: Embeddings semánticos (all-MiniLM-L6-v2)
- **OpenAI GPT**: Generación de análisis contextualizado
- **PyPDF**: Extracción de texto de documentos PDF
- **NumPy**: Cálculos de similitud coseno

## 📦 Instalación

```bash
pip install streamlit sentence-transformers openai pypdf numpy
```

O usando el requirements.txt del proyecto:

```bash
pip install -r requirements.txt
```

## 🚀 Uso

### 1. Iniciar la aplicación

```bash
streamlit run app.py
```

Luego navega a la página "🤖 DealRoom DD Agent" desde la barra lateral.

### 2. Configurar

1. **API Key**: Introduce tu OpenAI API key en la barra lateral
2. **Data Room**: Sube uno o varios PDFs con documentación del target
3. **Modo**: Selecciona el tipo de análisis deseado

### 3. Ejecutar análisis

1. Si seleccionaste "Free Question", escribe tu pregunta
2. Haz clic en "▶️ Run Due Diligence Agent"
3. Espera a que el agente procese los documentos y genere el análisis

### 4. Revisar resultados

- **Análisis**: Respuesta estructurada con referencias a fuentes [SOURCE n]
- **Fuentes**: Expandir para ver los fragmentos exactos utilizados del data room

## 🏗️ Arquitectura

### Pipeline RAG

```
PDFs → Extracción → Chunking → Embeddings → Vector Search → LLM → Análisis
```

### Componentes principales

1. **Extracción de PDF** (`extract_chunks_from_pdfs`)
   - Lee PDFs página por página
   - Divide en chunks de ~900 caracteres con overlap de 100

2. **Embeddings** (`build_embeddings_index`)
   - Genera vectores semánticos con Sentence Transformers
   - Cached para evitar recálculos innecesarios

3. **Búsqueda** (`retrieve_relevant_chunks`)
   - Similitud coseno entre query y chunks
   - Retorna top-10 más relevantes

4. **Generación** (`call_llm`)
   - Construye prompts especializados para M&A Due Diligence
   - Llama a OpenAI GPT-4o-mini
   - Retorna análisis estructurado con referencias

## 💡 Casos de Uso

### Para entrevistas de M&A

Demuestra capacidades técnicas end-to-end:
- ✅ Ingeniería de datos (extracción, chunking)
- ✅ Machine Learning (embeddings, búsqueda vectorial)
- ✅ Prompt Engineering (system prompts especializados)
- ✅ Integración de APIs (OpenAI)
- ✅ UX/UI (Streamlit, validaciones)

### Workflow típico

1. Analista sube deck del target, estados financieros y contratos
2. Ejecuta "Summary" para contexto inicial
3. Ejecuta "Risks" para identificar red flags
4. Ejecuta "Questions" para preparar reunión con management
5. Usa "Free Question" para deep-dives específicos

## ⚙️ Configuración avanzada

### Parámetros de chunking

En `extract_chunks_from_pdfs`:
- `chunk_size=900`: Tamaño de cada chunk
- `overlap=100`: Overlap entre chunks

### Parámetros de búsqueda

En `retrieve_relevant_chunks`:
- `top_k=10`: Número de chunks a recuperar

### Modelo LLM

En `call_llm`:
- `model="gpt-4o-mini"`: Modelo de OpenAI
- `temperature=0.3`: Balance creatividad/precisión
- `max_tokens=2000`: Longitud máxima de respuesta

## 🔐 Seguridad

- ✅ API key no se almacena (solo en sesión)
- ✅ Documentos procesados en memoria (no persisten)
- ✅ Sin acceso a internet para los PDFs
- ✅ Validaciones de entrada

## 🐛 Troubleshooting

### "No se pudo extraer texto"
- Verifica que el PDF contenga texto seleccionable (no escaneos)
- Intenta con un PDF diferente

### "Error calling OpenAI API"
- Verifica que tu API key sea válida
- Verifica que tengas créditos disponibles
- Revisa tu conexión a internet

### "No se encontraron chunks relevantes"
- Reformula la pregunta con más contexto
- Sube documentos más relevantes para la query

## 📈 Mejoras futuras

- [ ] Soporte para más formatos (Word, Excel)
- [ ] Integración con Chroma/Pinecone para persistencia
- [ ] Multi-idioma (detección automática)
- [ ] Export de análisis a PDF/Word
- [ ] Comparación de múltiples targets
- [ ] Dashboard de KPIs extraídos automáticamente

## 📄 Licencia

Proyecto educativo para portfolio de M&A.

---

**Autor**: [Tu nombre]
**Contacto**: [Tu email/LinkedIn]
**Fecha**: Noviembre 2025
