# Perplexica - Python Version

Privacy-focused AI-powered search engine, refactored to Python.

## Features

- **Multiple LLM Providers**: Support for Anthropic (Claude), OpenAI, Ollama, and compatible APIs
- **Smart Search Modes**: Speed, Balanced, and Quality optimization modes
- **Flexible Sources**: Web, academic, and social search sources
- **Privacy-Focused**: Uses SearXNG for private search
- **Local-First**: Can run entirely on your own hardware

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure

```bash
cp config.example.json config.json
# Edit config.json with your API keys and settings
```

### 3. Run

```bash
# Single query
python perplexica.py "What is Python?"

# Interactive mode
python perplexica.py

# Different modes
python perplexica.py "Explain ML" --mode speed
python perplexica.py "Explain ML" --mode balanced
python perplexica.py "Explain ML" --mode quality

# Different sources
python perplexica.py "Search" --sources academic
python perplexica.py "Search" --sources social
```

## Configuration

Edit `config.json` to configure:

- **LLM Provider**: Add your API key for Anthropic, OpenAI, or use Ollama
- **Search Engine**: Configure SearXNG URL (default: http://localhost:4000)
- **Optimization Modes**: Adjust search depth and iterations per mode
- **SSL Verification**: Disable for development (not recommended for production)

### Environment Variables

You can override config with environment variables:

- `ANTHROPIC_API_KEY` or `ANTHROPIC_AUTH_TOKEN`
- `ANTHROPIC_BASE_URL` (for custom endpoints)
- `OPENAI_API_KEY`
- `SEARXNG_URL`

## SearXNG Setup

Perplexica requires a SearXNG instance for search.

### Using Docker (Recommended)

```bash
# Create settings.yml
mkdir searxng
cat > searxng/settings.yml << EOF
use_default_settings: true
server:
  secret_key: "$(openssl rand -hex 32)"
  limiter: false
  methods:
    GET: []
    POST: []
search:
  safe_search: 0
EOF

# Run SearXNG
docker run -d \
  --name searxng \
  -p 4000:8080 \
  -v "$(pwd)/searxng/settings.yml:/etc/searxng/settings.yml:ro" \
  searxng/searxng:latest
```

See `SEARXNG_SETUP.md` for detailed instructions.

## Testing

```bash
# Basic setup tests
python test_setup.py

# Dry-run tests with mocks
python test_dry_run.py

# Full integration tests (requires services)
python test_runtime.py

# Health check
python check_health.py
```

## Project Structure

```
perplexica/
├── __init__.py
├── config.py              # Configuration management
├── search_agent.py        # Main orchestration
├── classifier.py          # Query classification
├── researcher.py          # Research logic
├── search.py              # SearXNG client
├── utils.py               # Utilities
├── prompts/               # Prompt templates
└── models/                # LLM providers
    ├── base.py
    ├── registry.py
    ├── ollama_provider.py
    ├── openai_provider.py
    └── anthropic_provider.py
```

## Requirements

- Python 3.10+
- aiohttp >= 3.10.0
- python-dotenv >= 1.0.0

**Note**: Do not install aiodns or pycares (compatibility issues).

## License

MIT License - See LICENSE file for details.

## Acknowledgments

Based on the original [Perplexica](https://github.com/ItzCrazyKns/Perplexica) project.
