# Perplexica - Python Version

A privacy-focused AI-powered search engine refactored into Python scripts. This version extracts the core functionality from the original TypeScript/Next.js codebase and provides a simple command-line interface.

## Features

- **Privacy-first**: All search happens through your own SearXNG instance
- **Multiple AI Providers**: Support for Ollama (local), OpenAI, and Anthropic
- **Intelligent Search**: Automatic query classification and multi-step research
- **Source Citations**: All answers include citations to sources
- **Interactive Mode**: Chat interface for continuous conversations

## Prerequisites

1. **Python 3.10+**
2. **SearXNG instance** running locally or remotely
3. **AI Model Provider**:
   - Ollama (recommended for privacy): https://ollama.com
   - OpenAI API key (optional)
   - Anthropic API key (optional)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/Perplexica.git
cd Perplexica
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Setup SearXNG:
```bash
docker run -d -p 4000:8080 searxng/searxng
```

4. Install Ollama (if using local models):
```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model
ollama pull llama3.2
ollama pull nomic-embed-text
```

## Configuration

Create a `.env` file from the example:
```bash
cp .env.example .env
```

Edit `.env` to configure your settings:
```bash
SEARXNG_URL=http://localhost:4000
DEFAULT_MODEL=ollama:llama3.2
```

Or create a `config.json`:
```bash
cp config.json.example config.json
```

## Usage

### Command Line

Single query:
```bash
python perplexica.py "What is quantum computing?"
```

With specific sources:
```bash
python perplexica.py "Latest AI research papers" --sources academic
```

Different optimization modes:
```bash
python perplexica.py "Compare Python vs JavaScript" --mode quality
```

### Interactive Mode

Simply run without arguments:
```bash
python perplexica.py
```

Then type your queries interactively.

### Options

- `query`: Search query (optional for interactive mode)
- `--config`: Path to configuration file (default: config.json)
- `--model`: Override the default model
- `--sources`: Search sources to use (web, academic, social, uploads)
- `--mode`: Optimization mode (speed, balanced, quality)
- `--verbose, -v`: Enable verbose output

### Examples

Search the web:
```bash
python perplexica.py "Best Python web frameworks 2024"
```

Academic search:
```bash
python perplexica.py "Transformer architecture improvements" --sources academic --mode quality
```

Use OpenAI:
```bash
export OPENAI_API_KEY=your_key
python perplexica.py "Explain machine learning" --model openai:gpt-4
```

## Architecture

The Python refactored version maintains the core architecture of the original:

- **perplexica.py**: Main entry point with CLI interface
- **perplexica/config.py**: Configuration management
- **perplexica/search_agent.py**: Main orchestration logic
- **perplexica/classifier.py**: Query classification
- **perplexica/researcher.py**: Multi-step research logic
- **perplexica/search.py**: SearXNG integration
- **perplexica/models/**: AI provider implementations
  - `base.py`: Base classes for LLM and embedding providers
  - `registry.py`: Model registry
  - `ollama_provider.py`: Ollama provider
  - `openai_provider.py`: OpenAI provider
  - `anthropic_provider.py`: Anthropic provider

## Differences from Original

This Python version focuses on the core search functionality and removes:

- **Frontend**: No React/Next.js web interface
- **Database**: No SQLite/chats persistence (state is in-memory)
- **File Uploads**: No document upload/search
- **Widgets**: No weather, stock, or calculation widgets
- **Session Management**: Simplified streaming

The core search intelligence remains the same.

## Future Enhancements

Potential areas for future iterations:

1. **Add database persistence** for chat history
2. **Implement file upload** and semantic search
3. **Add more AI providers** (Cohere, Hugging Face, etc.)
4. **Create web interface** using FastAPI or Flask
5. **Add streaming responses** in real-time
6. **Implement caching** for search results
7. **Add tests** and documentation

## License

This project maintains the same license as the original Perplexica project.
