# ArXiv Research Copilot

> Advanced RAG system for academic paper search, analysis, and Q&A

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## 🎯 Overview

ArXiv Research Copilot is a production-grade Retrieval-Augmented Generation (RAG) system designed to help researchers efficiently search, analyze, and interact with academic papers from ArXiv. Built with modern ML/AI stack including LangChain, OpenAI, and vector databases.

## ✨ Features

- **Semantic Search**: Find relevant papers using natural language queries
- **Multi-Modal Processing**: Handle text, equations, and figures from papers
- **Citation Tracking**: Maintain accurate citations and references
- **Advanced RAG**: Hybrid search with reranking and query expansion
- **Production-Ready API**: FastAPI backend with comprehensive endpoints
- **Interactive UI**: Streamlit demo for easy interaction
- **Extensible Architecture**: Modular design for easy customization

## 🛠️ Tech Stack

- **LLM Framework**: LangChain, LlamaIndex
- **Vector Database**: ChromaDB (local), Qdrant-ready
- **LLM Provider**: OpenAI GPT-4
- **Embeddings**: OpenAI text-embedding-3, Sentence Transformers
- **Backend**: FastAPI, Pydantic
- **Frontend**: Streamlit
- **Data Source**: ArXiv API
- **PDF Processing**: PyPDF2, PyMuPDF

## 🚀 Quick Start

### Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/arxiv-research-copilot.git
cd arxiv-research-copilot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
make install

# Set up environment variables
cp .env.example .env
# Edit .env and add your API keys
```

### Usage
```bash
# Run the API server
make api

# In another terminal, run the UI
make ui
```

Visit http://localhost:8501 for the Streamlit UI or http://localhost:8000/docs for API documentation.

## 📁 Project Structure
```
arxiv-research-copilot/
├── src/
│   ├── ingestion/      # Data download and processing
│   ├── retrieval/      # Vector search and embeddings
│   ├── generation/     # LLM integration and prompts
│   ├── api/            # FastAPI backend
│   ├── ui/             # Streamlit frontend
│   └── utils/          # Shared utilities
├── data/               # Local data storage (gitignored)
├── tests/              # Unit and integration tests
├── notebooks/          # Jupyter notebooks for experiments
├── scripts/            # Utility scripts
└── config/             # Configuration files
```

## 🗺️ Roadmap

- [x] Project setup and architecture
- [ ] ArXiv data ingestion pipeline
- [ ] Vector database implementation
- [ ] Basic RAG with citations
- [ ] Advanced retrieval (hybrid search, reranking)
- [ ] Multi-modal support (equations, figures)
- [ ] Production deployment
- [ ] Evaluation framework
- [ ] Multi-language support

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📧 Contact

Your Name - [@yourhandle](https://twitter.com/yourhandle)

Project Link: [https://github.com/yourusername/arxiv-research-copilot](https://github.com/yourusername/arxiv-research-copilot)
