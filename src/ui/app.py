"""Streamlit UI for the ArXiv Research Copilot.

Provides an interactive web interface for searching papers,
asking questions, and exploring results.
"""

from __future__ import annotations

import streamlit as st

# -- Page Configuration --

st.set_page_config(
    page_title="ArXiv Research Copilot",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)


def render_sidebar() -> dict:
    """Render the sidebar with configuration options.

    Returns:
        Dict of user-selected configuration values.
    """
    st.sidebar.title("⚙️ Settings")

    top_k = st.sidebar.slider("Number of results", min_value=1, max_value=20, value=5)

    categories = st.sidebar.multiselect(
        "ArXiv Categories",
        options=["cs.AI", "cs.LG", "cs.CL", "cs.CV", "cs.IR", "stat.ML"],
        default=["cs.AI", "cs.LG"],
    )

    model = st.sidebar.selectbox(
        "LLM Model",
        options=["gpt-4", "gpt-3.5-turbo"],
        index=0,
    )

    return {"top_k": top_k, "categories": categories, "model": model}


def render_search_tab() -> None:
    """Render the paper search interface."""
    st.header("🔍 Paper Search")

    query = st.text_input(
        "Search query",
        placeholder="e.g., transformer attention mechanisms for NLP",
    )

    if st.button("Search", type="primary") and query:
        with st.spinner("Searching papers..."):
            # TODO: Call search API endpoint
            # TODO: Display results with expandable abstracts
            # TODO: Add download/save functionality
            st.info("Search functionality not yet implemented. Connect to the API backend.")


def render_qa_tab() -> None:
    """Render the question answering interface."""
    st.header("💬 Ask a Question")

    question = st.text_area(
        "Your question",
        placeholder="e.g., What are the main advantages of attention mechanisms over RNNs?",
        height=100,
    )

    if st.button("Ask", type="primary") and question:
        with st.spinner("Generating answer..."):
            # TODO: Call Q&A API endpoint
            # TODO: Display answer with formatted citations
            # TODO: Show source documents in expandable sections
            st.info("Q&A functionality not yet implemented. Connect to the API backend.")


def render_ingest_tab() -> None:
    """Render the paper ingestion interface."""
    st.header("📥 Ingest Papers")

    ingest_query = st.text_input(
        "ArXiv search query for ingestion",
        placeholder="e.g., large language models 2024",
    )

    max_papers = st.number_input("Max papers to ingest", min_value=1, max_value=100, value=10)

    if st.button("Ingest Papers", type="primary") and ingest_query:
        with st.spinner("Ingesting papers..."):
            # TODO: Call ingest API endpoint
            # TODO: Show progress bar
            # TODO: Display ingestion summary
            st.info("Ingestion functionality not yet implemented. Connect to the API backend.")


def main() -> None:
    """Main application entry point."""
    st.title("📚 ArXiv Research Copilot")
    st.caption("Semantic search and Q&A over academic papers")

    config = render_sidebar()

    tab_search, tab_qa, tab_ingest = st.tabs(["🔍 Search", "💬 Q&A", "📥 Ingest"])

    with tab_search:
        render_search_tab()

    with tab_qa:
        render_qa_tab()

    with tab_ingest:
        render_ingest_tab()


if __name__ == "__main__":
    main()
