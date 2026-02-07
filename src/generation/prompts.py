"""Prompt templates for the RAG pipeline.

Defines structured prompt templates for different stages of the
generation pipeline including QA, summarization, and citation formatting.
"""

from __future__ import annotations

# -- RAG Question Answering Prompt --

RAG_QA_TEMPLATE = """You are a research assistant specializing in academic papers.
Use the following context from ArXiv papers to answer the user's question.
Always cite your sources using the paper titles and ArXiv IDs.

If the context doesn't contain enough information to answer the question,
say so clearly rather than making up an answer.

Context:
{context}

Question: {question}

Instructions:
- Provide a clear, well-structured answer
- Cite specific papers using [Author et al., ArXiv ID] format
- If multiple papers discuss the topic, synthesize the information
- Highlight any disagreements or different perspectives between papers

Answer:"""


# -- Paper Summarization Prompt --

SUMMARIZE_PAPER_TEMPLATE = """You are a research assistant. Summarize the following
academic paper content in a structured format.

Paper Content:
{paper_text}

Provide a summary with the following sections:
1. **Main Contribution**: What is the key contribution of this paper?
2. **Methodology**: What approach/method does the paper use?
3. **Key Findings**: What are the main results?
4. **Limitations**: What limitations do the authors mention?
5. **Relevance**: Why is this paper important for the field?

Summary:"""


# -- Multi-Document Synthesis Prompt --

SYNTHESIS_TEMPLATE = """You are a research assistant tasked with synthesizing
information from multiple academic papers on a given topic.

Papers and their relevant excerpts:
{papers_context}

Topic: {topic}

Provide a comprehensive synthesis that:
1. Identifies common themes and approaches
2. Highlights key differences between the papers
3. Notes the progression of ideas over time
4. Cites each paper appropriately

Synthesis:"""


# -- Query Expansion Prompt --

QUERY_EXPANSION_TEMPLATE = """You are a research assistant helping to improve
search queries for academic paper retrieval.

Original query: {query}

Generate 3 alternative phrasings of this query that might help find
relevant academic papers. Consider:
- Technical terminology
- Related concepts
- Broader and narrower formulations

Alternative queries (one per line):"""


# -- Citation Formatting Prompt --

CITATION_FORMAT_TEMPLATE = """Format the following paper information as a proper
academic citation:

Title: {title}
Authors: {authors}
Year: {year}
ArXiv ID: {arxiv_id}

Provide the citation in the following formats:
1. APA format
2. BibTeX entry

Citation:"""


# TODO: Add prompt template for comparing two specific papers
# TODO: Add prompt template for extracting methodology details
# TODO: Add prompt template for generating related work sections
# TODO: Add prompt versioning/management system
# TODO: Consider using LangChain PromptTemplate objects for variable validation
