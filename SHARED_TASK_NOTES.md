# Shared Task Notes - Perplexica Python Refactoring

## Project Goal

Refactor the entire Perplexica project into Python scripts, removing code and documentation unrelated to core functionality.

## Recent Progress (Current Iteration - 2026-01-02)

### Completed This Session (Morning)

1. **Created comprehensive runtime testing suite** ✓
   - Added `test_runtime.py` with integration tests for all components
   - Tests: config loading, SearXNG connection, model registry, classifier, search integration
   - Tests different modes (speed/balanced) and sources (web/academic)
   - Provides helpful error messages and troubleshooting tips

2. **Created detailed setup guide** ✓
   - Added `SETUP_GUIDE.md` with step-by-step instructions
   - Covers: installation, service setup, configuration, usage, troubleshooting
   - Includes examples for Docker + Ollama (local) and cloud services
   - Provides performance tips and architecture overview

3. **Created example configuration** ✓
   - Added `config.example.json` with all settings documented
   - Includes SearXNG, models, optimization modes, and provider configs
   - Easy to customize and copy to config.json

4. **Updated README_PYTHON.md** ✓
   - Quick start guide with minimal steps to get running
   - Links to detailed SETUP_GUIDE.md
   - Clear project status and feature list

### Completed This Session (Previous - Prompts & Dependencies)

1. **Fixed dependency issues** ✓
   - Removed aiodns and pycares packages (compatibility issues with aiohttp)
   - Updated requirements.txt with clear warnings about incompatible packages
   - All modules now import successfully without errors

2. **Integrated official prompts** ✓
   - **Classifier**: Integrated `CLASSIFIER_PROMPT` into classifier.py
     - Uses official query classification prompt from TypeScript codebase
     - Maps classification output to internal format (skipSearch, academicSearch, etc.)
     - Improved error handling with fallback classification

   - **Researcher**: Enhanced researcher.py with prompt structure
     - Added datetime imports and action descriptions
     - Improved iterative research with better logging
     - Simplified prompt that works with current architecture

   - **Writer**: Integrated `get_writer_prompt()` into search_agent.py
     - Uses official answer generation prompt
     - Supports mode-specific instructions (speed/balanced/quality)
     - Proper citation requirements and formatting

3. **All imports working** ✓
   - Tested: perplexica, Classifier, Researcher, SearchAgent, Config
   - All prompts import successfully
   - No more aiohttp/aiodns compatibility errors

4. **Test suite passing** ✓
   - File structure validation
   - Python syntax checking
   - Configuration loading tests
   - All modules can be imported

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
   - `classifier.py`: Query classification with official prompt
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

6. **Prompts** (`perplexica/prompts/`)
   - `classifier.py`: Official classification prompt
   - `researcher.py`: Mode-specific research prompts (speed/balanced/quality)
   - `writer.py`: Answer generation with citation requirements

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

1. **Test with real services**
   - Verify SearXNG integration works with actual instance
   - Test with Ollama provider (or OpenAI/Anthropic)
   - Verify classification produces sensible results
   - Test research logic and iterative search
   - Verify citation formatting in answers
   - Test error handling paths (SearXNG down, LLM failures)

2. **End-to-end CLI testing**
   - `python perplexica.py "test query"` should work
   - Interactive mode should work (`python perplexica.py`)
   - Different modes (speed/balanced/quality) should produce different results
   - Different sources (web/academic/social) should work

### Medium Priority - Enhancements

3. **Add database persistence**
   - Store chat history in SQLite
   - Persist search results for caching
   - Export chat history

4. **Implement streaming responses**
   - Stream answers as they're generated
   - Show research progress in real-time
   - Better UX for long queries

5. **Add file upload support**
   - Process PDFs and documents
   - Semantic search over uploads
   - Combine with web search

6. **Add more providers**
   - Google Gemini
   - Cohere
   - Hugging Face
   - Local OpenAI-compatible APIs

### Low Priority - Nice to Have

7. **Add web interface**
   - FastAPI or Flask backend
   - Simple web UI
   - WebSocket support for streaming

8. **Add tests**
   - Unit tests for core logic
   - Integration tests with mocks
   - Test coverage reporting

9. **Improve documentation**
    - API documentation
    - Contributor guide
    - Architecture diagrams

## Technical Notes

### Current Dependencies

```
aiohttp>=3.10.0
python-dotenv>=1.0.0
```

**Important**: Do NOT install aiodns or pycares. They have compatibility issues that cause `AttributeError` during import. aiohttp works fine without them.

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

### Prompt Integration

All three major components now use official prompts from the TypeScript codebase:

1. **Classifier** (`perplexica/prompts/classifier.py`)
   - Determines if search is needed
   - Generates standalone query from context
   - Selects appropriate sources (web/academic/social)

2. **Researcher** (`perplexica/prompts/researcher.py`)
   - Mode-specific research strategies (speed/balanced/quality)
   - Iterative deepening for quality mode
   - Action descriptions for tool calling

3. **Writer** (`perplexica/prompts/writer.py`)
   - Professional blog-style answers
   - Inline citation requirements [index]
   - Mode-specific depth (quality mode requires 2000+ words)

## Known Issues/Limitations

1. **No runtime testing yet**: Code structure verified but not tested with real services
2. **No persistence**: All data is lost on exit
3. **No streaming**: Responses are generated all at once

## Next Steps Recommendation

**CURRENT ITERATION SHOULD:**

1. **Run the test suite** to verify the current implementation
   ```bash
   python test_setup.py      # Basic structure tests
   python test_runtime.py    # Integration tests (requires services)
   ```

2. **Set up services** if not already running:
   ```bash
   # SearXNG
   docker run -d --name searxng -p 4000:8080 searxng/searxng:latest

   # Ollama
   ollama serve
   ollama pull llama3.2
   ```

3. **Test basic functionality**:
   ```bash
   python perplexica.py "What is the capital of France?"
   ```

4. **Verify all core features work**:
   - [ ] Single query search works
   - [ ] Interactive mode works
   - [ ] Different modes produce different results (speed/balanced/quality)
   - [ ] Different sources work (web/academic/social)
   - [ ] Citations are included in answers
   - [ ] Error handling works (e.g., stop SearXNG and verify graceful error)

5. **Document any issues found** in SHARED_TASK_NOTES.md for next iteration

**If runtime testing reveals bugs, fix them immediately.** This is critical - we need the basic CLI to work reliably before moving on to enhancements.

**Once basic testing passes**, then consider:
- Adding database persistence (medium priority)
- Implementing streaming responses (medium priority)
- Adding more providers (low priority)

**Don't worry about yet:**
- File uploads
- Web interface
- Widgets and extras

Focus on getting the basic CLI search working reliably with real services first.

## Files Created/Modified

```
perplexica.py                 # Main CLI entry point
test_setup.py               # Basic test suite
test_runtime.py             # Integration tests (NEW)
requirements.txt            # Dependencies (FIXED: removed aiodns)
SETUP_GUIDE.md              # Detailed setup guide (NEW)
config.example.json         # Example configuration (NEW)

perplexica/
├── __init__.py
├── config.py                # Configuration management
├── search_agent.py          # Main orchestration (UPDATED: writer prompt)
├── classifier.py            # Query classification (UPDATED: official prompt)
├── researcher.py            # Research logic (UPDATED: prompt structure)
├── search.py                # SearXNG client
├── utils.py                 # Utilities
├── prompts/                 # Prompt templates
│   ├── __init__.py
│   ├── classifier.py        # Classification prompt (INTEGRATED)
│   ├── researcher.py        # Research prompts (INTEGRATED)
│   └── writer.py            # Writer prompt (INTEGRATED)
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
✓ Runtime imports - All modules import without errors
✗ Runtime testing - Not tested with real services yet

## Testing Checklist

Before considering the core "done", verify:

- [x] All files have valid syntax
- [x] Configuration loads correctly
- [x] Import all modules without errors
- [ ] `python perplexica.py "test query"` works
- [ ] Interactive mode works (`python perplexica.py`)
- [ ] SearXNG integration returns results
- [ ] LLM provider generates responses
- [ ] Classification produces sensible results
- [ ] Citations/sources are included in answers
- [ ] Error handling works (e.g., SearXNG down)
- [ ] Different modes (speed/balanced/quality) work
- [ ] Different sources (web/academic/social) work

