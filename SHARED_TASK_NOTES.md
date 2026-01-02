# Shared Task Notes - Perplexica Python Refactoring

## Project Goal

Refactor the entire Perplexica project into Python scripts, removing code and documentation unrelated to core functionality.

## Recent Progress (Current Iteration)

### Completed This Session

1. **Fixed async/sync boundary** in `perplexica.py`
   - Converted main() to use `asyncio.run()` properly
   - Separated sync and async code paths
   - Added proper error handling in CLI layer

2. **Added comprehensive error handling**
   - Search errors: `SearchError`, `SearxngConnectionError` exceptions
   - Connection failures, timeouts, non-JSON responses
   - Graceful degradation with helpful error messages
   - Fallback responses when LLM fails

3. **Added original prompts from TypeScript code**
   - `perplexica/prompts/classifier.py`: Query classification prompt
   - `perplexica/prompts/researcher.py`: Speed/balanced/quality research prompts
   - `perplexica/prompts/writer.py`: Answer generation prompt

4. **Fixed type hints and return values**
   - Search methods now return `Dict[str, Any]` instead of `List`
   - Consistent error handling across modules

5. **Created test suite** (`test_setup.py`)
   - File structure validation
   - Python syntax checking
   - Configuration loading tests
   - All tests passing ✓

### What Was Already Implemented (Previous Iterations)

1. **Main Entry Point** (`perplexica.py`)
   - Command-line interface with argparse
   - Single query and interactive modes
   - Support for various options (model, sources, mode)

2. **Configuration Management** (`perplexica/config.py`)
   - JSON-based configuration
   - Environment variable overrides
   - Support for multiple model providers

3. **Search Architecture**
   - `search_agent.py`: Main orchestration with error handling
   - `classifier.py`: Query classification logic
   - `researcher.py`: Multi-step research implementation
   - `search.py`: SearXNG integration with proper error handling

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

### What Was Removed (Intentionally Not Implemented)

- **Frontend**: All React/Next.js UI components
- **Database**: SQLite, Drizzle ORM, chat/message persistence
- **File Uploads**: UploadManager, document processing
- **Widgets**: Weather, stock, calculation widgets
- **Complex Session Management**: SSE streaming, block updates
- **Theme System**: UI theming and styling
- **Setup Flow**: Initial configuration wizard

## What Still Needs to Be Done

### High Priority - Core Functionality

1. **Fix dependency issues**
   - aiohttp has dependency conflicts with aiodns/pycares
   - Need to update requirements or provide workaround
   - Consider using httpx as alternative to aiohttp

2. **Test with real services**
   - Verify SearXNG integration works with actual instance
   - Test with Ollama provider
   - Verify classification and research logic
   - Test error handling paths

3. **Update prompts integration**
   - Currently prompts are defined but not used by classifier/researcher
   - Need to integrate `perplexica/prompts/classifier.py` into classifier.py
   - Need to integrate `perplexica/prompts/researcher.py` into researcher.py
   - Need to integrate `perplexica/prompts/writer.py` into search_agent.py

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

### Current Dependencies

```
aiohttp>=3.10.0
python-dotenv>=1.0.0
```

**Known Issue**: There's a compatibility issue with `aiohttp` and `aiodns`/`pycares` that causes import errors. The code structure is correct but dependencies need to be resolved for runtime testing.

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
- Proper error handling for connection failures

Results are standardized to a common format.

## Known Issues/Limitations

1. **Dependency conflicts**: aiohttp/aiodns import errors prevent full testing
2. **No persistence**: All data is lost on exit
3. **Prompts not integrated**: Prompt files exist but aren't used by actual code
4. **No runtime testing**: Code structure verified but not tested with real services

## Next Steps Recommendation

**Immediate next iteration should:**

1. Fix the dependency issue (either resolve aiodns conflict or switch to httpx)
2. Integrate the prompt files into actual classifier/researcher/writer code
3. Test with a real SearXNG instance
4. Test with a real LLM (Ollama or OpenAI)
5. Verify end-to-end search flow works

**Don't worry about yet:**
- Database persistence
- File uploads
- Web interface
- More providers
- Widgets and extras

Focus on getting the basic CLI search working reliably first.

## Files Created/Modified

```
perplexica.py                 # Main CLI entry point (FIXED: async/sync)
test_setup.py               # Basic test suite (NEW)
requirements.txt            # Updated dependencies

perplexica/
├── __init__.py
├── config.py                # Configuration management
├── search_agent.py          # Main orchestration (UPDATED: error handling)
├── classifier.py            # Query classification
├── researcher.py            # Research logic
├── search.py                # SearXNG client (UPDATED: error handling)
├── utils.py                 # Utilities
├── prompts/                 # NEW: Prompt templates
│   ├── __init__.py
│   ├── classifier.py
│   ├── researcher.py
│   └── writer.py
└── models/
    ├── __init__.py
    ├── base.py              # Abstract base classes
    ├── registry.py          # Model registry
    ├── ollama_provider.py   # Ollama provider
    ├── openai_provider.py   # OpenAI provider
    └── anthropic_provider.py # Anthropic provider
```

## Testing Status

✓ File structure - All required files exist
✓ Python syntax - All files compile successfully
✓ Configuration - Config structure is valid
✗ Runtime imports - Blocked by dependency issues

## Testing Checklist

Before considering the core "done", verify:

- [x] All files have valid syntax
- [x] Configuration loads correctly
- [ ] Import all modules without errors (blocked by aiohttp)
- [ ] `python perplexica.py "test query"` works
- [ ] Interactive mode works (`python perplexica.py`)
- [ ] SearXNG integration returns results
- [ ] Ollama provider generates responses
- [ ] Classification produces sensible results
- [ ] Citations/sources are included in answers
- [ ] Error handling works (e.g., SearXNG down)
- [ ] Different modes (speed/balanced/quality) work

