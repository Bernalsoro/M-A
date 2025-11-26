"""
Financial RAG Agent - Streamlit Web Application

Interactive web interface for the Financial RAG Agent with in-app API key configuration.
"""

import streamlit as st
import sys
import os
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "financial-rag-agent" / "src"))

try:
    from financial_rag_agent.agents.agent import FinancialAgent
    from financial_rag_agent.ingestion.loader import DataLoader
    from financial_rag_agent.retrieval.vector_store import build_vector_store_from_news
    from financial_rag_agent.llm.llm_client import LLMClient
    from financial_rag_agent.agents.tools import FinancialTools
    from financial_rag_agent.agents.planner import AgentPlanner
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


# Initialize session state
if "data_initialized" not in st.session_state:
    st.session_state.data_initialized = False
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "llm_provider" not in st.session_state:
    st.session_state.llm_provider = "openai"
if "llm_model" not in st.session_state:
    st.session_state.llm_model = "gpt-4o-mini"
if "llm_connected" not in st.session_state:
    st.session_state.llm_connected = False


@st.cache_resource
def initialize_data_layer():
    """Initialize data layer (cached) - only runs once."""
    try:
        loader = DataLoader()
        news = loader.load_news()
        vector_store = build_vector_store_from_news(news, save=False)
        tickers = loader.get_tickers()
        return loader, vector_store, tickers
    except Exception as e:
        st.error(f"Failed to initialize data: {e}")
        return None, None, []


def create_agent_with_key(api_key, provider, model):
    """Create agent with specific API key and configuration."""
    try:
        # Create LLM client with explicit API key
        llm_client = LLMClient(
            provider=provider,
            model=model,
            api_key=api_key if api_key else None,
            temperature=0.1,
            max_tokens=2048
        )

        # Create agent with this LLM client
        tools = FinancialTools()
        planner = AgentPlanner()

        agent = FinancialAgent(
            tools=tools,
            planner=planner,
            llm_client=llm_client,
            enable_planning=True
        )

        return agent
    except Exception as e:
        st.error(f"Error creating agent: {e}")
        return None


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

        # Show retrieved documents
        if "tool_results" in result and "retrieve_context" in result["tool_results"]:
            context_result = result["tool_results"]["retrieve_context"]
            if context_result.get("success") and context_result.get("documents"):
                st.markdown("**Retrieved Documents:**")
                for i, doc in enumerate(context_result["documents"][:3], 1):
                    st.markdown(f"**{i}. {doc.get('headline', 'N/A')}**")
                    st.caption(f"Ticker: {doc.get('ticker')} | Date: {doc.get('date')} | Score: {doc.get('score', 0):.3f}")


def main():
    """Main Streamlit app."""

    # Header
    st.markdown('<div class="main-header">📊 Financial RAG Agent</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">AI-Powered Financial Analysis with RAG & Agents</div>', unsafe_allow_html=True)

    # Initialize data layer
    if not st.session_state.data_initialized:
        with st.spinner("Initializing Financial RAG Agent..."):
            loader, vector_store, tickers = initialize_data_layer()
            if loader and vector_store:
                st.session_state.loader = loader
                st.session_state.vector_store = vector_store
                st.session_state.tickers = tickers
                st.session_state.data_initialized = True
            else:
                st.error("❌ Failed to initialize. Please refresh.")
                st.stop()

    # Sidebar
    with st.sidebar:
        st.header("🔑 API Configuration")

        # Provider selection
        provider = st.selectbox(
            "LLM Provider",
            ["openai", "anthropic"],
            index=0,
            help="Select your LLM provider"
        )

        # Model selection
        if provider == "openai":
            model_options = ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]
            default_idx = 0
            help_text = "gpt-4o-mini is cheapest (~$0.15/1M tokens)"
        else:
            model_options = ["claude-3-5-sonnet-20241022", "claude-3-opus-20240229", "claude-3-sonnet-20240229"]
            default_idx = 0
            help_text = "Claude models for analysis"

        model = st.selectbox(
            "Model",
            model_options,
            index=default_idx,
            help=help_text
        )

        # API Key input
        api_key = st.text_input(
            "API Key",
            value=st.session_state.api_key,
            type="password",
            placeholder="sk-..." if provider == "openai" else "sk-ant-...",
            help=f"Your {provider.upper()} API key"
        )

        # Connect button
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔌 Connect", type="primary", use_container_width=True):
                if api_key and api_key.strip():
                    st.session_state.api_key = api_key.strip()
                    st.session_state.llm_provider = provider
                    st.session_state.llm_model = model
                    st.session_state.llm_connected = True
                    st.success("✅ API key saved!")
                    st.rerun()
                else:
                    st.warning("⚠️ Please enter an API key")

        with col2:
            if st.button("🔌 Disconnect", use_container_width=True):
                st.session_state.api_key = ""
                st.session_state.llm_connected = False
                st.info("🔓 Disconnected")
                st.rerun()

        # Status display
        st.markdown("---")
        st.markdown("**🤖 Status:**")

        if st.session_state.llm_connected and st.session_state.api_key:
            st.success(f"✅ {st.session_state.llm_provider.upper()}")
            st.caption(f"Model: {st.session_state.llm_model}")
        else:
            st.info("ℹ️ Mock Mode")
            st.caption("Add API key for real responses")

        # Instructions
        with st.expander("ℹ️ Get API Key"):
            if provider == "openai":
                st.markdown("""
                **OpenAI API Key:**
                1. Visit [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
                2. Sign up or log in
                3. Click "Create new secret key"
                4. Copy and paste above

                **Cost:** ~$0.15 per 1M tokens (very cheap!)
                """)
            else:
                st.markdown("""
                **Anthropic API Key:**
                1. Visit [console.anthropic.com](https://console.anthropic.com/)
                2. Sign up or log in
                3. Get your API key
                4. Copy and paste above
                """)

        st.markdown("---")

        # Query settings
        st.header("⚙️ Settings")

        ticker = st.selectbox(
            "Ticker (Optional)",
            ["None"] + st.session_state.tickers,
            help="Select a company"
        )
        if ticker == "None":
            ticker = None

        st.markdown("---")

        # Examples
        st.header("💡 Examples")

        examples = {
            "📊 Analysis": [
                "What are Apple's key financial metrics?",
                "How is Microsoft's cloud business?",
                "Analyze NVIDIA's recent earnings"
            ],
            "⚖️ Compare": [
                "Compare Apple vs Microsoft profitability",
                "Which has better margins: Google or Meta?",
                "NVDA vs AMZN growth comparison"
            ],
            "⚠️ Risks": [
                "What are Tesla's main risks?",
                "NVIDIA's key challenges?",
                "Amazon's financial risks?"
            ]
        }

        for category, questions in examples.items():
            with st.expander(category):
                for q in questions:
                    if st.button(q, key=q, use_container_width=True):
                        st.session_state.example_question = q

    # Main area
    st.header("🤔 Ask a Question")

    # Question input
    default_q = st.session_state.get("example_question", "")
    question = st.text_area(
        "Your question:",
        value=default_q,
        height=100,
        placeholder="e.g., What are Apple's key financial highlights?"
    )

    if default_q:
        st.session_state.example_question = ""

    # Buttons
    col1, col2 = st.columns([1, 5])
    with col1:
        ask_btn = st.button("🚀 Ask", type="primary", use_container_width=True)
    with col2:
        if st.button("🗑️ Clear", use_container_width=True):
            st.rerun()

    # Process question
    if ask_btn:
        if not question:
            st.error("❌ Please enter a question")
        else:
            with st.spinner("🤖 Thinking..."):
                try:
                    # Create agent with current configuration
                    agent = create_agent_with_key(
                        st.session_state.api_key if st.session_state.llm_connected else None,
                        st.session_state.llm_provider,
                        st.session_state.llm_model
                    )

                    if agent:
                        result = agent.answer(ticker=ticker, question=question)

                        if result.get("success", True):
                            format_answer(result)

                            # Show LLM mode
                            if result.get("llm_available"):
                                st.success("✅ Response from real LLM")
                            else:
                                st.warning("⚠️ Mock response (add API key for real AI)")
                        else:
                            st.error(f"❌ Error: {result.get('error')}")
                    else:
                        st.error("❌ Failed to create agent")

                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    with st.expander("Details"):
                        st.exception(e)

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666;">
        <p><b>Financial RAG Agent v0.1.0</b> | AI-Powered Analysis</p>
        <p>⚠️ Demo system with synthetic data - Not for investment decisions</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
