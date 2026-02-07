"""Tests for the generation module."""

from __future__ import annotations

import pytest

from src.generation.llm import LLMHandler
from src.generation.prompts import (
    CITATION_FORMAT_TEMPLATE,
    QUERY_EXPANSION_TEMPLATE,
    RAG_QA_TEMPLATE,
    SUMMARIZE_PAPER_TEMPLATE,
    SYNTHESIS_TEMPLATE,
)


class TestPromptTemplates:
    """Tests for prompt templates."""

    def test_rag_qa_template_has_required_variables(self) -> None:
        """Test that RAG QA template contains required placeholders."""
        assert "{context}" in RAG_QA_TEMPLATE
        assert "{question}" in RAG_QA_TEMPLATE

    def test_summarize_template_has_required_variables(self) -> None:
        """Test that summarize template contains required placeholders."""
        assert "{paper_text}" in SUMMARIZE_PAPER_TEMPLATE

    def test_synthesis_template_has_required_variables(self) -> None:
        """Test that synthesis template contains required placeholders."""
        assert "{papers_context}" in SYNTHESIS_TEMPLATE
        assert "{topic}" in SYNTHESIS_TEMPLATE

    def test_query_expansion_template_has_required_variables(self) -> None:
        """Test that query expansion template contains required placeholders."""
        assert "{query}" in QUERY_EXPANSION_TEMPLATE

    def test_citation_format_template_has_required_variables(self) -> None:
        """Test that citation template contains required placeholders."""
        assert "{title}" in CITATION_FORMAT_TEMPLATE
        assert "{authors}" in CITATION_FORMAT_TEMPLATE
        assert "{arxiv_id}" in CITATION_FORMAT_TEMPLATE

    def test_rag_qa_template_formats_correctly(self) -> None:
        """Test that RAG QA template can be formatted."""
        result = RAG_QA_TEMPLATE.format(
            context="Some paper context",
            question="What is attention?",
        )
        assert "Some paper context" in result
        assert "What is attention?" in result


class TestLLMHandler:
    """Tests for LLMHandler class."""

    def test_init_default_values(self) -> None:
        """Test default initialization values."""
        handler = LLMHandler()
        assert handler.provider == "openai"
        assert handler.model == "gpt-4"
        assert handler.temperature == 0.0
        assert handler.max_tokens == 2000

    def test_init_custom_values(self) -> None:
        """Test initialization with custom values."""
        handler = LLMHandler(
            provider="anthropic",
            model="claude-3-sonnet",
            temperature=0.7,
            max_tokens=4000,
        )
        assert handler.provider == "anthropic"
        assert handler.model == "claude-3-sonnet"
        assert handler.temperature == 0.7
        assert handler.max_tokens == 4000

    # TODO: Add test for generate with mocked LLM API
    # TODO: Add test for generate_with_context
    # TODO: Add test for count_tokens
    # TODO: Add test for error handling on API failure
