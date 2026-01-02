#!/usr/bin/env python3
"""
Basic test script to verify the Python refactoring structure
"""
import sys
from pathlib import Path


def test_file_structure():
    """Test that all required files exist"""
    print("Testing file structure...")

    required_files = [
        "perplexica.py",
        "requirements.txt",
        "perplexica/__init__.py",
        "perplexica/config.py",
        "perplexica/search_agent.py",
        "perplexica/classifier.py",
        "perplexica/researcher.py",
        "perplexica/search.py",
        "perplexica/utils.py",
        "perplexica/models/__init__.py",
        "perplexica/models/base.py",
        "perplexica/models/registry.py",
        "perplexica/models/ollama_provider.py",
        "perplexica/models/openai_provider.py",
        "perplexica/models/anthropic_provider.py",
        "perplexica/prompts/__init__.py",
        "perplexica/prompts/classifier.py",
        "perplexica/prompts/researcher.py",
        "perplexica/prompts/writer.py",
    ]

    missing_files = []
    for file_path in required_files:
        full_path = Path(file_path)
        if not full_path.exists():
            missing_files.append(file_path)
        else:
            print(f"  ✓ {file_path}")

    if missing_files:
        print(f"\n✗ Missing files: {missing_files}")
        return False

    print("\n✓ All required files exist!")
    return True


def test_syntax():
    """Test Python syntax for all files"""
    print("\nTesting Python syntax...")

    import py_compile

    python_files = list(Path("perplexica").rglob("*.py")) + [Path("perplexica.py")]

    errors = []
    for py_file in python_files:
        try:
            py_compile.compile(str(py_file), doraise=True)
            print(f"  ✓ {py_file}")
        except py_compile.PyCompileError as e:
            print(f"  ✗ {py_file}: {e}")
            errors.append((py_file, e))

    if errors:
        print(f"\n✗ Syntax errors in {len(errors)} files")
        return False

    print("\n✓ All files have valid syntax!")
    return True


def test_config():
    """Test configuration loading"""
    print("\nTesting configuration...")

    try:
        # Import config directly (avoiding aiohttp dependency)
        sys.path.insert(0, str(Path.cwd()))
        from perplexica.config import Config

        # Test creating a config instance (which creates default)
        config = Config("/tmp/test_config.json")

        required_keys = ["version", "search", "models", "optimization"]
        for key in required_keys:
            if key not in config.config:
                print(f"  ✗ Missing config key: {key}")
                return False
            print(f"  ✓ Config has key: {key}")

        print("\n✓ Configuration structure is valid!")
        return True

    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("Perplexica Python Refactoring - Basic Tests")
    print("=" * 60)

    results = []

    results.append(("File Structure", test_file_structure()))
    results.append(("Syntax", test_syntax()))
    results.append(("Configuration", test_config()))

    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name}: {status}")

    all_passed = all(result for _, result in results)

    if all_passed:
        print("\n✓ All tests passed!")
        return 0
    else:
        print("\n✗ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
