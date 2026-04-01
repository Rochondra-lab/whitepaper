# Whitepaper Analysis Tool

> ⚠️ **Version V0 — Test / Proof of Concept**
>
> This is a **preliminary test version**. The project is under **active development** and will **evolve significantly** in future iterations. Nothing is set in stone — the architecture, features, and code are expected to change.

## 🚧 Work in Progress

This project is a **proof of concept** aimed at automatically analyzing whitepapers (PDFs, URLs) and extracting summaries and complexity metrics.

## Current Features (V0)

- **PDF Parsing**: Text extraction from whitepaper files
- **Web Parsing**: Content retrieval from URLs
- **Automatic Summarization**: LLM-powered summary generation
- **Complexity Analysis**: Basic metrics on structure and content

## Project Structure

```
whitepaper_analysis/
├── app/                    # Main application
│   └── main.py
├── core/                   # Business logic
│   ├── pdf_parser.py       # PDF Parser
│   ├── web_parser.py       # Web Parser
│   ├── summarizer.py       # LLM Summarization
│   └── complexity_analyzer.py  # Complexity Analysis
└── data/                   # Data (whitepapers, outputs, etc.)
```

## Prerequisites

### Local LLM with Ollama

This tool requires a local LLM running via **Ollama**.

1. Install Ollama: https://ollama.ai
2. Pull a model (e.g., Llama, Mistral):
   ```bash
   ollama pull llama3
   ```
3. Start the Ollama server (runs on `http://localhost:11434` by default)

The code connects to this local Ollama instance for summarization.

## Installation

```bash
# Create virtual environment
python -m venv .venv

# Activate environment
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
python app/main.py
```

## ⚠️ Important Notes

- **V0 Version**: Test code, not production-ready
- **Major changes planned**: Architecture refactoring, new features, parser and summarizer improvements
- **Do not use in production**

---

**Next version**: V1 — Refactored architecture and extended features
