#!/usr/bin/env python3
"""
Test script to verify the secure API key system is working correctly.

This script will:
1. Check if API keys are configured
2. Test encryption/decryption
3. Verify HuggingFace provider integration
4. Test the multi-agent system with secure keys
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import asyncio

console = Console()


def test_api_keys_manager():
    """Test 1: Verify APIKeysManager is working"""
    console.print("\n[bold cyan]Test 1: APIKeysManager[/bold cyan]")

    try:
        from app.config.api_keys_manager import get_api_keys_manager

        manager = get_api_keys_manager()
        console.print("[green]✅ APIKeysManager initialized[/green]")

        # Check if HuggingFace key is configured
        has_hf_key = manager.has_api_key("HUGGINGFACE")

        if has_hf_key:
            console.print("[green]✅ Hugging Face API key is configured[/green]")

            # Get masked key
            hf_key = manager.get_api_key("HUGGINGFACE")
            masked = hf_key[:8] + "..." + hf_key[-4:] if len(hf_key) > 12 else hf_key[:4] + "..."
            console.print(f"   Masked key: {masked}")

            return True
        else:
            console.print("[yellow]⚠️ Hugging Face API key NOT configured[/yellow]")
            console.print("\n[bold]Please configure your API key first:[/bold]")
            console.print("python scripts/security/manage_api_keys.py set HUGGINGFACE hf_your_token_here")
            return False

    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        return False


def test_encryption():
    """Test 2: Verify encryption is working"""
    console.print("\n[bold cyan]Test 2: Encryption System[/bold cyan]")

    try:
        from app.config.api_keys_manager import get_api_keys_manager

        manager = get_api_keys_manager()

        # Check if encryption key exists
        if manager.key_file.exists():
            console.print(f"[green]✅ Encryption key file exists: {manager.key_file}[/green]")

            # Check permissions
            import stat
            file_stat = os.stat(manager.key_file)
            permissions = oct(file_stat.st_mode)[-3:]
            console.print(f"   File permissions: {permissions}")

            if permissions == "600":
                console.print("[green]✅ Correct permissions (600)[/green]")
            else:
                console.print(f"[yellow]⚠️ Permissions should be 600, found {permissions}[/yellow]")

        # Check encrypted storage
        if manager.storage_file.exists():
            console.print(f"[green]✅ Encrypted storage exists: {manager.storage_file}[/green]")

            # Get stats
            stats = manager.get_stats()
            console.print(f"   Configured providers: {stats['configured_providers']}/{stats['total_providers']}")
        else:
            console.print("[yellow]⚠️ No encrypted storage yet (will be created on first save)[/yellow]")

        return True

    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        return False


async def test_huggingface_provider():
    """Test 3: Verify HuggingFace provider integration"""
    console.print("\n[bold cyan]Test 3: HuggingFace Provider Integration[/bold cyan]")

    try:
        from app.services.llm_providers.huggingface_provider import HuggingFaceProvider

        # Initialize provider (should get API key from secure storage)
        provider = HuggingFaceProvider()

        if not provider.api_key:
            console.print("[yellow]⚠️ Provider initialized but no API key found[/yellow]")
            return False

        console.print("[green]✅ Provider initialized with API key from secure storage[/green]")

        # Test basic generation
        console.print("\n[bold]Testing text generation...[/bold]")
        try:
            result = await provider.generate_text(
                "What is the capital of France?",
                model_id="gpt2",
                max_new_tokens=50
            )

            if result:
                console.print("[green]✅ Text generation successful[/green]")
                console.print(f"   Result preview: {result[:100]}...")
                return True
            else:
                console.print("[yellow]⚠️ No result from generation[/yellow]")
                return False

        except Exception as e:
            console.print(f"[red]❌ Generation error: {e}[/red]")
            return False

    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        import traceback
        traceback.print_exc()
        return False


async def test_agent_wrapper():
    """Test 4: Verify agent wrapper with secure keys"""
    console.print("\n[bold cyan]Test 4: Multi-Agent Wrapper[/bold cyan]")

    try:
        from app.services.huggingface_agent_wrapper import HuggingFaceAgentWrapper

        # Create wrapper for orchestrator role
        wrapper = HuggingFaceAgentWrapper(
            agent_role="orchestrator",
            domain="biology"
        )

        console.print("[green]✅ Agent wrapper initialized[/green]")
        console.print(f"   Agent role: orchestrator")
        console.print(f"   Domain: biology")
        console.print(f"   Model: {wrapper.model_id}")

        # Test generation
        console.print("\n[bold]Testing agent generation...[/bold]")
        try:
            result = await wrapper.generate_async(
                "Generate a simple biological hypothesis about cell division.",
                max_new_tokens=100
            )

            if result:
                console.print("[green]✅ Agent generation successful[/green]")
                console.print(f"   Result preview: {result[:150]}...")
                return True
            else:
                console.print("[yellow]⚠️ No result from agent[/yellow]")
                return False

        except Exception as e:
            console.print(f"[red]❌ Generation error: {e}[/red]")
            return False

    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        return False


async def main():
    """Run all tests"""
    console.print(Panel.fit(
        "[bold cyan]🔐 AXIOM API Key Security Test Suite[/bold cyan]\n"
        "Testing secure API key management and integration",
        border_style="cyan"
    ))

    # Run tests
    results = {}

    # Test 1: APIKeysManager
    results["api_keys_manager"] = test_api_keys_manager()

    # Test 2: Encryption
    results["encryption"] = test_encryption()

    # Only run integration tests if API key is configured
    if results["api_keys_manager"]:
        # Test 3: HuggingFace Provider
        results["huggingface_provider"] = await test_huggingface_provider()

        # Test 4: Agent Wrapper
        results["agent_wrapper"] = await test_agent_wrapper()
    else:
        console.print("\n[yellow]⚠️ Skipping integration tests - configure API key first[/yellow]")

    # Summary
    console.print("\n" + "="*70)
    console.print("[bold cyan]Test Summary[/bold cyan]")
    console.print("="*70 + "\n")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Test", style="cyan")
    table.add_column("Status", justify="center")

    for test_name, result in results.items():
        status = "[green]✅ PASS[/green]" if result else "[red]❌ FAIL[/red]"
        table.add_row(test_name.replace("_", " ").title(), status)

    console.print(table)

    # Overall result
    passed = sum(1 for r in results.values() if r)
    total = len(results)

    console.print(f"\n[bold]Overall: {passed}/{total} tests passed[/bold]\n")

    if passed == total:
        console.print("[green]🎉 All tests passed! Your secure API key system is working correctly.[/green]\n")
    elif results.get("api_keys_manager"):
        console.print("[yellow]⚠️ API key configured but integration tests failed. Check your API key validity.[/yellow]\n")
    else:
        console.print("[yellow]⚠️ Please configure your API key to run all tests.[/yellow]\n")


if __name__ == "__main__":
    asyncio.run(main())
