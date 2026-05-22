#!/usr/bin/env python3
"""
Test COMPLETO del Sistema Multi-Agente AXIOM ATLAS
Simula una investigación científica real de principio a fin
"""

import sys
import asyncio
from datetime import datetime
sys.path.insert(0, '.')

from app.config.api_keys_manager import get_api_key
from app.services.llm_providers.huggingface_provider import (
    HuggingFaceProvider,
    HFInferenceRequest
)
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.markdown import Markdown

console = Console()

# Tema de investigación real
RESEARCH_TOPIC = """
Investigar el potencial de CRISPR-Cas9 para tratar la enfermedad de Huntington,
una enfermedad neurodegenerativa causada por mutaciones en el gen HTT.
Específicamente, evaluar la viabilidad de edición genética somática para
silenciar el alelo mutante preservando el alelo salvaje.
"""

class ResearchWorkflow:
    """Workflow completo de investigación multi-agente"""

    def __init__(self):
        api_key = get_api_key('HUGGINGFACE')
        self.provider = HuggingFaceProvider(api_key=api_key)
        self.results = {}

    async def run_agent(self, agent_name: str, agent_role: str, prompt: str, max_tokens: int = 300):
        """Ejecutar un agente específico"""

        model_id = self.provider.AGENT_MODEL_MAP[agent_role]

        console.print(f"\n[bold cyan]{'='*80}[/bold cyan]")
        console.print(f"[bold yellow]🤖 AGENTE: {agent_name.upper()}[/bold yellow]")
        console.print(f"[cyan]Modelo: {model_id}[/cyan]")
        console.print(f"[dim]Rol: {agent_role}[/dim]")
        console.print(f"[bold cyan]{'='*80}[/bold cyan]\n")

        console.print(Panel(
            f"[bold]Prompt:[/bold]\n{prompt[:200]}...",
            title="Entrada",
            border_style="blue"
        ))

        request = HFInferenceRequest(
            model_id=model_id,
            prompt=prompt,
            max_new_tokens=max_tokens,
            temperature=0.7
        )

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(f"Generando respuesta con {model_id.split('/')[-1]}...", total=None)

            response = await self.provider.generate_text(request)
            progress.update(task, completed=True)

        if response.success:
            console.print(Panel(
                response.generated_text,
                title=f"✅ Respuesta de {agent_name}",
                border_style="green"
            ))

            console.print(f"\n[dim]📊 Tokens: {response.tokens_generated} | Latencia: {response.latency_ms:.0f}ms[/dim]\n")

            self.results[agent_name] = {
                "response": response.generated_text,
                "tokens": response.tokens_generated,
                "latency": response.latency_ms,
                "model": model_id
            }

            return response.generated_text
        else:
            console.print(f"[red]❌ Error: {response.error}[/red]")
            return None

    async def execute_research_workflow(self):
        """Ejecutar workflow completo de investigación"""

        console.print(Panel.fit(
            "[bold cyan]🔬 AXIOM ATLAS - Sistema Multi-Agente de Investigación Científica[/bold cyan]\n"
            "[yellow]Prueba con Datos Científicos Reales[/yellow]",
            border_style="cyan"
        ))

        console.print(f"\n[bold]📋 TEMA DE INVESTIGACIÓN:[/bold]")
        console.print(Panel(RESEARCH_TOPIC.strip(), border_style="yellow"))

        # ========================================================================
        # FASE 1: ORCHESTRATOR - Planificación de la investigación
        # ========================================================================

        console.print(f"\n[bold magenta]{'='*80}[/bold magenta]")
        console.print(f"[bold magenta]FASE 1: PLANIFICACIÓN DE INVESTIGACIÓN[/bold magenta]")
        console.print(f"[bold magenta]{'='*80}[/bold magenta]")

        orchestrator_prompt = f"""You are a scientific research coordinator. Create a detailed research plan for:

{RESEARCH_TOPIC}

Provide:
1. Research objectives (2-3 specific goals)
2. Methodology outline
3. Key experiments to conduct
4. Expected timeline
5. Success criteria

Be specific and scientific."""

        plan = await self.run_agent(
            "Orchestrator",
            "orchestrator",
            orchestrator_prompt,
            max_tokens=400
        )

        await asyncio.sleep(2)

        # ========================================================================
        # FASE 2: BIO_HYPOTHESIS - Generación de hipótesis biológica
        # ========================================================================

        console.print(f"\n[bold magenta]{'='*80}[/bold magenta]")
        console.print(f"[bold magenta]FASE 2: GENERACIÓN DE HIPÓTESIS BIOLÓGICA[/bold magenta]")
        console.print(f"[bold magenta]{'='*80}[/bold magenta]")

        bio_prompt = f"""Based on this research plan:

{plan[:500]}...

Generate 2-3 specific, testable biological hypotheses about using CRISPR-Cas9 to treat Huntington's disease.
Each hypothesis should:
- Be falsifiable
- Include molecular mechanisms
- Predict specific outcomes
- Be testable with current technology

Format each hypothesis clearly."""

        hypotheses = await self.run_agent(
            "Bio Hypothesis Generator",
            "bio_hypothesis",
            bio_prompt,
            max_tokens=350
        )

        await asyncio.sleep(2)

        # ========================================================================
        # FASE 3: PHYSCHEM_CODER - Diseño experimental y código
        # ========================================================================

        console.print(f"\n[bold magenta]{'='*80}[/bold magenta]")
        console.print(f"[bold magenta]FASE 3: DISEÑO EXPERIMENTAL Y CÓDIGO[/bold magenta]")
        console.print(f"[bold magenta]{'='*80}[/bold magenta]")

        coder_prompt = f"""Design a computational analysis pipeline for CRISPR-Cas9 off-target prediction.

Write Python code that:
1. Loads a guide RNA sequence
2. Scans the human genome for potential off-target sites
3. Scores each site based on mismatches
4. Returns top 10 most likely off-target sites

Use BioPython-style pseudocode. Include comments explaining the algorithm."""

        code = await self.run_agent(
            "PhysChem Coder",
            "physchem_coder",
            coder_prompt,
            max_tokens=400
        )

        await asyncio.sleep(2)

        # ========================================================================
        # FASE 4: SCIENTIFIC_REASONER - Análisis matemático
        # ========================================================================

        console.print(f"\n[bold magenta]{'='*80}[/bold magenta]")
        console.print(f"[bold magenta]FASE 4: ANÁLISIS MATEMÁTICO Y ESTADÍSTICO[/bold magenta]")
        console.print(f"[bold magenta]{'='*80}[/bold magenta]")

        math_prompt = f"""Calculate the statistical power needed for a CRISPR-Cas9 clinical trial.

Given:
- Expected editing efficiency: 60% ± 10%
- Minimum clinically significant improvement: 20%
- Alpha = 0.05 (95% confidence)
- Beta = 0.20 (80% power)

Calculate:
1. Required sample size per group
2. Expected effect size (Cohen's d)
3. Probability of detecting true effect

Show your mathematical reasoning."""

        math_analysis = await self.run_agent(
            "Scientific Reasoner",
            "scientific_reasoner",
            math_prompt,
            max_tokens=350
        )

        await asyncio.sleep(2)

        # ========================================================================
        # FASE 5: REVIEWER - Evaluación crítica
        # ========================================================================

        console.print(f"\n[bold magenta]{'='*80}[/bold magenta]")
        console.print(f"[bold magenta]FASE 5: REVISIÓN CRÍTICA[/bold magenta]")
        console.print(f"[bold magenta]{'='*80}[/bold magenta]")

        review_prompt = f"""Critically evaluate this CRISPR-Cas9 research proposal:

HYPOTHESES:
{hypotheses[:400]}...

COMPUTATIONAL APPROACH:
{code[:400]}...

Provide:
1. 3 major strengths
2. 3 potential weaknesses or risks
3. Ethical considerations
4. Suggestions for improvement

Be constructive but rigorous."""

        review = await self.run_agent(
            "Scientific Reviewer",
            "reviewer",
            review_prompt,
            max_tokens=400
        )

        await asyncio.sleep(2)

        # ========================================================================
        # FASE 6: PUBLISHER - Generación de reporte
        # ========================================================================

        console.print(f"\n[bold magenta]{'='*80}[/bold magenta]")
        console.print(f"[bold magenta]FASE 6: GENERACIÓN DE REPORTE CIENTÍFICO[/bold magenta]")
        console.print(f"[bold magenta]{'='*80}[/bold magenta]")

        publisher_prompt = f"""Write an abstract for a research paper titled:

"CRISPR-Cas9 Gene Editing for Huntington's Disease: A Computational and Experimental Framework"

Based on:
- Research plan: {plan[:200]}
- Hypotheses: {hypotheses[:200]}
- Methods: {code[:200]}
- Review: {review[:200]}

Write a 200-word abstract following Nature journal format:
- Background (2 sentences)
- Methods (2 sentences)
- Results (2 sentences)
- Conclusions (2 sentences)

Use formal scientific language."""

        abstract = await self.run_agent(
            "Scientific Publisher",
            "publisher",
            publisher_prompt,
            max_tokens=350
        )

        # ========================================================================
        # RESUMEN FINAL
        # ========================================================================

        console.print(f"\n\n[bold cyan]{'='*80}[/bold cyan]")
        console.print(f"[bold cyan]📊 RESUMEN DEL WORKFLOW DE INVESTIGACIÓN[/bold cyan]")
        console.print(f"[bold cyan]{'='*80}[/bold cyan]\n")

        # Tabla de métricas
        table = Table(title="Métricas por Agente", show_header=True, header_style="bold magenta")
        table.add_column("Agente", style="cyan", width=25)
        table.add_column("Modelo", style="yellow", width=40)
        table.add_column("Tokens", justify="right", style="green")
        table.add_column("Latencia", justify="right", style="blue")

        total_tokens = 0
        total_latency = 0

        for agent_name, data in self.results.items():
            table.add_row(
                agent_name,
                data['model'].split('/')[-1],
                str(data['tokens']),
                f"{data['latency']:.0f}ms"
            )
            total_tokens += data['tokens']
            total_latency += data['latency']

        table.add_row(
            "[bold]TOTAL[/bold]",
            "",
            f"[bold]{total_tokens}[/bold]",
            f"[bold]{total_latency:.0f}ms[/bold]"
        )

        console.print(table)

        # Métricas del provider
        console.print(f"\n[bold]📈 Métricas Globales del Provider:[/bold]")
        metrics_table = Table(show_header=False, box=None)
        metrics_table.add_column("Métrica", style="cyan")
        metrics_table.add_column("Valor", style="yellow")

        for key, value in self.provider.metrics.items():
            metrics_table.add_row(f"  {key}", str(value))

        console.print(metrics_table)

        # Abstract final
        console.print(f"\n[bold green]{'='*80}[/bold green]")
        console.print(f"[bold green]📄 ABSTRACT FINAL GENERADO[/bold green]")
        console.print(f"[bold green]{'='*80}[/bold green]\n")

        console.print(Panel(
            abstract if abstract else "No disponible",
            title="Abstract del Artículo",
            border_style="green",
            padding=(1, 2)
        ))

        # Guardar resultados
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"research_output_{timestamp}.txt"

        with open(filename, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("AXIOM ATLAS - Reporte de Investigación Multi-Agente\n")
            f.write("="*80 + "\n\n")
            f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Tema: {RESEARCH_TOPIC.strip()}\n\n")
            f.write("="*80 + "\n\n")

            for agent_name, data in self.results.items():
                f.write(f"\n{'='*80}\n")
                f.write(f"{agent_name.upper()}\n")
                f.write(f"Modelo: {data['model']}\n")
                f.write(f"Tokens: {data['tokens']} | Latencia: {data['latency']:.0f}ms\n")
                f.write(f"{'='*80}\n\n")
                f.write(data['response'])
                f.write("\n\n")

        console.print(f"\n[green]💾 Resultados guardados en: {filename}[/green]")

        return self.results


async def main():
    """Ejecutar workflow completo"""

    console.print("\n")
    workflow = ResearchWorkflow()

    try:
        results = await workflow.execute_research_workflow()

        console.print(f"\n\n[bold green]✅ WORKFLOW COMPLETADO EXITOSAMENTE[/bold green]")
        console.print(f"[green]Se generaron {len(results)} outputs de agentes[/green]\n")

    except Exception as e:
        console.print(f"\n[bold red]❌ Error en el workflow: {e}[/bold red]")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
