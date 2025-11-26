# Dependencies:
# pip install streamlit sentence-transformers openai pypdf numpy

import streamlit as st
import io
import numpy as np
from typing import List, Dict, Tuple
from dataclasses import dataclass

# PDF extraction
try:
    from pypdf import PdfReader
except ImportError:
    from PyPDF2 import PdfReader

# Embeddings
from sentence_transformers import SentenceTransformer

# OpenAI
from openai import OpenAI


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class DocumentChunk:
    """Represents a chunk of text from a document with metadata."""
    text: str
    file_name: str
    page_num: int
    chunk_id: int


# ============================================================================
# PDF EXTRACTION
# ============================================================================

def extract_chunks_from_pdfs(uploaded_files, chunk_size: int = 900, overlap: int = 100) -> List[DocumentChunk]:
    """
    Extract text from uploaded PDFs and split into overlapping chunks.

    Args:
        uploaded_files: List of Streamlit UploadedFile objects
        chunk_size: Target size for each chunk in characters
        overlap: Number of characters to overlap between chunks

    Returns:
        List of DocumentChunk objects
    """
    all_chunks = []

    for uploaded_file in uploaded_files:
        try:
            # Read PDF
            pdf_reader = PdfReader(io.BytesIO(uploaded_file.read()))

            # Process each page
            for page_num, page in enumerate(pdf_reader.pages, start=1):
                text = page.extract_text()
                if not text.strip():
                    continue

                # Split into chunks with overlap
                chunks = _split_text_with_overlap(text, chunk_size, overlap)

                # Create DocumentChunk objects
                for i, chunk_text in enumerate(chunks):
                    chunk = DocumentChunk(
                        text=chunk_text,
                        file_name=uploaded_file.name,
                        page_num=page_num,
                        chunk_id=len(all_chunks)
                    )
                    all_chunks.append(chunk)

        except Exception as e:
            st.error(f"Error processing {uploaded_file.name}: {str(e)}")
            continue

    return all_chunks


def _split_text_with_overlap(text: str, chunk_size: int, overlap: int) -> List[str]:
    """Split text into overlapping chunks."""
    chunks = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = start + chunk_size
        chunk = text[start:end]

        if chunk.strip():
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


# ============================================================================
# EMBEDDINGS & RETRIEVAL
# ============================================================================

@st.cache_resource
def load_embedding_model():
    """Load the sentence transformer model (cached)."""
    return SentenceTransformer('all-MiniLM-L6-v2')


def build_embeddings_index(chunks: List[DocumentChunk]) -> Tuple[np.ndarray, List[DocumentChunk]]:
    """
    Build embeddings for all chunks.

    Returns:
        Tuple of (embeddings_matrix, chunks_list)
    """
    if not chunks:
        return np.array([]), []

    model = load_embedding_model()
    texts = [chunk.text for chunk in chunks]

    with st.spinner("🔄 Generating embeddings for document chunks..."):
        embeddings = model.encode(texts, show_progress_bar=False)

    return embeddings, chunks


def retrieve_relevant_chunks(
    query: str,
    embeddings: np.ndarray,
    chunks: List[DocumentChunk],
    top_k: int = 10
) -> List[Tuple[DocumentChunk, float]]:
    """
    Retrieve top_k most relevant chunks for a query using cosine similarity.

    Returns:
        List of (chunk, similarity_score) tuples, sorted by relevance
    """
    if len(chunks) == 0:
        return []

    model = load_embedding_model()
    query_embedding = model.encode([query])[0]

    # Compute cosine similarity
    similarities = np.dot(embeddings, query_embedding) / (
        np.linalg.norm(embeddings, axis=1) * np.linalg.norm(query_embedding)
    )

    # Get top_k indices
    top_indices = np.argsort(similarities)[::-1][:top_k]

    results = [(chunks[i], similarities[i]) for i in top_indices]
    return results


# ============================================================================
# PROMPTS
# ============================================================================

def get_mode_query(mode: str, custom_question: str = "") -> str:
    """Get the query string based on the selected mode."""
    queries = {
        "Summary": (
            "Resume el negocio del target, su posición competitiva, principales KPIs "
            "financieros y tendencias recientes. Estructura la respuesta como un resumen "
            "ejecutivo de Due Diligence (M&A)."
        ),
        "Risks": (
            "Identifica los principales riesgos y red flags del target en términos "
            "financieros, legales, operativos y ESG. Estructura la respuesta por categoría."
        ),
        "Questions": (
            "A partir de la documentación, genera una lista priorizada de preguntas para "
            "el equipo directivo que deberíamos hacer en una reunión de Due Diligence. "
            "Divide en bloques: financiero, operativo, comercial, legal/contratos, ESG."
        ),
        "Free question": custom_question
    }
    return queries.get(mode, "")


def build_system_and_user_prompts(
    mode: str,
    question: str,
    retrieved_chunks: List[Tuple[DocumentChunk, float]]
) -> Tuple[str, str]:
    """
    Build system and user prompts for the LLM.

    Args:
        mode: Analysis mode
        question: User query
        retrieved_chunks: List of (chunk, score) tuples

    Returns:
        Tuple of (system_prompt, user_prompt)
    """
    # System prompt
    system_prompt = """Eres un analista senior de M&A especializado en Due Diligence.

Tu rol:
- Analizar documentación de targets (empresas objetivo de adquisición)
- Identificar oportunidades, riesgos y red flags
- Proporcionar insights accionables para el proceso de M&A

Instrucciones:
- Usa EXCLUSIVAMENTE la información del contexto proporcionado
- Si no tienes información suficiente sobre algo, indícalo claramente
- Cita las fuentes usando [SOURCE n] en tu respuesta
- Estructura tu análisis de forma clara y profesional

Formato de respuesta:
1. **Resumen Ejecutivo**: Síntesis de hallazgos principales
2. **Análisis Detallado**: Evidencia clave con referencias [SOURCE n]
3. **Riesgos / Red Flags**: Puntos de atención identificados
4. **Mitigantes Potenciales**: Posibles estrategias de mitigación
5. **Preguntas Recomendadas**: Áreas que requieren profundización"""

    # Build context from retrieved chunks
    context_parts = []
    for i, (chunk, score) in enumerate(retrieved_chunks, start=1):
        source_header = f"[SOURCE {i} | file={chunk.file_name}, page={chunk.page_num}]"
        context_parts.append(f"{source_header}\n{chunk.text}\n")

    context = "\n---\n".join(context_parts)

    # User prompt
    user_prompt = f"""**CONTEXTO DEL DATA ROOM:**

{context}

---

**ANÁLISIS SOLICITADO:**
{question}

Por favor, proporciona un análisis estructurado basándote ÚNICAMENTE en la información anterior.
Cita las fuentes relevantes usando [SOURCE n] en tu respuesta."""

    return system_prompt, user_prompt


# ============================================================================
# LLM INTEGRATION
# ============================================================================

def call_llm(
    system_prompt: str,
    user_prompt: str,
    openai_api_key: str,
    model: str = "gpt-4o-mini"
) -> str:
    """
    Call OpenAI API with the given prompts.

    Args:
        system_prompt: System instructions for the model
        user_prompt: User query with context
        openai_api_key: OpenAI API key
        model: Model to use (default: gpt-4o-mini)

    Returns:
        Model response text
    """
    try:
        client = OpenAI(api_key=openai_api_key)

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=2000
        )

        return response.choices[0].message.content

    except Exception as e:
        raise Exception(f"Error calling OpenAI API: {str(e)}")


# ============================================================================
# STREAMLIT APP
# ============================================================================

def main():
    st.set_page_config(
        page_title="DealRoom DD Agent",
        page_icon="🤖",
        layout="wide"
    )

    # ========================================================================
    # HEADER
    # ========================================================================

    st.title("🤖 DealRoom DD Agent – AI Due Diligence Assistant")

    st.markdown("""
    Este agente de IA te ayuda a realizar análisis preliminares de Due Diligence sobre empresas objetivo (targets)
    en procesos de M&A. **Sube documentación del data room** (informes financieros, contratos, presentaciones)
    y elige el tipo de análisis que necesitas. El agente usa **RAG (Retrieval-Augmented Generation)** para
    proporcionar insights basados exclusivamente en tus documentos.
    """)

    st.markdown("---")

    # ========================================================================
    # SIDEBAR - INPUTS
    # ========================================================================

    with st.sidebar:
        st.header("⚙️ Configuración")

        # API Key
        st.markdown("### 🔑 OpenAI API Key")
        openai_api_key = st.text_input(
            "Introduce tu API key",
            type="password",
            help="Tu API key no se almacena y solo se usa para esta sesión"
        )

        st.markdown("---")

        # File upload
        st.markdown("### 📁 Data Room")
        uploaded_files = st.file_uploader(
            "Sube documentos (PDF)",
            type=["pdf"],
            accept_multiple_files=True,
            help="Sube uno o varios PDFs del data room del target"
        )

        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)} documento(s) cargado(s)")
            with st.expander("📄 Archivos cargados"):
                for file in uploaded_files:
                    st.markdown(f"- `{file.name}`")

        st.markdown("---")

        # Analysis mode
        st.markdown("### 🎯 Modo de Análisis")
        mode = st.selectbox(
            "Selecciona el tipo de análisis",
            ["Summary", "Risks", "Questions", "Free question"],
            help="Elige el enfoque del análisis de Due Diligence"
        )

        # Mode descriptions
        mode_descriptions = {
            "Summary": "📊 Resumen ejecutivo del target: negocio, posición competitiva, KPIs y tendencias",
            "Risks": "⚠️ Mapa de riesgos y red flags: financieros, legales, operativos y ESG",
            "Questions": "❓ Lista de preguntas clave para el equipo directivo del target",
            "Free question": "💬 Pregunta personalizada sobre la documentación"
        }

        st.info(mode_descriptions[mode])

    # ========================================================================
    # MAIN AREA
    # ========================================================================

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("## 🔍 Análisis")
        st.markdown(f"**Modo seleccionado:** `{mode}`")

    with col2:
        st.markdown("## 📊 Estado")
        if not openai_api_key:
            st.warning("⚠️ API key requerida")
        if not uploaded_files:
            st.warning("⚠️ Sube documentos")
        if openai_api_key and uploaded_files:
            st.success("✅ Listo para analizar")

    st.markdown("---")

    # Free question input
    custom_question = ""
    if mode == "Free question":
        custom_question = st.text_area(
            "✍️ Escribe tu pregunta",
            height=100,
            placeholder="Ejemplo: ¿Cuál es la estructura de costes del target y cómo ha evolucionado?",
            help="Haz cualquier pregunta sobre la documentación cargada"
        )

    # Run button
    run_analysis = st.button(
        "▶️ Run Due Diligence Agent",
        type="primary",
        use_container_width=True
    )

    # ========================================================================
    # ANALYSIS EXECUTION
    # ========================================================================

    if run_analysis:
        # Validations
        if not openai_api_key:
            st.error("❌ **Error:** Por favor, introduce tu OpenAI API key en la barra lateral.")
            st.stop()

        if not uploaded_files:
            st.error("❌ **Error:** Por favor, sube al menos un documento PDF en la barra lateral.")
            st.stop()

        if mode == "Free question" and not custom_question.strip():
            st.error("❌ **Error:** Por favor, escribe tu pregunta en el campo de texto.")
            st.stop()

        # Process documents
        with st.spinner("📄 Extrayendo texto de los PDFs..."):
            chunks = extract_chunks_from_pdfs(uploaded_files)

        if not chunks:
            st.error("❌ **Error:** No se pudo extraer texto de los documentos. Verifica que los PDFs contengan texto legible.")
            st.stop()

        st.info(f"✅ Extraídos {len(chunks)} chunks de texto de {len(uploaded_files)} documento(s)")

        # Build embeddings
        embeddings, chunks = build_embeddings_index(chunks)

        # Get query
        query = get_mode_query(mode, custom_question)

        # Retrieve relevant chunks
        with st.spinner("🔍 Buscando información relevante..."):
            retrieved = retrieve_relevant_chunks(query, embeddings, chunks, top_k=10)

        if not retrieved:
            st.warning("⚠️ No se encontraron chunks relevantes. Intenta con otros documentos o reformula la pregunta.")
            st.stop()

        # Build prompts
        system_prompt, user_prompt = build_system_and_user_prompts(mode, query, retrieved)

        # Call LLM
        try:
            with st.spinner("🤖 Generando análisis..."):
                response = call_llm(system_prompt, user_prompt, openai_api_key)

            # Display response
            st.markdown("---")
            st.markdown("## 📝 Resultado del Análisis")
            st.markdown(response)

            # Display sources
            st.markdown("---")
            with st.expander("📚 **Fuentes utilizadas** (ver contexto completo)", expanded=False):
                st.markdown("El agente utilizó los siguientes fragmentos de documentación:")
                for i, (chunk, score) in enumerate(retrieved, start=1):
                    st.markdown(f"### SOURCE {i}")
                    st.markdown(f"**Archivo:** `{chunk.file_name}` | **Página:** {chunk.page_num} | **Relevancia:** {score:.2%}")
                    st.text_area(
                        f"Contenido SOURCE {i}",
                        chunk.text,
                        height=150,
                        key=f"source_{i}",
                        label_visibility="collapsed"
                    )
                    st.markdown("---")

        except Exception as e:
            st.error(f"❌ **Error al llamar a la API de OpenAI:**\n\n{str(e)}")
            st.info("💡 Verifica que tu API key sea válida y que tengas créditos disponibles.")

    # ========================================================================
    # FOOTER
    # ========================================================================

    st.markdown("---")
    st.caption("""
    🧠 **Sobre esta herramienta:**
    Este DD Agent demuestra capacidades end-to-end en sistemas RAG (Retrieval-Augmented Generation):
    - Extracción y procesamiento de documentos PDF
    - Embeddings semánticos con Sentence Transformers
    - Búsqueda vectorial y ranking de relevancia
    - Generación de análisis contextualizados con LLMs

    Ideal para mostrar en entrevistas técnicas de M&A / Data Science.
    """)


if __name__ == "__main__":
    main()
