#!/usr/bin/env python3
"""
License Administration CLI
Manage license keys for Binance Algo Bot

Usage:
    python admin_license.py generate --tier pro --email user@example.com --days 30
    python admin_license.py validate LICENSE-KEY
    python admin_license.py list
    python admin_license.py info LICENSE-KEY
    python admin_license.py deactivate LICENSE-KEY
    python admin_license.py extend LICENSE-KEY --days 30
    python admin_license.py upgrade LICENSE-KEY --tier premium
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime
from modules.license_manager import LicenseManager
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()


def generate_license(args):
    """Generate a new license"""
    manager = LicenseManager()

    # Validate tier
    valid_tiers = ['free', 'pro', 'premium', 'enterprise']
    if args.tier.lower() not in valid_tiers:
        console.print(f"[red]❌ Invalid tier. Must be one of: {', '.join(valid_tiers)}[/red]")
        return

    # Generate license
    console.print(f"\n[cyan]🔑 Generating {args.tier.upper()} license...[/cyan]\n")

    try:
        license = manager.create_license(
            tier=args.tier.lower(),
            email=args.email,
            duration_days=args.days,
            max_activations=args.max_activations,
            metadata={
                'source': 'admin_cli',
                'notes': args.notes or ''
            }
        )

        # Display license info
        panel = Panel(
            f"""[bold green]{license.license_key}[/bold green]

[cyan]Tier:[/cyan] {license.tier.upper()}
[cyan]Email:[/cyan] {license.email}
[cyan]Issued:[/cyan] {license.issued_date.strftime('%Y-%m-%d %H:%M:%S')}
[cyan]Expires:[/cyan] {license.expiry_date.strftime('%Y-%m-%d %H:%M:%S')}
[cyan]Duration:[/cyan] {args.days} days
[cyan]Max Activations:[/cyan] {license.max_activations}
[cyan]User ID:[/cyan] {license.user_id}
""",
            title="✅ License Generated Successfully",
            border_style="green",
            box=box.ROUNDED
        )

        console.print(panel)

        # Save to file
        if args.save:
            filename = f"license_{license.tier}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, 'w') as f:
                f.write(f"BINANCE ALGO BOT LICENSE\n")
                f.write(f"=" * 50 + "\n\n")
                f.write(f"License Key: {license.license_key}\n")
                f.write(f"Tier: {license.tier.upper()}\n")
                f.write(f"Email: {license.email}\n")
                f.write(f"Issued: {license.issued_date.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Expires: {license.expiry_date.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Duration: {args.days} days\n")
                f.write(f"Max Activations: {license.max_activations}\n")
                f.write(f"User ID: {license.user_id}\n")

            console.print(f"\n[green]💾 License saved to: {filename}[/green]")

    except Exception as e:
        console.print(f"[red]❌ Error generating license: {e}[/red]")


def validate_license(args):
    """Validate a license key"""
    manager = LicenseManager()

    console.print(f"\n[cyan]🔍 Validating license...[/cyan]\n")

    is_valid, message, tier = manager.validate_license(args.license_key)

    if is_valid:
        console.print(Panel(
            f"""[bold green]✅ License is VALID[/bold green]

[cyan]Tier:[/cyan] {tier.upper() if tier else 'N/A'}
[cyan]Message:[/cyan] {message}
""",
            border_style="green",
            box=box.ROUNDED
        ))
    else:
        console.print(Panel(
            f"""[bold red]❌ License is INVALID[/bold red]

[yellow]Reason:[/yellow] {message}
""",
            border_style="red",
            box=box.ROUNDED
        ))


def show_license_info(args):
    """Show detailed license information"""
    manager = LicenseManager()

    info = manager.get_license_info(args.license_key)

    if not info:
        console.print(f"[red]❌ License not found[/red]")
        return

    # Status badge
    if info['is_expired']:
        status = "[red]EXPIRED[/red]"
    elif info['is_active']:
        status = "[green]ACTIVE[/green]"
    else:
        status = "[yellow]INACTIVE[/yellow]"

    panel = Panel(
        f"""[cyan]License Key:[/cyan] {info['license_key']}
[cyan]Status:[/cyan] {status}

[bold]ACCOUNT INFO[/bold]
[cyan]Tier:[/cyan] {info['tier']}
[cyan]Email:[/cyan] {info['email']}

[bold]DATES[/bold]
[cyan]Issued:[/cyan] {info['issued_date']}
[cyan]Expires:[/cyan] {info['expiry_date']}
[cyan]Days Remaining:[/cyan] {info['days_remaining']}

[bold]ACTIVATIONS[/bold]
[cyan]Active:[/cyan] {info['activation_count']} / {info['max_activations']}
[cyan]Hardware ID:[/cyan] {info['hardware_id'] or 'Not activated'}
""",
        title="📋 License Information",
        border_style="cyan",
        box=box.ROUNDED
    )

    console.print(panel)


def list_licenses(args):
    """List all licenses"""
    import sqlite3

    db_path = "data/licenses.db"
    if not Path(db_path).exists():
        console.print("[yellow]No licenses found[/yellow]")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT license_key, tier, email, expiry_date, is_active, activation_count
        FROM licenses
        ORDER BY expiry_date DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        console.print("[yellow]No licenses found[/yellow]")
        return

    table = Table(title="📊 All Licenses", box=box.ROUNDED)

    table.add_column("License Key", style="cyan", no_wrap=True)
    table.add_column("Tier", style="magenta")
    table.add_column("Email", style="green")
    table.add_column("Expires", style="yellow")
    table.add_column("Status", style="white")
    table.add_column("Activations", justify="right", style="blue")

    for row in rows:
        license_key, tier, email, expiry_date, is_active, activation_count = row

        # Truncate license key for display
        display_key = license_key[:20] + "..." if len(license_key) > 20 else license_key

        # Calculate status
        expiry = datetime.fromisoformat(expiry_date)
        is_expired = datetime.utcnow() > expiry

        if is_expired:
            status = "🔴 Expired"
        elif is_active:
            status = "🟢 Active"
        else:
            status = "🟡 Inactive"

        table.add_row(
            display_key,
            tier.upper(),
            email,
            expiry_date[:10],
            status,
            str(activation_count)
        )

    console.print(table)
    console.print(f"\n[cyan]Total: {len(rows)} licenses[/cyan]")


def deactivate_license(args):
    """Deactivate a license"""
    manager = LicenseManager()

    console.print(f"\n[yellow]⚠️  Deactivating license...[/yellow]\n")

    success, message = manager.deactivate_license(args.license_key)

    if success:
        console.print(f"[green]✅ {message}[/green]")
    else:
        console.print(f"[red]❌ {message}[/red]")


def extend_license(args):
    """Extend license expiry"""
    manager = LicenseManager()

    console.print(f"\n[cyan]📅 Extending license by {args.days} days...[/cyan]\n")

    success, message = manager.extend_license(args.license_key, args.days)

    if success:
        console.print(f"[green]✅ {message}[/green]")

        # Show updated info
        info = manager.get_license_info(args.license_key)
        if info:
            console.print(f"\n[cyan]New expiry date:[/cyan] {info['expiry_date']}")
            console.print(f"[cyan]Days remaining:[/cyan] {info['days_remaining']}")
    else:
        console.print(f"[red]❌ {message}[/red]")


def upgrade_license(args):
    """Upgrade license tier"""
    manager = LicenseManager()

    console.print(f"\n[cyan]⬆️  Upgrading license to {args.tier.upper()}...[/cyan]\n")

    success, message = manager.upgrade_license(args.license_key, args.tier)

    if success:
        console.print(f"[green]✅ {message}[/green]")
    else:
        console.print(f"[red]❌ {message}[/red]")


def main():
    parser = argparse.ArgumentParser(
        description="Binance Algo Bot - License Administration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate a PRO license for 30 days
  python admin_license.py generate --tier pro --email user@example.com --days 30

  # Generate PREMIUM license with 2 device activations
  python admin_license.py generate --tier premium --email vip@example.com --days 90 --max-activations 2

  # Validate a license key
  python admin_license.py validate PRO-1A2B-3C4D-5E6F-7890-ABCD

  # List all licenses
  python admin_license.py list

  # Show license details
  python admin_license.py info PRO-1A2B-3C4D-5E6F-7890-ABCD

  # Extend license by 30 days
  python admin_license.py extend PRO-1A2B-3C4D-5E6F-7890-ABCD --days 30

  # Upgrade to PREMIUM
  python admin_license.py upgrade PRO-1A2B-3C4D-5E6F-7890-ABCD --tier premium
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Generate command
    generate_parser = subparsers.add_parser('generate', help='Generate a new license')
    generate_parser.add_argument('--tier', required=True, help='License tier (free/pro/premium/enterprise)')
    generate_parser.add_argument('--email', required=True, help='User email')
    generate_parser.add_argument('--days', type=int, default=30, help='License duration in days (default: 30)')
    generate_parser.add_argument('--max-activations', type=int, default=1, help='Max device activations (default: 1)')
    generate_parser.add_argument('--notes', help='Additional notes')
    generate_parser.add_argument('--save', action='store_true', help='Save license to file')

    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate a license key')
    validate_parser.add_argument('license_key', help='License key to validate')

    # Info command
    info_parser = subparsers.add_parser('info', help='Show license information')
    info_parser.add_argument('license_key', help='License key')

    # List command
    list_parser = subparsers.add_parser('list', help='List all licenses')

    # Deactivate command
    deactivate_parser = subparsers.add_parser('deactivate', help='Deactivate a license')
    deactivate_parser.add_argument('license_key', help='License key')

    # Extend command
    extend_parser = subparsers.add_parser('extend', help='Extend license expiry')
    extend_parser.add_argument('license_key', help='License key')
    extend_parser.add_argument('--days', type=int, required=True, help='Days to extend')

    # Upgrade command
    upgrade_parser = subparsers.add_parser('upgrade', help='Upgrade license tier')
    upgrade_parser.add_argument('license_key', help='License key')
    upgrade_parser.add_argument('--tier', required=True, help='New tier (pro/premium/enterprise)')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Route to appropriate handler
    if args.command == 'generate':
        generate_license(args)
    elif args.command == 'validate':
        validate_license(args)
    elif args.command == 'info':
        show_license_info(args)
    elif args.command == 'list':
        list_licenses(args)
    elif args.command == 'deactivate':
        deactivate_license(args)
    elif args.command == 'extend':
        extend_license(args)
    elif args.command == 'upgrade':
        upgrade_license(args)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Cancelled by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        sys.exit(1)
