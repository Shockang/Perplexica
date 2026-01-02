#!/usr/bin/env python3
"""
Service setup helper for Perplexica
Provides interactive setup for required services
"""
import sys
import subprocess
import platform
from pathlib import Path


class ServiceSetupHelper:
    """Helper for setting up Perplexica services"""

    def __init__(self):
        self.os_type = platform.system().lower()
        self.has_docker = self._check_docker()
        self.has_ollama = self._check_ollama()

    def print_header(self, title: str):
        """Print section header"""
        print(f"\n{'='*70}")
        print(f"  {title}")
        print('='*70)

    def _check_command(self, command: str) -> bool:
        """Check if a command is available"""
        try:
            result = subprocess.run(
                ["which", command],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except Exception:
            return False

    def _check_docker(self) -> bool:
        """Check if Docker is available"""
        return self._check_command("docker")

    def _check_ollama(self) -> bool:
        """Check if Ollama is available"""
        return self._check_command("ollama")

    def _run_command(self, command: str, description: str):
        """Run a command and display results"""
        print(f"\n{description}...")
        print(f"Command: {command}")
        response = input("\nRun this command? (y/n): ").strip().lower()

        if response == 'y':
            try:
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    print("✓ Success!")
                    if result.stdout:
                        print(result.stdout)
                    return True
                else:
                    print(f"✗ Failed with error:")
                    print(result.stderr)
                    return False
            except Exception as e:
                print(f"✗ Error: {e}")
                return False
        else:
            print("Skipped.")
            return False

    def setup_searxng(self):
        """Setup SearXNG search service"""
        self.print_header("SearXNG Setup")

        if not self.has_docker:
            print("⚠ Docker is not installed or not in PATH")
            print("\nOptions for running SearXNG:")
            print("\n1. Install Docker:")
            print("   - Mac: https://docs.docker.com/desktop/install/mac-install/")
            print("   - Linux: https://docs.docker.com/engine/install/")
            print("   - Windows: https://docs.docker.com/desktop/install/windows-install/")
            print("\n2. Use a public SearXNG instance:")
            print("   - Set environment variable:")
            print("     export SEARXNG_URL=https://searx.be")
            print("   - Or add to config.json:")
            print('     "search": {"searxng_url": "https://searx.be"}')
            print("\n3. Run SearXNG manually:")
            print("   - See: https://docs.searxng.org/admin/installation.html")
            return False

        print("✓ Docker is available")

        # Check if SearXNG is already running
        result = subprocess.run(
            ["docker", "ps", "-q", "-f", "name=searxng"],
            capture_output=True,
            text=True
        )

        if result.stdout.strip():
            print("✓ SearXNG container is already running")
            return True

        # Check if container exists but is stopped
        result = subprocess.run(
            ["docker", "ps", "-a", "-q", "-f", "name=searxng"],
            capture_output=True,
            text=True
        )

        if result.stdout.strip():
            print("Found existing SearXNG container (stopped)")
            response = input("Start existing container? (y/n): ").strip().lower()
            if response == 'y':
                return self._run_command(
                    "docker start searxng",
                    "Starting SearXNG container"
                )
        else:
            print("No SearXNG container found")
            response = input("Create and start SearXNG container? (y/n): ").strip().lower()
            if response == 'y':
                return self._run_command(
                    "docker run -d --name searxng -p 4000:8080 searxng/searxng:latest",
                    "Creating and starting SearXNG container"
                )

        return False

    def setup_ollama(self):
        """Setup Ollama LLM service"""
        self.print_header("Ollama Setup")

        if not self.has_ollama:
            print("⚠ Ollama is not installed or not in PATH")
            print("\nTo install Ollama:")
            print("   - Mac: https://ollama.ai/download")
            print("   - Linux: curl -fsSL https://ollama.ai/install.sh | sh")
            print("   - Windows: https://ollama.ai/download")
            print("\nAlternative: Use cloud providers")
            print("   - OpenAI: Set OPENAI_API_KEY environment variable")
            print("   - Anthropic: Set ANTHROPIC_API_KEY environment variable")
            return False

        print("✓ Ollama is installed")

        # Check if Ollama is running
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print("✓ Ollama is running")

            # Check for models
            lines = result.stdout.strip().split('\n')
            models = [line.strip() for line in lines[1:] if line.strip()]

            if models:
                print(f"✓ Found {len(models)} model(s):")
                for model in models[:5]:  # Show first 5
                    print(f"   - {model}")

                # Check if llama3.2 is available
                has_llama = any('llama3.2' in m or 'llama-3.2' in m for m in models)
                if not has_llama:
                    print("\n⚠ llama3.2 model not found")
                    response = input("Download llama3.2 model? (y/n): ").strip().lower()
                    if response == 'y':
                        return self._run_command(
                            "ollama pull llama3.2",
                            "Downloading llama3.2 model"
                        )
                return True
            else:
                print("⚠ No models found")
                response = input("Download llama3.2 model? (y/n): ").strip().lower()
                if response == 'y':
                    return self._run_command(
                        "ollama pull llama3.2",
                        "Downloading llama3.2 model"
                    )
        else:
            print("⚠ Ollama is not running")
            response = input("Start Ollama service? (y/n): ").strip().lower()

            if response == 'y':
                # Ollama needs to be started in background
                print("\nTo start Ollama:")
                print("  - Mac/Linux: Run 'ollama serve' in a terminal")
                print("  - Windows: Ollama usually starts automatically")

                if self.os_type == "darwin" or self.os_type == "linux":
                    print("\nStarting Ollama in background...")
                    try:
                        subprocess.Popen(
                            ["ollama", "serve"],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL
                        )
                        print("✓ Ollama started")
                        return True
                    except Exception as e:
                        print(f"✗ Failed to start: {e}")
                        return False
                else:
                    print("\nPlease start Ollama manually and run this script again")
                    return False

        return False

    def setup_cloud_provider(self):
        """Setup cloud LLM provider"""
        self.print_header("Cloud LLM Provider Setup")

        print("Choose a cloud provider:")
        print("\n1. OpenAI (GPT models)")
        print("2. Anthropic (Claude models)")
        print("3. Skip")

        choice = input("\nEnter choice (1-3): ").strip()

        if choice == "1":
            print("\nOpenAI Setup:")
            print("1. Get API key from: https://platform.openai.com/api-keys")
            print("2. Set environment variable:")
            print("   export OPENAI_API_KEY='sk-...'")
            print("\nOr add to config.json:")
            print('  "openai": {"api_key": "sk-..."}')

            api_key = input("\nEnter API key (or press Enter to skip): ").strip()
            if api_key:
                print(f"\nTo use this key, run:")
                print(f"  export OPENAI_API_KEY='{api_key}'")
                print("\nOr add to config.json")
                return True

        elif choice == "2":
            print("\nAnthropic Setup:")
            print("1. Get API key from: https://console.anthropic.com/")
            print("2. Set environment variable:")
            print("   export ANTHROPIC_API_KEY='sk-ant-...'")
            print("\nOr add to config.json:")
            print('  "anthropic": {"api_key": "sk-ant-..."}')

            api_key = input("\nEnter API key (or press Enter to skip): ").strip()
            if api_key:
                print(f"\nTo use this key, run:")
                print(f"  export ANTHROPIC_API_KEY='{api_key}'")
                print("\nOr add to config.json")
                return True

        return False

    def run_interactive_setup(self):
        """Run interactive setup"""
        print("="*70)
        print("  Perplexica - Service Setup Helper")
        print("="*70)
        print("\nThis script helps you set up the required services for Perplexica.")

        # Setup SearXNG
        searxng_ok = self.setup_searxng()

        # Setup LLM provider
        self.print_header("LLM Provider Setup")
        print("\nChoose LLM provider:")
        print("1. Ollama (local, free)")
        print("2. Cloud provider (OpenAI/Anthropic, paid)")

        llm_choice = input("\nEnter choice (1-2): ").strip()

        if llm_choice == "1":
            llm_ok = self.setup_ollama()
        elif llm_choice == "2":
            llm_ok = self.setup_cloud_provider()
        else:
            print("Invalid choice")
            llm_ok = False

        # Summary
        self.print_header("Setup Summary")
        print(f"\nSearXNG: {'✓ Configured' if searxng_ok else '✗ Not configured'}")
        print(f"LLM Provider: {'✓ Configured' if llm_ok else '✗ Not configured'}")

        if searxng_ok and llm_ok:
            print("\n✓ All services configured!")
            print("\nNext steps:")
            print("  1. Run: python check_health.py")
            print("  2. Test: python perplexica.py 'What is the capital of France?'")
        else:
            print("\n⚠ Some services are not configured")
            print("\nYou can:")
            print("  1. Run this script again later")
            print("  2. Manually configure services (see SETUP_GUIDE.md)")
            print("  3. Use cloud services with API keys")


def main():
    """Main entry point"""
    helper = ServiceSetupHelper()
    helper.run_interactive_setup()


if __name__ == "__main__":
    main()
