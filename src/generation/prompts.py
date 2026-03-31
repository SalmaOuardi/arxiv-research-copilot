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


# -- Claim Extractor Prompt --

CLAIM_EXTRACTOR_TEMPLATE = """You are a research analyst reading an excerpt from an academic paper.

Paper: "{title}" ({published})
Authors: {authors}

Excerpt:
{chunks}

Task: In 2-4 sentences, state what this paper specifically claims or contributes \
regarding "{concept}". Be precise. Only use what is in the excerpt above — do not \
add outside knowledge.

Claim:"""


# -- Narrative Generator Prompt --

NARRATIVE_GENERATOR_TEMPLATE = """You are a science historian writing about the evolution of a research idea.

Concept: "{concept}"

Below is a chronological list of papers and what each one claimed:

{timeline}

Write a flowing narrative (4-8 paragraphs) tracing how "{concept}" evolved over time. \
Show how later papers built on, challenged, or refined earlier ones. \
Cite each paper as (Author et al., YEAR [arxiv_id]).

Narrative:"""


# -- Contradiction Detector Prompt --

CONTRADICTION_DETECTOR_TEMPLATE = """You are a critical research analyst.

Concept: "{concept}"

Paper A: "{title_a}" ({year_a})
Claim: {claim_a}

Paper B: "{title_b}" ({year_b})
Claim: {claim_b}

Do these two claims contradict each other regarding "{concept}"?
Answer YES or NO on the first line, then explain in 1-2 sentences.

Answer:"""
