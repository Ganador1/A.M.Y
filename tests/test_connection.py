"""
Test de conexión y ciclo cognitivo básico de A.M.Y.

1. Verifica que las API keys de Ollama Cloud funcionan
2. Envía un chat simple al modelo GLM 5.1
3. Prueba la rotación de keys (round-robin)
"""
import asyncio
import sys
import os

# Asegura que el directorio del proyecto esté en sys.path
sys.path.insert(0, os.path.dirname(__file__))

from rich.console import Console
from rich.panel import Panel

console = Console()


async def test_connection():
    """Test 1: Verificar conexión con Ollama Cloud."""
    console.print("\n[bold cyan]═══ A.M.Y — Test de Conexión ═══[/bold cyan]\n")

    # Cargar config
    import yaml
    with open("config.yaml") as f:
        config = yaml.safe_load(f)

    llm_config = config["llm"]
    console.print(f"  Provider: [green]{llm_config['provider']}[/green]")
    console.print(f"  Base URL: [green]{llm_config['base_url']}[/green]")
    console.print(f"  Model:    [green]{llm_config['reasoner']['model']}[/green]")

    # Inicializar cliente
    from core.ollama_client import OllamaCloudClient
    client = OllamaCloudClient(llm_config)

    # Health check
    console.print("\n[bold]1. Health Check (verificando API keys)...[/bold]")
    health = await client.health_check()
    for key_name, status in health.items():
        emoji = "✓" if status.get("status") == "ok" else "✗"
        color = "green" if status.get("status") == "ok" else "red"
        console.print(f"  {emoji} [{color}]{key_name}: {status}[/{color}]")

    # Chat simple
    console.print("\n[bold]2. Chat test (enviando mensaje al modelo)...[/bold]")
    try:
        response = await client.chat(
            model=llm_config["reasoner"]["model"],
            messages=[
                {"role": "system", "content": "Eres un asistente conciso. Responde en 1-2 oraciones."},
                {"role": "user", "content": "¿Qué es la inferencia activa (Active Inference)?"},
            ],
            temperature=0.5,
            max_tokens=2048,
        )

        msg = response.get("message", {})
        content = msg.get("content", "") or msg.get("thinking", "Sin respuesta")
        console.print(Panel(content, title="Respuesta del modelo", border_style="green"))
        console.print(f"  Modelo usado:  {response.get('model', '?')}")
        console.print(f"  Tokens eval:   {response.get('eval_count', '?')}")
    except Exception as e:
        console.print(f"  [red]Error en chat: {e}[/red]")
        return False

    # Rotación de keys
    console.print("\n[bold]3. Test de rotación de keys (2 requests consecutivos)...[/bold]")
    for i in range(2):
        try:
            resp = await client.chat(
                model=llm_config["fast"]["model"],
                messages=[
                    {"role": "user", "content": f"Di solo el número {i+1}"},
                ],
                temperature=0.0,
                max_tokens=512,
            )
            msg = resp.get("message", {})
            content = (msg.get("content", "") or msg.get("thinking", "?")).strip()
            console.print(f"  Request {i+1}: respuesta=[green]{content[:100]}[/green]")
        except Exception as e:
            console.print(f"  Request {i+1}: [red]{e}[/red]")

    # JSON format test
    console.print("\n[bold]4. Test formato JSON (como lo usa el reasoning engine)...[/bold]")
    try:
        resp = await client.chat(
            model=llm_config["reasoner"]["model"],
            messages=[
                {
                    "role": "system",
                    "content": "Responde SOLO en JSON válido con la estructura: {\"thought\": \"...\", \"action\": \"...\"}",
                },
                {
                    "role": "user",
                    "content": "Analiza: ¿Qué papel juegan los astrocitos en el glioblastoma?",
                },
            ],
            temperature=0.3,
            max_tokens=2048,
            format_json=True,
        )
        import json
        msg = resp.get("message", {})
        raw = msg.get("content", "") or msg.get("thinking", "{}")
        # Strip markdown code fences
        import re
        m = re.match(r'^```(?:json)?\s*\n(.*?)\n```\s*$', raw.strip(), re.DOTALL)
        content = m.group(1).strip() if m else raw.strip()
        parsed = json.loads(content)
        console.print(f"  [green]JSON válido ✓[/green]")
        console.print(f"  thought: {parsed.get('thought', '?')[:120]}...")
        console.print(f"  action:  {parsed.get('action', '?')[:120]}...")
    except json.JSONDecodeError as e:
        console.print(f"  [red]JSON inválido: {e}[/red]")
        console.print(f"  Raw: {content[:200]}")
    except Exception as e:
        console.print(f"  [red]Error: {e}[/red]")

    await client.close()
    console.print("\n[bold green]═══ Tests completados ═══[/bold green]\n")
    return True


async def test_mini_cycle():
    """Test 5: Mini ciclo cognitivo (sin heartbeat completo)."""
    console.print("\n[bold cyan]═══ A.M.Y — Mini Ciclo Cognitivo ═══[/bold cyan]\n")

    import yaml
    with open("config.yaml") as f:
        config = yaml.safe_load(f)

    from cognition.reasoning import ReasoningEngine

    engine = ReasoningEngine(config["llm"])

    focus = {
        "content": "Investigar mecanismos de resistencia a temozolomida en glioblastoma",
        "source": "goal_stack",
        "priority": 0.9,
        "type": "goal_directed",
    }

    context = {
        "current_goal": config["mission"]["goal"],
        "cycle": 1,
        "recent_thoughts": [],
    }

    console.print("[bold]5. Ejecutando un ciclo de razonamiento...[/bold]")
    console.print(f"  Focus: [yellow]{focus['content']}[/yellow]")

    thought = await engine.reason(focus=focus, context=context)

    console.print(Panel(
        f"Acción:      {thought.get('action_type', '?')}\n"
        f"Observación: {thought.get('observation', '?')[:150]}\n"
        f"Pensamiento: {thought.get('thought', thought.get('content', '?'))[:150]}\n"
        f"Hipótesis:   {thought.get('hypothesis', 'N/A')[:150]}",
        title="Resultado del razonamiento",
        border_style="cyan",
    ))

    if thought.get("action_type") == "research":
        console.print(f"  Query de búsqueda: [green]{thought.get('research_query', '?')}[/green]")
    elif thought.get("action_type") == "decompose_goal":
        console.print(f"  Sub-goals: {thought.get('sub_goals', [])}")

    await engine.client.close()
    console.print("\n[bold green]═══ Mini ciclo completado ═══[/bold green]\n")


async def main():
    success = await test_connection()
    if success:
        await test_mini_cycle()


if __name__ == "__main__":
    asyncio.run(main())
