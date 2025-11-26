"""
Financial RAG Agent - Streamlit Web Application

Interactive web interface for the Financial RAG Agent.
"""

import streamlit as st
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "financial-rag-agent" / "src"))

try:
    from financial_rag_agent.agents.agent import FinancialAgent
    from financial_rag_agent.ingestion.loader import DataLoader
    from financial_rag_agent.retrieval.vector_store import build_vector_store_from_news
except ImportError as e:
    st.error(f"Error importing modules: {e}")
    st.stop()

# Page config
st.set_page_config(
    page_title="Financial RAG Agent",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .tool-badge {
        background-color: #e1f5ff;
        padding: 0.2rem 0.5rem;
        border-radius: 0.3rem;
        margin: 0.2rem;
        display: inline-block;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def initialize_system():
    """Initialize the RAG system (cached)."""
    try:
        # Load data
        loader = DataLoader()
        news = loader.load_news()

        # Build vector store
        vector_store = build_vector_store_from_news(news, save=False)

        # Initialize agent
        agent = FinancialAgent()

        # Get available tickers
        tickers = loader.get_tickers()

        return agent, tickers, True
    except Exception as e:
        st.error(f"Failed to initialize system: {e}")
        return None, [], False


def format_answer(result):
    """Format the agent's answer nicely."""
    st.markdown("### 📝 Answer")
    st.markdown(result["final_answer"])

    # Show metadata in expander
    with st.expander("🔍 Details & Metadata"):
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Execution Time", f"{result.get('execution_time_ms', 0):.0f} ms")

        with col2:
            st.metric("Tools Used", len(result.get("used_tools", [])))

        with col3:
            plan = result.get("plan", {})
            st.metric("Question Type", plan.get("question_type", "N/A"))

        # Show tools used
        st.markdown("**Tools Executed:**")
        tools = result.get("used_tools", [])
        if tools:
            tools_html = " ".join([f'<span class="tool-badge">{tool}</span>' for tool in tools])
            st.markdown(tools_html, unsafe_allow_html=True)
        else:
            st.info("No tools were used")

        # Show plan
        if "plan" in result:
            st.markdown("**Execution Plan:**")
            st.json(result["plan"])

        # Show retrieved documents
        if "tool_results" in result and "retrieve_context" in result["tool_results"]:
            context_result = result["tool_results"]["retrieve_context"]
            if context_result.get("success") and context_result.get("documents"):
                st.markdown("**Retrieved Documents:**")
                for i, doc in enumerate(context_result["documents"][:3], 1):
                    with st.container():
                        st.markdown(f"**{i}. {doc.get('headline', 'N/A')}**")
                        st.caption(f"Ticker: {doc.get('ticker')} | Date: {doc.get('date')} | Score: {doc.get('score', 0):.3f}")
                        with st.expander("View summary"):
                            st.write(doc.get("summary", ""))


def main():
    """Main Streamlit app."""

    # Header
    st.markdown('<div class="main-header">📊 Financial RAG Agent</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">AI-Powered Financial Analysis with RAG & Agents</div>', unsafe_allow_html=True)

    # Initialize system
    with st.spinner("Initializing Financial RAG Agent..."):
        agent, available_tickers, success = initialize_system()

    if not success or agent is None:
        st.error("❌ Failed to initialize the system. Please check the logs.")
        st.stop()

    st.success("✅ System initialized successfully!")

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")

        # Ticker selection
        ticker = st.selectbox(
            "Select Ticker (Optional)",
            ["None"] + available_tickers,
            help="Select a specific company or leave as 'None' for general questions"
        )
        if ticker == "None":
            ticker = None

        st.markdown("---")

        # Example questions
        st.header("💡 Example Questions")

        examples = {
            "Single Company Analysis": [
                "What are the key financial highlights for Apple?",
                "How is Microsoft's cloud business performing?",
                "Analyze NVIDIA's recent earnings results"
            ],
            "Comparative Analysis": [
                "Compare Apple and Microsoft's profitability metrics",
                "Which has better margins: Google or Meta?",
                "Compare NVDA and AMZN growth rates"
            ],
            "Risk Analysis": [
                "What are the main risks facing Tesla?",
                "Identify key challenges for NVIDIA",
                "What are the financial risks for Amazon?"
            ],
            "Growth & Trends": [
                "Analyze Tesla's growth trajectory",
                "How are AI investments impacting tech companies?",
                "What's driving revenue growth for these companies?"
            ]
        }

        for category, questions in examples.items():
            with st.expander(category):
                for q in questions:
                    if st.button(q, key=q):
                        st.session_state.example_question = q

        st.markdown("---")

        # System status
        st.header("📊 System Status")
        status = agent.get_status()

        st.metric("Vector Store Docs", status["vector_store"]["num_documents"])
        st.metric("Available Tools", len(status["available_tools"]))

        llm_status = "✅ Available" if status["llm"]["available"] else "⚠️ Mock Mode"
        st.info(f"LLM: {llm_status}")

        if not status["llm"]["available"]:
            st.warning("⚠️ LLM not configured. Using mock responses. Add API keys to .env for real responses.")

    # Main content area
    st.header("🤔 Ask a Question")

    # Check if there's an example question
    default_question = st.session_state.get("example_question", "")

    # Question input
    question = st.text_area(
        "Enter your financial question:",
        value=default_question,
        height=100,
        placeholder="E.g., What are Apple's key financial metrics and recent performance highlights?"
    )

    # Clear example question after using it
    if default_question:
        st.session_state.example_question = ""

    # Submit button
    col1, col2, col3 = st.columns([1, 1, 4])

    with col1:
        submit = st.button("🚀 Ask Agent", type="primary", use_container_width=True)

    with col2:
        clear = st.button("🗑️ Clear", use_container_width=True)

    if clear:
        st.rerun()

    # Process question
    if submit:
        if not question:
            st.error("Please enter a question!")
        else:
            with st.spinner("🤖 Agent is thinking..."):
                try:
                    result = agent.answer(ticker=ticker, question=question)

                    if result.get("success", True):
                        format_answer(result)
                    else:
                        st.error(f"❌ Error: {result.get('error', 'Unknown error')}")

                except Exception as e:
                    st.error(f"❌ An error occurred: {str(e)}")
                    with st.expander("Show error details"):
                        st.exception(e)

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.9rem;">
        <p>Financial RAG Agent v0.1.0 | Built with Streamlit, FastAPI, and LangChain</p>
        <p>⚠️ This is a demonstration system with synthetic data. Not for actual investment decisions.</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
