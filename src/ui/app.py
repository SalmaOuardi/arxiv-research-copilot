"""Streamlit UI for the ArXiv Research Copilot."""

from __future__ import annotations

import requests
import streamlit as st

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="ArXiv Copilot",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.title("ArXiv Copilot")
    st.caption("Idea evolution narratives from academic papers")
    st.divider()

    try:
        health = requests.get(f"{API_URL}/health", timeout=3).json()
        st.success(f"API online — {health['indexed_documents']} chunks indexed")
    except Exception:
        st.error("API offline. Run: uvicorn src.api.main:app --reload")

    st.divider()
    max_papers = st.slider("Papers to fetch", min_value=3, max_value=15, value=8)

# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------

tab_narrative, tab_search = st.tabs(["Narrative", "Search"])

# ---------------------------------------------------------------------------
# Narrative tab
# ---------------------------------------------------------------------------

with tab_narrative:
    st.header("Idea Evolution Narrative")
    st.caption("Type a concept — the system fetches relevant ArXiv papers and writes the intellectual history.")

    concept = st.text_input(
        "Concept",
        placeholder="e.g. attention mechanism, reinforcement learning from human feedback",
    )

    if st.button("Generate narrative", type="primary") and concept:
        with st.spinner(f"Fetching papers and generating narrative for '{concept}'... (this takes a few minutes)"):
            try:
                resp = requests.post(
                    f"{API_URL}/narrative",
                    json={"concept": concept, "max_papers": max_papers},
                    timeout=600,
                )
                resp.raise_for_status()
                data = resp.json()
            except requests.exceptions.Timeout:
                st.error("Request timed out. Try a shorter concept or fewer papers.")
                st.stop()
            except Exception as e:
                st.error(f"API error: {e}")
                st.stop()

        # -- Narrative --
        st.subheader("Narrative")
        st.markdown(data["narrative"])

        st.divider()

        # -- Timeline --
        st.subheader(f"Timeline — {len(data['timeline'])} papers")
        for paper in data["timeline"]:
            year = paper["published"][:4] if paper["published"] else "????"
            with st.expander(f"{year} · {paper['title']}"):
                st.caption(f"{paper['authors']} · [{paper['arxiv_id']}](https://arxiv.org/abs/{paper['arxiv_id']})")
                st.markdown(paper["claim"])

        # -- Contradictions --
        if data["contradictions"]:
            st.divider()
            st.subheader(f"Contradictions detected — {len(data['contradictions'])}")
            for c in data["contradictions"]:
                st.warning(
                    f"**{c['paper_a']}** vs **{c['paper_b']}**\n\n{c['explanation']}",
                    icon="⚠️",
                )
        else:
            st.caption("No contradictions detected between consecutive papers.")

        # -- Export --
        st.divider()
        md = f"# {concept}\n\n{data['narrative']}\n\n---\n\n## Timeline\n\n"
        for paper in data["timeline"]:
            year = paper["published"][:4] if paper["published"] else "????"
            md += f"### {year} · {paper['title']}\n{paper['claim']}\n\n"
        st.download_button("Export as markdown", data=md, file_name=f"{concept.replace(' ', '_')}.md")

# ---------------------------------------------------------------------------
# Search tab
# ---------------------------------------------------------------------------

with tab_search:
    st.header("Semantic Search")
    st.caption("Search across all indexed papers.")

    query = st.text_input("Query", placeholder="e.g. transformer self-attention")
    context = st.text_input("Disambiguation context (optional)", placeholder="e.g. machine learning neural network")
    top_k = st.slider("Results", min_value=1, max_value=20, value=5)

    if st.button("Search", type="primary") and query:
        with st.spinner("Searching..."):
            try:
                resp = requests.post(
                    f"{API_URL}/search",
                    json={"query": query, "top_k": top_k, "context": context or None},
                    timeout=30,
                )
                resp.raise_for_status()
                results = resp.json()["results"]
            except Exception as e:
                st.error(f"API error: {e}")
                st.stop()

        st.caption(f"{len(results)} results for '{query}'")
        for r in results:
            with st.expander(f"{r['score']:.3f} · {r['title'] or r['arxiv_id']}"):
                st.caption(f"[{r['arxiv_id']}](https://arxiv.org/abs/{r['arxiv_id']}) · {r['published'][:10]}")
                st.markdown(r["text"])
