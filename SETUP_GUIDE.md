# Perplexica Python - Setup and Testing Guide

This guide will help you set up and test the Python refactored version of Perplexica.

## Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- (Optional) Docker for running SearXNG
- (Optional) Ollama for local LLM, or API keys for OpenAI/Anthropic

## Installation

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

**Important**: Do NOT install aiodns or pycares manually. They have compatibility issues with aiohttp.

### 2. Verify Installation

Run the basic setup test:

```bash
python test_setup.py
```

You should see:
```
✓ File Structure
✓ Syntax
✓ Configuration
✓ All tests passed!
```

## Service Setup

You need two services running: SearXNG (search) and an LLM provider.

### Option A: SearXNG + Ollama (Recommended for Local Testing)

#### 1. Start SearXNG

Using Docker:
```bash
docker run -d --name searxng \
  -p 4000:8080 \
  -e BASE_URL=http://localhost:4000 \
  searxng/searxng:latest
```

Wait 30-60 seconds for it to start, then verify:
```bash
curl http://localhost:4000
```

#### 2. Install and Start Ollama

**macOS/Linux:**
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama server
ollama serve

# In another terminal, pull a model
ollama pull llama3.2
```

**Verify Ollama:**
```bash
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2",
  "prompt": "Say hello"
}'
```

#### 3. Test the Setup

```bash
python test_runtime.py
```

### Option B: Public SearXNG + OpenAI/Anthropic

#### 1. Use Public SearXNG Instance

Set environment variable:
```bash
export SEARXNG_URL=https://search.example.com  # Replace with actual instance
```

Or edit `config.json` after first run.

#### 2. Configure OpenAI

```bash
export OPENAI_API_KEY=your_api_key_here
```

#### 3. Configure Anthropic (Alternative)

```bash
export ANTHROPIC_API_KEY=your_api_key_here
```

#### 4. Test the Setup

```bash
python test_runtime.py
```

## Configuration

### Default Configuration

The first time you run Perplexica, it creates a `config.json` file with defaults:

```json
{
  "version": 1,
  "search": {
    "searxng_url": "http://localhost:4000",
    "timeout": 30,
    "max_results": 10
  },
  "models": {
    "default_chat_model": "ollama:llama3.2",
    "default_embedding_model": "ollama:nomic-embed-text"
  },
  "optimization": {
    "speed": {
      "max_iterations": 2,
      "max_results": 5
    },
    "balanced": {
      "max_iterations": 6,
      "max_results": 10
    },
    "quality": {
      "max_iterations": 25,
      "max_results": 15
    }
  }
}
```

### Environment Variables

You can override config with environment variables:

- `SEARXNG_URL`: URL of SearXNG instance
- `OLLAMA_HOST`: Ollama server URL (default: http://localhost:11434)
- `OPENAI_API_KEY`: OpenAI API key
- `ANTHROPIC_API_KEY`: Anthropic API key
- `DEFAULT_MODEL`: Default model (e.g., ollama:llama3.2, openai:gpt-4, anthropic:claude-sonnet-4)

### Model Selection

Models are specified as `provider:model_name`:

- Ollama: `ollama:llama3.2`, `ollama:mistral`, `ollama:gemma2`
- OpenAI: `openai:gpt-4`, `openai:gpt-4o`, `openai:gpt-3.5-turbo`
- Anthropic: `anthropic:claude-sonnet-4`, `anthropic:claude-opus-4`

## Usage

### Basic Search

```bash
python perplexica.py "What is the capital of France?"
```

### Interactive Mode

```bash
python perplexica.py
```

Then type your questions:
```
You: What is machine learning?
Assistant: [answer with sources]

You: Tell me more about neural networks
Assistant: [follow-up answer with context]

You: quit
```

### Different Modes

Speed mode (fast, less thorough):
```bash
python perplexica.py --mode speed "What is quantum computing?"
```

Balanced mode (default):
```bash
python perplexica.py --mode balanced "What is quantum computing?"
```

Quality mode (slow, most thorough):
```bash
python perplexica.py --mode quality "What is quantum computing?"
```

### Different Sources

Web search (default):
```bash
python perplexica.py --sources web "Latest AI news"
```

Academic search:
```bash
python perplexica.py --sources academic "Machine learning research papers"
```

Social search:
```bash
python perplexica.py --sources social "Trending topics on Twitter"
```

Multiple sources:
```bash
python perplexica.py --sources web academic "Climate change research"
```

### Custom Model

```bash
python perplexica.py --model openai:gpt-4 "Your question"
```

### Verbose Output

For debugging:
```bash
python perplexica.py -v "Your question"
```

## Testing

### Run All Tests

```bash
python test_runtime.py
```

This will test:
1. Configuration loading
2. SearXNG connection
3. Model registry and LLM generation
4. Query classification
5. Full search integration
6. Different optimization modes
7. Different search sources

### Expected Output

If everything is set up correctly:
```
============================================================
TEST: Configuration Loading
============================================================
✓ PASS: Config loaded successfully
✓ PASS: Has key: search
✓ PASS: Has key: models
✓ PASS: Has key: optimization
✓ PASS: SearXNG URL configured: http://localhost:4000

============================================================
TEST: SearXNG Connection
============================================================
✓ PASS: Connected to SearXNG, got 10 results
  First result: Test query result...

[... more tests ...]

============================================================
TEST SUMMARY
============================================================
Passed: 20
Failed: 0
Skipped: 0
Total: 20

✓ All tests passed!
```

## Troubleshooting

### "Cannot connect to host" or "Connection refused"

**Problem**: Can't reach SearXNG

**Solutions**:
1. Make sure SearXNG is running: `docker ps | grep searxng`
2. Check the URL: `curl http://localhost:4000`
3. Update `SEARXNG_URL` environment variable
4. Try a public SearXNG instance

### "LLM generation failed"

**Problem**: Can't reach LLM provider

**Solutions**:
1. **Ollama**: Make sure it's running: `ollama list`
2. **OpenAI**: Check API key: `echo $OPENAI_API_KEY`
3. **Anthropic**: Check API key: `echo $ANTHROPIC_API_KEY`
4. Try a different model with `--model` flag

### "Classification failed"

**Problem**: LLM is not responding correctly

**Solutions**:
1. Check LLM is working: `python test_runtime.py` (look for "Model Registry" test)
2. Try a simpler model (ollama:llama3.2 is reliable)
3. Check API rate limits

### Import Errors

**Problem**: `AttributeError: module 'aiohttp' has no attribute 'ClientSession'`

**Solutions**:
1. Make sure you didn't install aiodns or pycares
2. Reinstall aiohttp: `pip uninstall aiohttp && pip install -r requirements.txt`

### Slow Responses

**Problem**: Searches take too long

**Solutions**:
1. Use speed mode: `--mode speed`
2. Reduce max results in config
3. Use a faster model (e.g., ollama:llama3.2 instead of gpt-4)
4. Check network latency to SearXNG

### Empty Answers or No Citations

**Problem**: Answer doesn't include sources

**Solutions**:
1. Check SearXNG is returning results: `curl http://localhost:4000/search?q=test`
2. Try a different query (some queries might not have good search results)
3. Check verbose mode: `python perplexica.py -v "your query"`

## Performance Tips

### For Speed

- Use `--mode speed`
- Use smaller models (ollama:llama3.2, openai:gpt-3.5-turbo)
- Reduce `max_results` in config
- Use local Ollama instead of API calls

### For Quality

- Use `--mode quality`
- Use larger models (openai:gpt-4, anthropic:claude-opus-4)
- Increase `max_results` in config
- Enable multiple sources (web + academic)

### For Cost

- Use Ollama (free after download)
- Cache results when possible (future feature)
- Use balanced mode for good quality/speed tradeoff

## Architecture

The Python refactored version consists of:

1. **perplexica.py**: Main CLI entry point
2. **perplexica/config.py**: Configuration management
3. **perplexica/search_agent.py**: Main orchestration logic
4. **perplexica/classifier.py**: Query classification
5. **perplexica/researcher.py**: Multi-step research
6. **perplexica/search.py**: SearXNG client
7. **perplexica/prompts/**: Official prompts from TypeScript version
8. **perplexica/models/**: LLM provider implementations

## What's Different from TypeScript Version

### Removed (Not Core Functionality)
- Frontend (React/Next.js UI)
- Database (SQLite, chat persistence)
- File uploads and document processing
- Widgets (weather, stock, etc.)
- SSE streaming
- Setup wizard

### Kept (Core Functionality)
- Search orchestration
- Query classification
- Multi-step research
- Answer generation with citations
- Multiple LLM providers
- Multiple search sources
- Optimization modes

## Next Steps

Once basic testing is working:

1. ✅ Test with real queries
2. ✅ Try different modes and sources
3. ⬜ Add database persistence (medium priority)
4. ⬜ Implement streaming responses (medium priority)
5. ⬜ Add file upload support (medium priority)
6. ⬜ Add more LLM providers (low priority)
7. ⬜ Add web interface (low priority)

## Contributing

When contributing new features:

1. Keep the core philosophy: simple, focused on search
2. Add tests to `test_runtime.py`
3. Update this guide if adding new configuration options
4. Follow the existing code structure
5. Use official prompts from the TypeScript version when applicable

## License

Same as the original Perplexica project.
