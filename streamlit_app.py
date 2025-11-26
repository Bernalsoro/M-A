"""
Financial RAG Agent - Streamlit Web Application

Interactive web interface for the Financial RAG Agent.
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
    .api-key-input {
        font-family: monospace;
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state
if "agent" not in st.session_state:
    st.session_state.agent = None
if "system_initialized" not in st.session_state:
    st.session_state.system_initialized = False
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "llm_provider" not in st.session_state:
    st.session_state.llm_provider = "openai"


def initialize_data_layer():
    """Initialize data layer (cached) - separate from agent."""
    try:
        loader = DataLoader()
        news = loader.load_news()
        vector_store = build_vector_store_from_news(news, save=False)
        tickers = loader.get_tickers()
        return loader, vector_store, tickers, True
    except Exception as e:
        st.error(f"Failed to initialize data layer: {e}")
        return None, None, [], False


def create_agent(api_key=None, provider="openai"):
    """Create agent with optional API key."""
    try:
        # Set environment variable if API key provided
        if api_key:
            if provider == "openai":
                os.environ["OPENAI_API_KEY"] = api_key
                os.environ["LLM_PROVIDER"] = "openai"
            elif provider == "anthropic":
                os.environ["ANTHROPIC_API_KEY"] = api_key
                os.environ["LLM_PROVIDER"] = "anthropic"

        # Create agent
        agent = FinancialAgent()
        return agent, True
    except Exception as e:
        st.error(f"Failed to create agent: {e}")
        return None, False


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

    # Initialize data layer (always needed, cached)
    if not st.session_state.system_initialized:
        with st.spinner("Initializing data layer..."):
            loader, vector_store, tickers, success = initialize_data_layer()
            if success:
                st.session_state.loader = loader
                st.session_state.vector_store = vector_store
                st.session_state.tickers = tickers
                st.session_state.system_initialized = True
            else:
                st.error("❌ Failed to initialize system. Please refresh the page.")
                st.stop()

    # Sidebar
    with st.sidebar:
        st.header("🔑 LLM Configuration")

        # API Key input
        st.markdown("**Enter your API Key:**")

        # Provider selection
        provider = st.selectbox(
            "Provider",
            ["openai", "anthropic"],
            index=0 if st.session_state.llm_provider == "openai" else 1,
            help="Select your LLM provider"
        )

        # API Key input
        api_key_input = st.text_input(
            "API Key" if provider == "openai" else "API Key",
            value=st.session_state.api_key,
            type="password",
            placeholder="sk-..." if provider == "openai" else "sk-ant-...",
            help=f"Enter your {provider.upper()} API key",
            key="api_key_input"
        )

        # Model selection
        if provider == "openai":
            model = st.selectbox(
                "Model",
                ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo"],
                help="gpt-4o-mini is cheapest (~$0.15/1M tokens)"
            )
            if model:
                os.environ["OPENAI_MODEL"] = model
        else:
            model = st.selectbox(
                "Model",
                ["claude-3-5-sonnet-20241022", "claude-3-opus-20240229", "claude-3-sonnet-20240229"],
                help="Claude models for financial analysis"
            )
            if model:
                os.environ["ANTHROPIC_MODEL"] = model

        # Apply button
        if st.button("🔄 Apply API Key", type="primary", use_container_width=True):
            if api_key_input and api_key_input.strip():
                st.session_state.api_key = api_key_input.strip()
                st.session_state.llm_provider = provider

                # Create new agent with API key
                with st.spinner("Connecting to LLM..."):
                    agent, success = create_agent(st.session_state.api_key, provider)
                    if success:
                        st.session_state.agent = agent
                        st.success(f"✅ Connected to {provider.upper()}!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to connect. Check your API key.")
            else:
                st.warning("Please enter an API key")

        # Clear API key button
        if st.session_state.api_key:
            if st.button("🗑️ Clear API Key", use_container_width=True):
                st.session_state.api_key = ""
                st.session_state.agent = None
                st.rerun()

        # LLM Status
        st.markdown("---")
        st.markdown("**🤖 LLM Status:**")

        if st.session_state.agent:
            status = st.session_state.agent.get_status()
            if status["llm"]["available"]:
                st.success(f"✅ Connected: {status['llm']['provider']} - {status['llm']['model']}")
            else:
                st.warning("⚠️ Mock Mode - Add API key for real responses")
        else:
            st.info("ℹ️ No API key configured - Using mock mode")
            st.caption("Mock mode works but gives pre-written responses. Add your API key above for real AI answers.")

        st.markdown("---")

        # Ticker selection
        st.header("⚙️ Query Settings")
        ticker = st.selectbox(
            "Select Ticker (Optional)",
            ["None"] + st.session_state.tickers,
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
                    if st.button(q, key=q, use_container_width=True):
                        st.session_state.example_question = q

        st.markdown("---")

        # System status
        st.header("📊 System Status")
        st.metric("Vector Store Docs", len(st.session_state.get("tickers", [])) * 3)
        st.metric("Available Tickers", len(st.session_state.get("tickers", [])))

        # Get API key info
        st.markdown("---")
        with st.expander("ℹ️ How to get API keys"):
            st.markdown("""
            **OpenAI (Recommended):**
            1. Go to [platform.openai.com](https://platform.openai.com/api-keys)
            2. Sign up / Log in
            3. Create new secret key
            4. Copy and paste above

            **Cost:** ~$0.15 per 1M tokens (very cheap!)

            **Anthropic:**
            1. Go to [console.anthropic.com](https://console.anthropic.com/)
            2. Sign up / Log in
            3. Get API key
            4. Copy and paste above
            """)

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
            # Create agent if not exists
            if not st.session_state.agent:
                with st.spinner("Initializing agent..."):
                    agent, success = create_agent(st.session_state.api_key, st.session_state.llm_provider)
                    if success:
                        st.session_state.agent = agent

            if st.session_state.agent:
                with st.spinner("🤖 Agent is thinking..."):
                    try:
                        result = st.session_state.agent.answer(ticker=ticker, question=question)

                        if result.get("success", True):
                            format_answer(result)
                        else:
                            st.error(f"❌ Error: {result.get('error', 'Unknown error')}")

                    except Exception as e:
                        st.error(f"❌ An error occurred: {str(e)}")
                        with st.expander("Show error details"):
                            st.exception(e)
            else:
                st.error("Failed to initialize agent. Please check configuration.")

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.9rem;">
        <p><strong>Financial RAG Agent v0.1.0</strong> | Built with Streamlit & AI</p>
        <p>💡 <strong>Tip:</strong> Add your OpenAI/Anthropic API key in the sidebar for real AI responses!</p>
        <p>⚠️ This is a demonstration system with synthetic data. Not for actual investment decisions.</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
