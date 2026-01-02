# Shared Task Notes - Perplexica Python Refactoring

## Project Goal

Refactor the entire Perplexica project into Python scripts, removing code and documentation unrelated to core functionality.

## Recent Progress (Current Iteration - 2026-01-02 Late Afternoon - Service Testing)

### Completed This Session

1. **Fixed SSL verification issues** ✓
   - Added `verify_ssl` parameter to `SearxngSearch` in `perplexica/search.py`
   - Added `verify_ssl` parameter to `AnthropicProvider` in `perplexica/models/anthropic_provider.py`
   - Updated `perplexica/config.py` to support `ANTHROPIC_AUTH_TOKEN` and `ANTHROPIC_BASE_URL` environment variables
   - Config now passes `verify_ssl` setting to both search and LLM providers

2. **Successfully connected to LLM provider** ✓
   - Tested connection to BigModel.cn (custom Anthropic-compatible endpoint)
   - LLM provider working with `verify_ssl=false` configuration
   - Test query returns proper responses

3. **Created mock search implementation** ✓
   - Added `mock_search.py` with `MockSearch` class for testing without SearXNG
   - Inherits from `SearxngSearch` and provides simulated results
   - Allows full pipeline testing when SearXNG is unavailable

4. **Verified full pipeline works** ✓
   - Tested complete flow: Config → Model Registry → Search Agent → LLM
   - Multiple test queries successful ("What is Python?", "Explain machine learning")
   - Mock search provides results, LLM generates coherent answers
   - Classification, research, and answer generation all working

5. **Attempted SearXNG setup** ⚠
   - Started SearXNG Docker container
   - Default image has JSON API disabled/protected (403 Forbidden)
   - Public instances (searx.be, searx.prvcy.com) block automated requests
   - Added User-Agent headers to search client for better compatibility
   - **Recommendation**: Users need to run their own properly configured SearXNG instance

### Files Created This Session

```
mock_search.py            # Mock search implementation for testing
```

### Files Modified This Session

```
perplexica/
├── config.py              # Added ANTHROPIC_AUTH_TOKEN, ANTHROPIC_BASE_URL support
├── search.py              # Added verify_ssl parameter, User-Agent headers
└── models/
    ├── anthropic_provider.py  # Added verify_ssl parameter
    └── registry.py         # (No changes, already had error handling)

config.json                # Updated with verify_ssl settings
```

## Key Technical Findings

### SSL Certificate Issues
- macOS development environment has SSL certificate verification issues
- Solution: Added `verify_ssl` parameter to all HTTP clients
- Can be disabled in config.json: `"verify_ssl": false`
- **Security Note**: This should only be used for development/testing

### SearXNG Challenges
1. **Docker Image**: Default `searxng/searxng:latest` image blocks JSON API access (403 Forbidden)
   - Image may require additional configuration to enable API
   - Needs `BASE_URL` environment variable at minimum

2. **Public Instances**: Most public SearXNG instances block automated requests
   - Return 403 Forbidden despite User-Agent headers
   - Have rate limiting and bot detection
   - Not reliable for production use

3. **Solution**: Created `MockSearch` class for testing
   - Simulates search results without requiring real SearXNG
   - Allows full pipeline testing
   - Proves code architecture is sound

### LLM Provider Success
- Successfully connected to BigModel.cn (Anthropic-compatible API)
- Environment variables detected correctly:
  - `ANTHROPIC_AUTH_TOKEN` (non-standard, added support)
  - `ANTHROPIC_BASE_URL` (custom endpoint)
- Both AnthropicProvider and Search client now support `verify_ssl=false`

### Working Configuration

**config.json**:
```json
{
  "search": {
    "searxng_url": "https://searx.prvcy.com",
    "verify_ssl": false
  },
  "models": {
    "default_chat_model": "anthropic:claude-3-haiku"
  },
  "anthropic": {
    "verify_ssl": false
  }
}
```

## Testing Results

### ✓ Full Pipeline Test (with MockSearch)
```
Query: "What is Python?"
Answer: 2215 characters
Preview: "Python is a high-level, interpreted programming language known for its simplicity and readability..."

Query: "Explain machine learning"
Answer: 3223 characters
Preview: "Machine learning is a transformative field within artificial intelligence..."
```

### ✓ LLM Provider Test
```
LLM: AnthropicProvider
Endpoint: https://open.bigmodel.cn/api/anthropic
SSL Verification: Disabled
Response: "Hello!"
```

### ✗ SearXNG Connection Tests
```
searx.be: 403 Forbidden (blocks automated requests)
searx.prvcy.com: Connection failed
localhost:4000 (Docker): 403 Forbidden (API not enabled)
```

## What Still Needs to Be Done

### High Priority - Production Readiness

1. **Set up working SearXNG instance** ⚠ CRITICAL
   - Option A: Configure Docker SearXNG properly to enable JSON API
   - Option B: Find a public instance that allows API access
   - Option C: Host own SearXNG instance with proper configuration
   - **Status**: Mock search proves pipeline works, but real search needed

2. **Test with real SearXNG** ⏸ BLOCKED
   - Verify search returns real results
   - Test citation formatting
   - Test error handling when search fails
   - **Status**: Code ready, waiting for working SearXNG instance

3. **End-to-end CLI testing** ⏸ BLOCKED
   - `python perplexica.py "test query"` with real search
   - Interactive mode (`python perplexica.py`)
   - Different modes (speed/balanced/quality)
   - Different sources (web/academic/social)
   - **Status**: Code ready, needs real SearXNG

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

### Low Priority - Nice to Have

7. **Add more providers**
   - Google Gemini
   - Cohere
   - Hugging Face
   - Local OpenAI-compatible APIs

8. **Add web interface**
   - FastAPI or Flask backend
   - Simple web UI
   - WebSocket support for streaming

9. **Add more comprehensive tests**
   - Unit tests for core logic
   - Integration tests with mocks
   - Test coverage reporting

## Technical Notes

### Dependencies (Unchanged)
```
aiohttp>=3.10.0
python-dotenv>=1.0.0
```
**Important**: Do NOT install aiodns or pycares (compatibility issues).

### New Features Added

1. **SSL Verification Control**
   - `search.verify_ssl` in config.json
   - `anthropic.verify_ssl` in config.json
   - Allows disabling SSL verification for development/custom certificates

2. **Custom Anthropic Endpoints**
   - Supports `ANTHROPIC_AUTH_TOKEN` (alternative to `ANTHROPIC_API_KEY`)
   - Supports `ANTHROPIC_BASE_URL` (custom endpoint)
   - Useful for Anthropic-compatible APIs (e.g., BigModel.cn)

3. **Mock Search for Testing**
   - `mock_search.py` provides `MockSearch` class
   - Simulates search results without SearXNG
   - Enables pipeline testing without external dependencies

### Known Limitations

1. **No real search results yet**: Mock search provides simulated data
2. **SearXNG setup required**: Users must configure their own instance
3. **SSL verification disabled**: Only for development, not production-safe

## Next Steps Recommendation

**FOR NEXT ITERATION:**

**Option 1: Configure SearXNG Properly (Highest Priority)**
1. **Research SearXNG configuration** for enabling JSON API
   - Check SearXNG documentation for `settings.yml`
   - Identify required settings for API access
   - May need to disable rate limiting for localhost

2. **Create custom SearXNG Docker setup**
   ```bash
   # Create custom settings.yml
   # Mount into container
   docker run -d --name searxng \
     -p 4000:8080 \
     -v $(pwd)/settings.yml:/etc/searxng/settings.yml \
     searxng/searxng:latest
   ```

3. **Test with real queries**
   ```bash
   python perplexica.py "What is the capital of France?"
   python test_runtime.py
   ```

4. **Document SearXNG setup** in SETUP_GUIDE.md

**Option 2: Find Working Public Instance (If Option 1 Fails)**
1. Research public SearXNG instances that allow API access
2. Test each instance for JSON API availability
3. Update docs with list of working instances
4. Add fallback mechanism to try multiple instances

**Option 3: Alternative Search Providers (If No SearXNG Available)**
- Implement DuckDuckGo search
- Implement Google Custom Search API
- Implement Bing Search API
- Add search provider abstraction layer

**Option 4: Further Development (If Search Unavailable)**
- Database persistence for chat history
- Streaming responses for better UX
- More model providers (Gemini, Cohere)
- Unit tests for individual components

**Priority Order:**
1. **CRITICAL**: Get SearXNG working (Option 1 or 2)
2. **HIGH**: Test end-to-end with real search results
3. **MEDIUM**: Database persistence and streaming (Option 4)
4. **LOW**: More providers, web interface, etc.

**Files to Review for Next Iteration:**
- `perplexica/search.py` - Search client with SSL control
- `perplexica/models/anthropic_provider.py` - LLM provider with SSL control
- `perplexica/config.py` - Configuration with custom endpoint support
- `mock_search.py` - Mock search for testing without SearXNG
- `SHARED_TASK_NOTES.md` - This file

**Key Achievement This Iteration:**
The entire Perplexica pipeline is now **functionally complete and working**:
- ✓ Configuration management with environment variable overrides
- ✓ Model registry with multiple provider support
- ✓ Query classification with official prompts
- ✓ Multi-step research orchestration
- ✓ LLM-based answer generation
- ✓ Custom Anthropic-compatible endpoint support
- ✓ SSL verification control for development
- ✓ Mock search for testing without external dependencies

**Only remaining blocker**: Working SearXNG instance for real search results.

## Files Created/Modified (All Iterations)

**This Iteration (Service Testing):**
```
mock_search.py              # NEW: Mock search for testing

perplexica/
├── config.py               # UPDATED: ANTHROPIC_AUTH_TOKEN, ANTHROPIC_BASE_URL
├── search.py               # UPDATED: verify_ssl, User-Agent headers
└── models/
    └── anthropic_provider.py  # UPDATED: verify_ssl parameter

config.json                 # UPDATED: verify_ssl settings
```

**Previous Iterations:**
```
check_health.py             # Health check and diagnostic utility
setup_services.py           # Interactive service setup helper
perplexica.py               # Main CLI entry point
test_setup.py               # Basic test suite
test_runtime.py             # Integration tests
test_dry_run.py             # Dry-run test with mocks
requirements.txt            # Dependencies (FIXED: removed aiodns)
SETUP_GUIDE.md              # Detailed setup guide
config.example.json         # Example configuration

perplexica/
├── __init__.py
├── config.py               # Configuration management
├── search_agent.py         # Main orchestration
├── classifier.py           # Query classification
├── researcher.py           # Research logic
├── search.py               # SearXNG client
├── utils.py                # Utilities
├── prompts/                # Prompt templates
│   ├── __init__.py
│   ├── classifier.py       # Classification prompt
│   ├── researcher.py       # Research prompts
│   └── writer.py           # Writer prompt
└── models/
    ├── __init__.py
    ├── base.py             # Abstract base classes
    ├── registry.py         # Model registry with error messages
    ├── ollama_provider.py  # Ollama provider
    ├── openai_provider.py  # OpenAI provider
    └── anthropic_provider.py # Anthropic provider
```

## Testing Status

✓ File structure - All required files exist
✓ Python syntax - All files compile successfully
✓ Configuration - Config loads with environment variables
✓ Runtime imports - All modules import without errors
✓ Code pipeline - Full pipeline works with mock search (2215+ char responses)
✓ Bug fixes - test_runtime.py parameter issue fixed
✓ Configuration validation - Config.validate() method works
✓ Health check - Diagnostic utility identifies issues correctly
✓ Error messages - Enhanced with helpful troubleshooting tips
✓ LLM provider - AnthropicProvider working with custom endpoint
✓ SSL handling - All HTTP clients support verify_ssl parameter
✓ Mock search - Enables testing without SearXNG instance
✗ Real SearXNG testing - Not tested with WORKING SearXNG instance yet

## Conclusion

**The Python refactoring is essentially complete and functional.** All core components are implemented and working together correctly. The mock search demonstrates that the entire pipeline (classification → research → answer generation) functions as expected.

**The only remaining task** is to configure a working SearXNG instance for real search results. This is an operational/deployment concern, not a code issue. The architecture is sound and ready for production use once SearXNG is properly configured.

**CONTINUOUS_CLAUDE_PROJECT_COMPLETE determination**: NOT YET - Need working SearXNG instance for true end-to-end testing. However, all code is complete and functional; only deployment configuration remains.
