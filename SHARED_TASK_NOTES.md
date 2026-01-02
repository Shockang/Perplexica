# Shared Task Notes - Perplexica Python Refactoring

## Project Goal

Refactor the entire Perplexica project into Python scripts, removing code and documentation unrelated to core functionality.

## What Was Done in This Iteration

### Core Implementation Created

1. **Main Entry Point** (`perplexica.py`)
   - Command-line interface with argparse
   - Single query and interactive modes
   - Support for various options (model, sources, mode)

2. **Configuration Management** (`perplexica/config.py`)
   - JSON-based configuration
   - Environment variable overrides
   - Support for multiple model providers

3. **Search Architecture**
   - `search_agent.py`: Main orchestration (similar to original SearchAgent)
   - `classifier.py`: Query classification logic
   - `researcher.py`: Multi-step research implementation
   - `search.py`: SearXNG integration

4. **Model Providers** (`perplexica/models/`)
   - `base.py`: Abstract base classes for LLM and Embedding
   - `registry.py`: Model registry for provider management
   - `ollama_provider.py`: Ollama (local) provider
   - `openai_provider.py`: OpenAI provider
   - `anthropic_provider.py`: Anthropic/Claude provider

5. **Utilities** (`perplexica/utils.py`)
   - Logging setup
   - Chat history formatting
   - Text manipulation utilities

### What Was Removed (Not Implemented)

These features from the original were intentionally excluded:

- **Frontend**: All React/Next.js UI components
- **Database**: SQLite, Drizzle ORM, chat/message persistence
- **File Uploads**: UploadManager, document processing
- **Widgets**: Weather, stock, calculation widgets
- **Complex Session Management**: SSE streaming, block updates
- **Theme System**: UI theming and styling
- **Setup Flow**: Initial configuration wizard

### Key Architectural Decisions

1. **Async-first**: Uses `asyncio` and `aiohttp` for all I/O operations
2. **Simplified streaming**: Removed complex block-based streaming for simpler approach
3. **In-memory state**: No database persistence (state is ephemeral)
4. **Provider pattern**: Abstract base classes for easy provider addition
5. **Original prompts preserved**: Same system prompts as original

## What Still Needs to Be Done

### High Priority - Core Functionality

1. **Fix main entry point** (`perplexica.py`)
   - Currently synchronous but calls async code
   - Needs to use `asyncio.run()` properly

2. **Test basic functionality**
   - Verify SearXNG integration works
   - Test with Ollama provider
   - Verify classification and research logic

3. **Add error handling**
   - Graceful handling of API failures
   - Better error messages for users
   - Retry logic for network requests

### Medium Priority - Enhancements

4. **Add database persistence**
   - Store chat history in SQLite
   - Persist search results for caching
   - Export chat history

5. **Implement streaming responses**
   - Stream answers as they're generated
   - Show research progress in real-time
   - Better UX for long queries

6. **Add file upload support**
   - Process PDFs and documents
   - Semantic search over uploads
   - Combine with web search

7. **Add more providers**
   - Google Gemini
   - Cohere
   - Hugging Face
   - Local OpenAI-compatible APIs

### Low Priority - Nice to Have

8. **Add web interface**
   - FastAPI or Flask backend
   - Simple web UI
   - WebSocket support for streaming

9. **Add tests**
   - Unit tests for core logic
   - Integration tests with mocks
   - Test coverage reporting

10. **Improve documentation**
    - API documentation
    - Contributor guide
    - Architecture diagrams

## Technical Notes

### Dependencies

The Python version currently only needs:
- `aiohttp` for HTTP requests
- `python-dotenv` for environment variables

This is much lighter than the original Node.js dependencies.

### Model Providers

The provider system is designed to be easily extensible:

1. Inherit from `BaseLLM` or `BaseEmbedding`
2. Implement `generate()` and `stream_generate()` methods
3. Register in `ModelRegistry.get_llm()`

### Configuration

Configuration is loaded in this order:
1. Default values in code
2. `config.json` file
3. Environment variables (highest priority)

### SearXNG Integration

The search client (`perplexica/search.py`) provides:
- General web search
- Academic search (science category)
- Social search (social category)

Results are standardized to a common format.

## Known Issues/Limitations

1. **Main script not tested**: The async/sync boundary needs verification
2. **No persistence**: All data is lost on exit
3. **Limited testing**: Only code structure created, not runtime tested
4. **No streaming**: Original had sophisticated block-based streaming
5. **Missing prompts**: Original prompt files in `src/lib/prompts/` not ported yet

## Next Steps Recommendation

**Immediate next iteration should:**

1. Fix the `perplexica.py` entry point to properly run async code
2. Test with a real SearXNG instance and Ollama
3. Debug any runtime errors
4. Add proper error handling
5. Verify the core search flow works end-to-end

**Don't worry about yet:**
- Database persistence
- File uploads
- Web interface
- More providers
- Widgets and extras

Focus on getting the basic CLI search working reliably first.

## Files Created

```
perplexica.py                 # Main CLI entry point
example_usage.py             # Example usage script
requirements.txt             # Python dependencies
.env.example                 # Environment variables template
config.json.example          # Configuration template
README_PYTHON.md             # Documentation

perplexica/
├── __init__.py
├── config.py                # Configuration management
├── search_agent.py          # Main orchestration
├── classifier.py            # Query classification
├── researcher.py            # Research logic
├── search.py                # SearXNG client
├── utils.py                 # Utilities
└── models/
    ├── __init__.py
    ├── base.py              # Abstract base classes
    ├── registry.py          # Model registry
    ├── ollama_provider.py   # Ollama provider
    ├── openai_provider.py   # OpenAI provider
    └── anthropic_provider.py # Anthropic provider
```

## Testing Checklist

Before considering the core "done", verify:

- [ ] `python perplexica.py "test query"` works
- [ ] Interactive mode works (`python perplexica.py`)
- [ ] SearXNG integration returns results
- [ ] Ollama provider generates responses
- [ ] Classification produces sensible results
- [ ] Citations/sources are included in answers
- [ ] Error handling works (e.g., SearXNG down)
- [ ] Different modes (speed/balanced/quality) work
