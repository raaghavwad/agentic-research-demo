"""Streamlit frontend for the agentic research demo.

This module provides a web UI that allows users to interact with the Research Analyst
Agentic System through a simple browser interface. The UI calls into the existing
LangGraph workflow (root agent + SearchAgent + DatabaseAgent) and preserves all
observability behavior, ensuring that OpenTelemetry spans and Jaeger traces are
generated consistently whether the system is accessed via CLI or this web interface.

The UI should:
- Initialize the workflow once (e.g., via st.cache_resource) for performance
- For each user query, call the orchestration function (e.g., run_graph(workflow, user_query))
- Display the combined final answer, optionally showing separate "Web Research Summary"
  and "Oracle Trends" sections
- Provide clear instructions and a link or note about viewing traces in Jaeger

Running:
    streamlit run ui/streamlit_app.py

Note: The UI must not bypass observability - it should always rely on the same
build_workflow + run_graph functions that the CLI uses, so traces remain consistent
and visible in Jaeger under service.name = agentic-research-demo.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add src/ to Python path so relative imports in src/app.py work correctly
# (src/app.py uses "from config import ..." which expects src/ to be on the path)
src_dir = Path(__file__).parent.parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

import streamlit as st

# Import the workflow builder and runner from the backend
# These use relative imports, so we import as if we're in the src/ directory
from app import build_workflow
from agents.agent_graph import run_graph


@st.cache_resource
def get_workflow():
    """Build and cache the LangGraph workflow once per Streamlit process.
    
    This ensures OpenTelemetry setup (init_tracer, init_http_instrumentation)
    happens only once, and the compiled workflow is reused across user queries.
    """
    return build_workflow()


# Page configuration
st.set_page_config(
    page_title="ResearchFlow AI – Agentic Research Assistant",
    page_icon="🔎",
    layout="wide",
)

# Sidebar with information sections
with st.sidebar:
    st.markdown("### About ResearchFlow AI")
    st.markdown(
        "This agentic system orchestrates a Web+LLM ResearchAgent and an "
        "Oracle trends DatabaseAgent under a root workflow. Each query triggers "
        "parallel research paths that are combined into a comprehensive answer."
    )
    
    st.markdown("---")
    
    st.markdown("### Traces in Jaeger")
    st.markdown(
        "Each request appears in Jaeger under service: `agentic-research-demo`"
    )
    st.markdown("[Open Jaeger →](http://localhost:16686)")
    
    st.markdown("---")
    
    st.markdown("### Tech Stack")
    st.markdown("- LangGraph")
    st.markdown("- Streamlit")
    st.markdown("- Oracle AI Database")
    st.markdown("- OpenTelemetry + Jaeger")

# Main content area with centered layout
left, center, right = st.columns([1, 2, 1])

with center:
    # Header section
    st.markdown("### ResearchFlow AI")
    st.markdown(
        "Agentic AI research assistant combining web research and Oracle database insights."
    )
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Search input and button
    query = st.text_input(
        "Ask a research question",
        placeholder="e.g., What are the latest trends in AI databases?",
        key="user_query",
    )
    
    run_clicked = st.button("Search insights", type="primary", use_container_width=True)
    
    # Initialize result state if not present
    if "result" not in st.session_state:
        st.session_state.result = ""
    
    # Handle search button click
    if run_clicked:
        if not query or not query.strip():
            st.warning("Please enter a question to analyze.")
            st.session_state.result = ""
        else:
            # Get the cached workflow and execute the query
            workflow = get_workflow()
            with st.spinner("Analyzing your question with agentic reasoning..."):
                try:
                    st.session_state.result = run_graph(workflow, query.strip())
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                    st.exception(e)
                    st.session_state.result = ""
    
    # Display results in a styled card container
    if st.session_state.result:
        st.markdown("----")
        st.subheader("Answer")
        
        with st.container():
            # Card-like styling for the answer
            # Convert newlines to HTML breaks for proper display
            formatted_result = st.session_state.result.replace("\n", "<br>")
            st.markdown(
                f"""
                <div style="
                    padding: 1rem 1.5rem;
                    border-radius: 0.75rem;
                    border: 1px solid rgba(200,200,200,0.6);
                    background-color: rgba(250,250,250,0.9);
                ">
                    {formatted_result}
                </div>
                """,
                unsafe_allow_html=True,
            )
        
        st.caption(
            "ResearchFlow AI combines web search, LLM summarization, and Oracle database trends under the hood."
        )

