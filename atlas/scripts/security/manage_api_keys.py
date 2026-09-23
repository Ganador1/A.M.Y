#!/usr/bin/env python3
"""
AXIOM API Keys Manager CLI
Herramienta de línea de comandos para gestionar API keys de forma segura

Uso:
    python scripts/security/manage_api_keys.py [command] [options]

Comandos:
    set <provider> <api_key>  - Configurar API key para un proveedor
    get <provider>            - Obtener API key (enmascarada)
    list                      - Listar todos los proveedores
    remove <provider>         - Eliminar API key
    import                    - Importar desde variables de entorno
    export                    - Exportar a .env.example
    stats                     - Mostrar estadísticas
    rotate                    - Rotar clave de cifrado
"""

import sys
import os
from pathlib import Path

# Agregar path del proyecto
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.config.api_keys_manager import APIKeysManager, get_api_keys_manager
import argparse
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

console = Console()


def cmd_set(args):
    """Configurar API key para un proveedor"""
    manager = get_api_keys_manager()

    provider = args.provider.upper()
    api_key = args.api_key

    console.print(f"\n🔐 Configurando API key para [bold]{provider}[/bold]...")

    try:
        manager.set_api_key(provider, api_key, save=True)
        console.print(f"[green]✅ API key guardada de forma segura para {provider}[/green]\n")

        # Mostrar información
        masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else api_key[:4] + "..."
        console.print(f"   API Key (masked): {masked_key}")
        console.print(f"   Archivo cifrado: {manager.storage_file}")
        console.print()

    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]\n")
        sys.exit(1)


def cmd_get(args):
    """Obtener API key (enmascarada)"""
    manager = get_api_keys_manager()
    provider = args.provider.upper()

    console.print(f"\n🔍 Buscando API key para [bold]{provider}[/bold]...\n")

    api_key = manager.get_api_key(provider)

    if api_key:
        masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else api_key[:4] + "..."

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Proveedor")
        table.add_column("API Key (masked)")
        table.add_column("Fuente")

        source = "encrypted" if provider in manager._api_keys else "env"
        table.add_row(provider, masked_key, source)

        console.print(table)
        console.print()
    else:
        console.print(f"[yellow]⚠️ No se encontró API key para {provider}[/yellow]\n")


def cmd_list(args):
    """Listar todos los proveedores"""
    manager = get_api_keys_manager()

    console.print("\n📋 [bold]Proveedores Configurados[/bold]\n")

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Proveedor", style="cyan")
    table.add_column("Estado", justify="center")
    table.add_column("API Key (masked)", style="dim")
    table.add_column("Fuente")

    providers_info = manager.list_providers()

    for info in providers_info:
        status_icon = "✅" if info["configured"] else "❌"
        masked_key = info["masked_key"] or "-"
        source = info["source"] or "-"

        table.add_row(
            info["provider"],
            status_icon,
            masked_key,
            source
        )

    console.print(table)

    # Resumen
    configured = sum(1 for p in providers_info if p["configured"])
    total = len(providers_info)

    console.print(f"\n📊 Resumen: {configured}/{total} proveedores configurados\n")


def cmd_remove(args):
    """Eliminar API key"""
    manager = get_api_keys_manager()
    provider = args.provider.upper()

    console.print(f"\n🗑️  Eliminando API key para [bold]{provider}[/bold]...\n")

    # Confirmar
    if not args.yes:
        confirm = input(f"¿Estás seguro de eliminar la API key para {provider}? (yes/no): ")
        if confirm.lower() != 'yes':
            console.print("[yellow]❌ Operación cancelada[/yellow]\n")
            return

    if manager.remove_api_key(provider, save=True):
        console.print(f"[green]✅ API key eliminada para {provider}[/green]\n")
    else:
        console.print(f"[yellow]⚠️ No se encontró API key para {provider}[/yellow]\n")


def cmd_import(args):
    """Importar desde variables de entorno"""
    manager = get_api_keys_manager()

    console.print("\n📥 [bold]Importando API keys desde variables de entorno[/bold]...\n")

    imported = manager.import_from_env(save=True)

    if imported > 0:
        console.print(f"[green]✅ Importadas {imported} API keys exitosamente[/green]\n")

        # Mostrar cuáles se importaron
        cmd_list(args)
    else:
        console.print("[yellow]⚠️ No se encontraron nuevas API keys para importar[/yellow]\n")


def cmd_export(args):
    """Exportar a .env.example"""
    manager = get_api_keys_manager()

    output_file = args.output or ".env.example"

    console.print(f"\n📤 [bold]Exportando configuración a {output_file}[/bold]...\n")

    try:
        content = manager.export_to_env_example(output_file)
        console.print(f"[green]✅ Archivo generado exitosamente[/green]\n")
        console.print(Panel(content[:500] + "\n..." if len(content) > 500 else content,
                           title=output_file, border_style="green"))
        console.print()
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]\n")
        sys.exit(1)


def cmd_stats(args):
    """Mostrar estadísticas"""
    manager = get_api_keys_manager()

    console.print("\n📊 [bold]Estadísticas del Gestor de API Keys[/bold]\n")

    stats = manager.get_stats()

    table = Table(show_header=False, box=None)
    table.add_column("Métrica", style="cyan")
    table.add_column("Valor", style="green")

    table.add_row("Total de proveedores", str(stats["total_providers"]))
    table.add_row("Proveedores configurados", f"{stats['configured_providers']} ✅")
    table.add_row("Proveedores sin configurar", f"{stats['unconfigured_providers']} ❌")
    table.add_row("Archivo de almacenamiento", stats["storage_file"])
    table.add_row("Archivo existe", "✅" if stats["storage_exists"] else "❌")
    table.add_row("Fallback a ENV habilitado", "✅" if stats["env_fallback_enabled"] else "❌")

    console.print(table)
    console.print()

    # Mostrar lista de proveedores
    cmd_list(args)


def cmd_rotate(args):
    """Rotar clave de cifrado"""
    manager = get_api_keys_manager()

    console.print("\n🔄 [bold red]ADVERTENCIA: Rotación de Clave de Cifrado[/bold red]\n")
    console.print("Esta operación descifrará y volverá a cifrar todas las API keys.")
    console.print("Se generará una nueva clave de cifrado.\n")

    # Confirmar
    if not args.yes:
        confirm = input("¿Estás seguro de continuar? (yes/no): ")
        if confirm.lower() != 'yes':
            console.print("[yellow]❌ Operación cancelada[/yellow]\n")
            return

    try:
        new_password = input("Nueva contraseña (vacío para clave aleatoria): ").strip() or None
        manager.rotate_encryption_key(new_password)
        console.print("[green]✅ Clave de cifrado rotada exitosamente[/green]\n")
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]\n")
        sys.exit(1)


def cmd_test(args):
    """Test de conexión con proveedores configurados"""
    manager = get_api_keys_manager()

    console.print("\n🔍 [bold]Probando Conexiones[/bold]\n")

    # Probar Hugging Face
    if manager.has_api_key("HUGGINGFACE"):
        console.print("Testing Hugging Face...")
        try:
            from app.services.llm_providers.huggingface_provider import HuggingFaceProvider
            provider = HuggingFaceProvider()
            if provider.api_key:
                console.print("[green]✅ Hugging Face: API key configurada[/green]")
            else:
                console.print("[yellow]⚠️ Hugging Face: Sin API key[/yellow]")
        except Exception as e:
            console.print(f"[red]❌ Hugging Face: Error - {e}[/red]")

    console.print()


def main():
    parser = argparse.ArgumentParser(
        description="AXIOM API Keys Manager - Gestión segura de API keys con cifrado",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  # Configurar API key de Hugging Face
  python manage_api_keys.py set HUGGINGFACE hf_xxxxxxxxxxxxx

  # Listar proveedores
  python manage_api_keys.py list

  # Importar desde variables de entorno
  python manage_api_keys.py import

  # Exportar a .env.example
  python manage_api_keys.py export

  # Ver estadísticas
  python manage_api_keys.py stats
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Comandos disponibles')

    # Comando: set
    parser_set = subparsers.add_parser('set', help='Configurar API key')
    parser_set.add_argument('provider', help='Nombre del proveedor (ej: HUGGINGFACE)')
    parser_set.add_argument('api_key', help='API key a guardar')
    parser_set.set_defaults(func=cmd_set)

    # Comando: get
    parser_get = subparsers.add_parser('get', help='Obtener API key (masked)')
    parser_get.add_argument('provider', help='Nombre del proveedor')
    parser_get.set_defaults(func=cmd_get)

    # Comando: list
    parser_list = subparsers.add_parser('list', help='Listar proveedores')
    parser_list.set_defaults(func=cmd_list)

    # Comando: remove
    parser_remove = subparsers.add_parser('remove', help='Eliminar API key')
    parser_remove.add_argument('provider', help='Nombre del proveedor')
    parser_remove.add_argument('-y', '--yes', action='store_true', help='No pedir confirmación')
    parser_remove.set_defaults(func=cmd_remove)

    # Comando: import
    parser_import = subparsers.add_parser('import', help='Importar desde ENV')
    parser_import.set_defaults(func=cmd_import)

    # Comando: export
    parser_export = subparsers.add_parser('export', help='Exportar a .env.example')
    parser_export.add_argument('-o', '--output', help='Archivo de salida', default='.env.example')
    parser_export.set_defaults(func=cmd_export)

    # Comando: stats
    parser_stats = subparsers.add_parser('stats', help='Mostrar estadísticas')
    parser_stats.set_defaults(func=cmd_stats)

    # Comando: rotate
    parser_rotate = subparsers.add_parser('rotate', help='Rotar clave de cifrado')
    parser_rotate.add_argument('-y', '--yes', action='store_true', help='No pedir confirmación')
    parser_rotate.set_defaults(func=cmd_rotate)

    # Comando: test
    parser_test = subparsers.add_parser('test', help='Test de conexión')
    parser_test.set_defaults(func=cmd_test)

    args = parser.parse_args()

    # Banner
    console.print("\n" + "="*70)
    console.print("[bold cyan]🔐 AXIOM API Keys Manager[/bold cyan]")
    console.print("Gestión Segura de API Keys con Cifrado Fernet (AES-128)")
    console.print("="*70)

    if not args.command:
        parser.print_help()
        sys.exit(0)

    # Ejecutar comando
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
