"""
Financial RAG Agent - Enhanced Streamlit UI
Shows the complete RAG + Agent workflow visually
"""

import streamlit as st
import sys
import os
from pathlib import Path
import time

# Add src to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "financial-rag-agent" / "src"))

try:
    from financial_rag_agent.agents.agent import FinancialAgent
    from financial_rag_agent.ingestion.loader import DataLoader
    from financial_rag_agent.retrieval.vector_store import build_vector_store_from_news
    from financial_rag_agent.retrieval.retriever import FinancialRetriever
    from financial_rag_agent.llm.llm_client import LLMClient
    from financial_rag_agent.agents.tools import FinancialTools
    from financial_rag_agent.agents.planner import AgentPlanner
except ImportError as e:
    st.error(f"Error importing modules: {e}")
    st.stop()

# Page config
st.set_page_config(
    page_title="Financial RAG Agent - Visual Demo",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
<style>
    .big-title {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(120deg, #1f77b4, #ff7f0e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .step-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .tool-box {
        background: #f0f8ff;
        border-left: 4px solid #1f77b4;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 5px;
    }
    .doc-box {
        background: #fff4e6;
        border-left: 4px solid #ff7f0e;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 5px;
    }
    .metric-box {
        background: #e8f5e9;
        border-left: 4px solid #4caf50;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Session state
if "data_initialized" not in st.session_state:
    st.session_state.data_initialized = False
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "llm_provider" not in st.session_state:
    st.session_state.llm_provider = "openai"
if "llm_model" not in st.session_state:
    st.session_state.llm_model = "gpt-4o-mini"
if "question" not in st.session_state:
    st.session_state.question = ""
if "selected_ticker" not in st.session_state:
    st.session_state.selected_ticker = "None"

@st.cache_resource
def initialize_data_layer():
    """Initialize data layer."""
    try:
        loader = DataLoader()
        news = loader.load_news()
        vector_store = build_vector_store_from_news(news, save=False)

        # Check if vector store is in fallback mode
        if vector_store and vector_store.fallback_mode:
            st.warning("⚠️ **Note:** Vector embeddings unavailable (using keyword search). All other features work normally!")

        tickers = loader.get_tickers()
        return loader, vector_store, tickers
    except Exception as e:
        st.error(f"❌ Failed to initialize data layer: {e}")
        import traceback
        with st.expander("Show error details"):
            st.code(traceback.format_exc())
        return None, None, []

def create_agent_with_key(api_key, provider, model, loader, vector_store):
    """Create agent with API key and initialized data."""
    try:
        # Treat empty string as None for mock mode
        effective_key = api_key.strip() if api_key else None
        effective_key = effective_key if effective_key else None

        llm_client = LLMClient(
            provider=provider,
            model=model,
            api_key=effective_key,
            temperature=0.1,
            max_tokens=2048
        )

        # Create retriever with the vector store
        retriever = FinancialRetriever(vector_store=vector_store)

        # Create tools with loader and retriever
        tools = FinancialTools(loader=loader, retriever=retriever)

        planner = AgentPlanner()
        agent = FinancialAgent(tools=tools, planner=planner, llm_client=llm_client, enable_planning=True)
        return agent
    except Exception as e:
        st.error(f"⚠️ **Error creating agent:** {e}")
        import traceback
        with st.expander("Show error details"):
            st.code(traceback.format_exc())
        st.info("💡 **Tip:** This might be a model loading issue. Try refreshing the page or check if Streamlit Cloud has enough memory.")
        return None

def main():
    # Header
    st.markdown('<div class="big-title">🤖 Financial RAG Agent</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">See RAG + Agents in Action - Step by Step</div>', unsafe_allow_html=True)

    # Show mode indicator
    if not st.session_state.api_key.strip():
        st.info("🎭 **Mock Mode**: The agent is working with simulated AI responses. Real financial data and RAG retrieval are active. Add an API key in the sidebar for real AI-generated analysis.")

    # Initialize
    if not st.session_state.data_initialized:
        with st.spinner("🔄 Initializing system..."):
            loader, vector_store, tickers = initialize_data_layer()
            if loader:
                st.session_state.loader = loader
                st.session_state.vector_store = vector_store
                st.session_state.tickers = tickers
                st.session_state.data_initialized = True
            else:
                st.stop()

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")

        provider = st.selectbox("Provider", ["openai", "anthropic"])

        if provider == "openai":
            model = st.selectbox("Model", ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"])
        else:
            model = st.selectbox("Model", ["claude-3-5-sonnet-20241022", "claude-3-opus-20240229"])

        api_key = st.text_input("API Key", value=st.session_state.api_key, type="password")

        if st.button("💾 Save Config", use_container_width=True):
            st.session_state.api_key = api_key.strip()
            st.session_state.llm_provider = provider
            st.session_state.llm_model = model
            st.success("✅ Saved!")

        st.markdown("---")
        st.markdown("**Status:**")
        if st.session_state.api_key.strip():
            st.success(f"✅ {provider.upper()} Connected")
        else:
            st.info("ℹ️ Mock Mode Active")
            st.caption("Using simulated responses. Add API key for real AI analysis.")

        st.markdown("---")
        st.header("📊 System Info")
        st.metric("Companies", len(st.session_state.tickers))
        st.metric("News Items", 21)
        st.metric("Financial Records", 35)

        with st.expander("🏢 Available Companies"):
            for ticker in st.session_state.tickers:
                st.write(f"• {ticker}")

    # Main area - 2 columns
    col1, col2 = st.columns([1, 1])

    with col1:
        st.header("💬 Your Question")

        ticker = st.selectbox(
            "Company (optional)",
            ["None"] + st.session_state.tickers,
            index=0 if st.session_state.selected_ticker == "None" else (
                st.session_state.tickers.index(st.session_state.selected_ticker) + 1
                if st.session_state.selected_ticker in st.session_state.tickers else 0
            ),
            key="ticker_select"
        )
        if ticker == "None":
            ticker = None
        else:
            st.session_state.selected_ticker = ticker

        question = st.text_area(
            "Ask anything:",
            value=st.session_state.question,
            height=150,
            placeholder="e.g., What are Apple's key financial metrics and recent performance?",
            key="question_input"
        )

        # Update session state when question changes
        if question != st.session_state.question:
            st.session_state.question = question

        # Quick examples
        st.caption("**Quick Examples:**")
        examples = {
            "📊 Single Analysis": "What are the key financial highlights for Apple?",
            "⚖️ Compare": "Compare Apple and Microsoft's profitability metrics",
            "⚠️ Risks": "What are the main risks facing NVIDIA?"
        }

        cols = st.columns(3)
        for idx, (label, q) in enumerate(examples.items()):
            with cols[idx]:
                if st.button(label, use_container_width=True, key=f"example_{idx}"):
                    st.session_state.question = q
                    st.session_state.run_analysis = False  # Reset analysis state
                    st.rerun()

        if st.button("🚀 ANALYZE", type="primary", use_container_width=True):
            if st.session_state.question.strip():
                st.session_state.run_analysis = True
                st.session_state.ticker = ticker
                st.rerun()

    with col2:
        st.header("🔍 Agent Workflow")

        if "run_analysis" in st.session_state and st.session_state.run_analysis:
            question = st.session_state.question
            ticker = st.session_state.get("ticker", None)

            # Create agent with initialized data
            agent = create_agent_with_key(
                st.session_state.api_key,
                st.session_state.llm_provider,
                st.session_state.llm_model,
                st.session_state.loader,
                st.session_state.vector_store
            )

            if not agent:
                st.error("❌ Failed to create agent. Please check the logs above.")
                st.session_state.run_analysis = False
            else:
                # STEP 1: Planning
                st.markdown('<div class="step-box">📋 STEP 1: PLANNING</div>', unsafe_allow_html=True)
                with st.spinner("Agent is analyzing your question..."):
                    time.sleep(0.5)
                    try:
                        result = agent.answer(ticker=ticker, question=question)
                    except Exception as e:
                        st.error(f"❌ Error during analysis: {e}")
                        import traceback
                        with st.expander("Show error details"):
                            st.code(traceback.format_exc())
                        st.info("💡 **Tip:** This error might be due to model loading issues. The app should still work in Mock Mode.")
                        st.session_state.run_analysis = False
                        return

                plan = result.get("plan", {})
                st.markdown(f"""
                **Question Type:** `{plan.get('question_type', 'N/A')}`
                **Tickers Detected:** `{', '.join(plan.get('tickers', ['None']))}`
                **Tools Needed:** `{', '.join(plan.get('tools', []))}`
                """)

                # STEP 2: Tool Execution
                st.markdown('<div class="step-box">🔧 STEP 2: EXECUTING TOOLS</div>', unsafe_allow_html=True)

                tool_results = result.get("tool_results", {})

                # Show each tool result
                for tool_name, tool_result in tool_results.items():
                    if tool_result.get("success"):
                        if tool_name == "compute_ratios":
                            st.markdown('<div class="metric-box">', unsafe_allow_html=True)
                            st.markdown(f"**🔢 {tool_name}**")
                            data = tool_result.get("data", {})

                            col_a, col_b, col_c = st.columns(3)
                            with col_a:
                                st.metric("Revenue", f"${data.get('revenue', 0):,.0f}M")
                            with col_b:
                                st.metric("Net Margin", f"{data.get('net_margin', 0):.1f}%")
                            with col_c:
                                st.metric("ROE", f"{data.get('roe', 0):.1f}%")

                            st.markdown('</div>', unsafe_allow_html=True)

                        elif tool_name == "retrieve_context":
                            st.markdown('<div class="doc-box">', unsafe_allow_html=True)
                            st.markdown(f"**📰 {tool_name}**")
                            docs = tool_result.get("documents", [])
                            st.write(f"Found **{len(docs)} relevant documents**:")
                            for i, doc in enumerate(docs[:2], 1):
                                st.markdown(f"{i}. *{doc.get('headline', 'N/A')}* (Score: {doc.get('score', 0):.2f})")
                            st.markdown('</div>', unsafe_allow_html=True)

                        elif tool_name == "compare_two_tickers":
                            st.markdown('<div class="tool-box">', unsafe_allow_html=True)
                            st.markdown(f"**⚖️ {tool_name}**")
                            st.write(f"Comparing {tool_result.get('ticker1')} vs {tool_result.get('ticker2')}")
                            st.markdown('</div>', unsafe_allow_html=True)

                # STEP 3: LLM Synthesis
                st.markdown('<div class="step-box">🧠 STEP 3: AI SYNTHESIS</div>', unsafe_allow_html=True)
                if result.get("llm_available"):
                    st.success("✅ Using real LLM (ChatGPT/Claude)")
                else:
                    st.warning("⚠️ Using mock response (no API key)")

                st.markdown("**Final Answer:**")
                st.markdown(result["final_answer"])

                # Metrics
                st.markdown("---")
                col_x, col_y, col_z = st.columns(3)
                with col_x:
                    st.metric("⏱️ Time", f"{result.get('execution_time_ms', 0):.0f}ms")
                with col_y:
                    st.metric("🔧 Tools", len(result.get("used_tools", [])))
                with col_z:
                    st.metric("📄 Docs", len(tool_results.get("retrieve_context", {}).get("documents", [])))

                # Reset
                st.session_state.run_analysis = False
        else:
            st.info("👆 Enter a question and click ANALYZE to see the agent in action!")

            st.markdown("""
            ### What you'll see:

            **📋 Planning Phase:**
            - Agent analyzes your question
            - Decides which tools to use
            - Creates execution plan

            **🔧 Tool Execution:**
            - Fetches real financial data
            - Computes ratios and metrics
            - Searches vector database for news

            **🧠 AI Synthesis:**
            - Combines all information
            - Generates analyst-style response
            - Shows execution metrics
            """)

if __name__ == "__main__":
    main()
