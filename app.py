#!/usr/bin/env python3
import subprocess
import time
import sys
import os
import requests
import pwd
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.prompt import IntPrompt
from rich.table import Table
from stem import Signal
from rich.align import Align
from rich.box import ROUNDED
from stem.control import Controller

# --- Global Configuration & Detection ---
console = Console()
TOOL_NAME = "Tor Switch"
SUBTITLE = "make yourself ANonymous"
DEVELOPER = "justt cyber tech"

def get_tor_uid():
    """Gets the UID of the debian-tor user for iptables rules."""
    try:
        return pwd.getpwnam('debian-tor').pw_uid
    except KeyError:
        console.print("[bold red]Error: 'debian-tor' user not found. This is required for the kill switch.[/bold red]")
        console.print("[yellow]Please ensure Tor is installed correctly (e.g., 'sudo apt install tor'). Exiting.[/yellow]")
        sys.exit(1)

TOR_UID = get_tor_uid()

# --- Helpers ---
def run_silent(cmd):
    """Run a shell command silently (no output)."""
    subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def _parse_ip_data(api_url, data):
    """Parses JSON data from different IP APIs into a standard format."""
    if "ipwho.is" in api_url:
        if not data.get('success', False): return None
        return {
            "query": data.get("ip", "N/A"), "city": data.get("city", "Unknown"),
            "country": data.get("country", "Unknown"), "isp": data.get("connection", {}).get("isp", "Unknown"),
            "timezone": data.get("timezone", {}).get("id", "Unknown")
        }
    elif "ipapi.co" in api_url:
        if data.get('error'): return None
        return {
            "query": data.get("ip", "N/A"), "city": data.get("city", "Unknown"),
            "country": data.get("country_name", "Unknown"), "isp": data.get("org", "Unknown"),
            "timezone": data.get("timezone", "Unknown")
        }
    elif "ip-api.com" in api_url:
        if data.get('status') != 'success': return None
        return {
            "query": data.get("query", "N/A"), "city": data.get("city", "Unknown"),
            "country": data.get("country", "Unknown"), "isp": data.get("isp", "Unknown"),
            "timezone": data.get("timezone", "Unknown")
        }
    return None

def get_ip_details():
    """Fetches IP details from multiple APIs for redundancy."""
    apis = [
        "http://ipwho.is/",
        "https://ipapi.co/json/",
        "http://ip-api.com/json"
    ]
    for api_url in apis:
        try:
            response = requests.get(api_url, timeout=5)
            response.raise_for_status()  # Raise an exception for bad status codes
            data = response.json()
            parsed_data = _parse_ip_data(api_url, data)
            if parsed_data:
                return parsed_data
        except (requests.exceptions.RequestException, ValueError):
            # This will catch connection errors, timeouts, and JSON decoding errors
            console.log(f"[yellow]API {api_url} failed. Trying next...[/yellow]")
            continue
    # Return this only if all APIs fail
    return {"query": "Offline", "city": "Unknown", "country": "Unknown", "isp": "Unknown", "timezone": "Unknown"}

def change_tor_ip():
    """Signals Tor to get a new IP address via the control port."""
    try:
        with Controller.from_port(port=9051) as controller:
            controller.authenticate()  # Authenticate using cookie or no password
            controller.signal(Signal.NEWNYM)
            return True
    except Exception as e:
        console.log(f"[bold red]Error signaling Tor for new IP: {e}[/bold red]")
        console.log("[bold yellow]Ensure Tor is running and the control port is configured for cookie or passwordless authentication.[/bold yellow]")
        return False

def get_timing_choice():
    """Ask user for timing interval and grade choice."""
    console.clear()
    header_text = f"[bold green]{TOOL_NAME}[/bold green] | [dim]Developed by {DEVELOPER}[/dim]"
    console.print(Panel(Align.center(header_text), style="on black", border_style="cyan", box=ROUNDED))

    console.print("\n[bold underline]Select Rotation Interval:[/bold underline]")
    console.print("[red]1.  10 - 30s[/red]  : [bold red]POOR[/bold red]")
    console.print("[yellow]2.  30 - 60s[/yellow]  : [bold yellow]GOOD[/bold yellow]")
    console.print("[green]3.  60s +   [/green]  : [bold green]PERFECT[/bold green]")
    console.print("[blue]4.  Custom  [/blue]  : Enter your own seconds\n")

    choice = IntPrompt.ask("Choose an option", choices=["1","2","3","4"], default="3")
    if choice == 1:
        seconds = IntPrompt.ask("Enter seconds (Recommended: 20)", default=20)
        quality = "[bold red]POOR[/bold red]"
    elif choice == 2:
        seconds = IntPrompt.ask("Enter seconds (Recommended: 45)", default=45)
        quality = "[bold yellow]GOOD[/bold yellow]"
    elif choice == 3:
        seconds = IntPrompt.ask("Enter seconds (Recommended: 120)", default=120)
        quality = "[bold green]PERFECT[/bold green]"
    else:
        seconds = IntPrompt.ask("Enter custom seconds")
        if seconds < 30:
            quality = "[bold red]POOR[/bold red]"
        elif seconds < 60:
            quality = "[bold yellow]GOOD[/bold yellow]"
        else:
            quality = "[bold green]PERFECT[/bold green]"
    return seconds, quality

def generate_dashboard(status_msg, ip_data, timer, total_cycles, quality_label, ipv6_status, killswitch_status):
    """Creates the visual dashboard layout."""
    from rich.align import Align

    grid = Table.grid(expand=True)
    grid.add_column(justify="center", ratio=1)
    grid.add_column(justify="center", ratio=1)

    status_color = "green" if "SECURE" in status_msg else "red"
    grid.add_row(
        Panel(Align.center(f"[bold {status_color}]{status_msg}[/bold {status_color}]"), title="Status", border_style=status_color, box=ROUNDED),
        Panel(Align.center(f"[bold white]{ip_data.get('query', 'Loading...')}[/bold white]"), title="Public IP", border_style="bright_blue", box=ROUNDED)
    )

    details = (
        f"[bold cyan]Location :[/bold cyan] {ip_data.get('city', 'Unknown')}, {ip_data.get('country', 'Unknown')}\n"
        f"[bold cyan]Provider :[/bold cyan] {ip_data.get('isp', 'Unknown')}\n"
        f"[bold cyan]Timezone :[/bold cyan] {ip_data.get('timezone', 'Unknown')}"
    )
    stats = f"Cycles: {total_cycles} | Interval: {quality_label} | Next Switch: {timer}s "

    layout = Table.grid(expand=True)
    header_text = f"[bold green]{TOOL_NAME}[/bold green] | [dim]Developed by {DEVELOPER}[/dim]"
    layout.add_row(Panel(Align.center(header_text), style="on black", border_style="cyan", box=ROUNDED))

    # --- Status Boxes ---
    status_grid = Table.grid(expand=True)
    status_grid.add_column()
    status_grid.add_column()
    status_grid.add_row(
        Panel(Align.center(ipv6_status), title="[bold]IPv6 Status[/bold]", border_style="magenta", box=ROUNDED),
        Panel(Align.center(killswitch_status), title="[bold]Traffic Policy[/bold]", border_style="yellow", box=ROUNDED)
    )
    layout.add_row(status_grid)
    layout.add_row(grid)
    layout.add_row(Panel(details, title="Geo-Location Data", border_style="white", box=ROUNDED))
    layout.add_row(Panel(Align.center(stats), style="bold white on black", box=ROUNDED))
    return layout

# --- Kill Switch / Internet Control ---
def enable_killswitch():
    console.print("[bold red]Activating Kill Switch: Only Tor traffic allowed[/bold red]")
    run_silent("iptables -F")
    run_silent("iptables -t nat -F")
    run_silent("iptables -P OUTPUT DROP")
    run_silent("iptables -P INPUT DROP")
    run_silent("iptables -P FORWARD DROP")
    run_silent("iptables -A OUTPUT -o lo -j ACCEPT")
    run_silent("iptables -A INPUT -i lo -j ACCEPT")
    run_silent(f"iptables -A OUTPUT -m owner --uid-owner {TOR_UID} -j ACCEPT")
    run_silent("iptables -A OUTPUT -p udp --dport 5353 -j ACCEPT")

def disable_killswitch():
    console.print("[bold green]Restoring normal internet access[/bold green]")
    run_silent("iptables -F")
    run_silent("iptables -t nat -F")
    run_silent("iptables -P OUTPUT ACCEPT")
    run_silent("iptables -P INPUT ACCEPT")
    run_silent("iptables -P FORWARD ACCEPT")

# --- Persistent IPv6 Control ---
IPV6_CONF_FILE = "/etc/sysctl.d/99-switch-to-tor-ipv6.conf"

def _update_ipv6_setting(enabled: bool):
    """Writes the IPv6 setting to a sysctl conf file and applies it."""
    value = 0 if enabled else 1
    content = (
        f"net.ipv6.conf.all.disable_ipv6={value}\n"
        f"net.ipv6.conf.default.disable_ipv6={value}\n"
    )
    try:
        with open(IPV6_CONF_FILE, "w") as f:
            f.write(content)
        # Apply the new settings immediately from all conf files
        run_silent("sysctl -p")
        return True
    except Exception as e:
        console.print(f"[bold red]Error updating IPv6 config: {e}[/bold red]")
        console.print("[yellow]Make sure you are running the script with sudo.[/yellow]")
        return False

def enable_ipv6():
    console.print("[bold green]Enabling IPv6 permanently...[/bold green]")
    if _update_ipv6_setting(enabled=True):
        console.print("[bold green]IPv6 has been permanently enabled.[/bold green]")
    input("\nPress Enter to return to the menu...")

def disable_ipv6():
    console.print("[bold red]Disabling IPv6 permanently...[/bold red]")
    if _update_ipv6_setting(enabled=False):
        console.print("[bold red]IPv6 has been permanently disabled.[/bold red]")
    input("\nPress Enter to return to the menu...")

def ipv6_menu():
    """Displays a sub-menu for managing IPv6 settings."""
    console.clear()
    header_text = f"[bold green]{TOOL_NAME}[/bold green] | [dim]Developed by {DEVELOPER}[/dim]"
    console.print(Panel(Align.center(header_text), style="on black", border_style="cyan", box=ROUNDED))
    console.print("\n[bold underline]IPv6 Settings:[/bold underline]")
    console.print("1. Enable IPv6 (On)")
    console.print("2. Disable IPv6 (Off)")
    console.print("3. Back to Main Menu\n")
    choice = IntPrompt.ask("Choose an option", choices=["1","2","3"], default="3")
    if choice == 1:
        enable_ipv6()
    elif choice == 2:
        disable_ipv6()
    # If choice is 3, we do nothing and simply return to the main menu.

# --- Rotation Dashboard ---
def rotation_dashboard():
    interval, quality = get_timing_choice()
    cycle_count = 0
    current_data = {"query": "Initializing..."}
    console.print("\n[bold green][*] Starting Rotation Dashboard...[/bold green]")
    time.sleep(1)

    # Start anonsurf once at the beginning of the session
    console.print(f"[bold green]{TOOL_NAME} is starting...[/bold green]")
    run_silent("yes | sudo anonsurf start")
    time.sleep(4) # Give anonsurf time to establish connection

    ipv6_status, killswitch_status = get_system_status()
    with Live(generate_dashboard("Initializing", {}, interval, 0, quality, ipv6_status, killswitch_status), refresh_per_second=4, screen=True) as live:
        try:
            while True:
                ipv6_status, killswitch_status = get_system_status()
                live.update(generate_dashboard("REQUESTING NEW IP...", current_data, 0, cycle_count, quality, ipv6_status, killswitch_status))
                if not change_tor_ip():
                    # If signaling fails, break the loop so the user can fix the config
                    time.sleep(5) # Give user time to read error
                    break
                time.sleep(2) # Wait a moment for the new circuit to be established

                current_data = get_ip_details()
                cycle_count += 1

                # --- Smoother Countdown Timer ---
                # Record the start time for the current interval
                start_time = time.time()
                while True:
                    elapsed = time.time() - start_time
                    remaining = interval - int(elapsed)
                    if remaining < 0:
                        break
                    status = "SECURE & ANONYMOUS"
                    ipv6_status, killswitch_status = get_system_status() # Refresh status for the countdown
                    live.update(generate_dashboard(status, current_data, remaining, cycle_count, quality, ipv6_status, killswitch_status))
                    time.sleep(0.25) # Update 4 times per second for a smoother feel

        except KeyboardInterrupt:
            console.print(f"\n[bold yellow]Shutdown signal received. Stopping {TOOL_NAME}...[/bold yellow]")

    # This code runs after the 'with' block finishes (normally or by interrupt)
    run_silent("yes | sudo anonsurf stop")
    console.print(f"[bold red]Session Terminated.[/bold red] {TOOL_NAME} stopped.")

# --- Status Checkers ---
def get_system_status():
    """Checks and returns the status of IPv6 and the iptables kill switch."""
    # Check IPv6 Status
    ipv6_status = "[bold yellow]Unknown[/bold yellow]"
    try:
        # Check the live kernel parameter
        result = subprocess.run(["sysctl", "net.ipv6.conf.all.disable_ipv6"], capture_output=True, text=True, check=True)
        output = result.stdout.strip()
        if output.endswith("= 1"):
            ipv6_status = "[bold red]Disabled[/bold red]"
        elif output.endswith("= 0"):
            ipv6_status = "[bold green]Enabled[/bold green]"
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Fallback for when sysctl fails
        ipv6_status = "[bold yellow]Unknown[/bold yellow]"

    # Check Kill Switch (iptables) Status
    killswitch_status = "[bold yellow]Unknown[/bold yellow]"
    try:
        # Check the default policy of the OUTPUT chain
        result = subprocess.run(["iptables", "-L", "OUTPUT"], capture_output=True, text=True, check=True)
        first_line = result.stdout.strip().split('\n')[0]
        if "policy DROP" in first_line:
            killswitch_status = "[bold red]Active (Tor-Only)[/bold red]"
        elif "policy ACCEPT" in first_line:
            killswitch_status = "[bold green]Inactive (All Traffic)[/bold green]"
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Fallback for when iptables fails
        killswitch_status = "[bold yellow]Unknown[/bold yellow]"

    return ipv6_status, killswitch_status

# --- Menu ---
def main_menu():
    while True:
        console.clear()

        # --- Create the main layout grid ---
        layout = Table.grid(expand=True, padding=(0, 1))
        layout.add_column()

        # --- Header ---
        header_text = f"[bold green]{TOOL_NAME}[/bold green] | [dim]Developed by {DEVELOPER}[/dim]"
        layout.add_row(Panel(Align.center(header_text), style="on black", border_style="cyan", box=ROUNDED))

        # --- Status Boxes ---
        ipv6_status, killswitch_status = get_system_status()
        status_grid = Table.grid(expand=True)
        status_grid.add_column()
        status_grid.add_column()
        status_grid.add_row(
            Panel(Align.center(ipv6_status), title="[bold]IPv6 Status[/bold]", border_style="magenta", box=ROUNDED),
            Panel(Align.center(killswitch_status), title="[bold]Traffic Policy[/bold]", border_style="yellow", box=ROUNDED)
        )
        layout.add_row(status_grid)

        # --- Menu Options ---
        menu_text = "[bold underline]Select Mode:[/bold underline]\n1. Kill Switch (Tor-only internet)\n2. Normal Internet (all traffic allowed)\n3. Rotation Timing Dashboard\n4. Exit"
        layout.add_row(Panel(menu_text, border_style="dim", box=ROUNDED, padding=(1, 2)))
        console.print(layout)

        choice = IntPrompt.ask("Choose an option", choices=["1","2","3","4"], default="3")
        if choice == 1:
            enable_killswitch()
        elif choice == 2:
            disable_killswitch()
        elif choice == 3:
            rotation_dashboard()
        elif choice == 4:
            console.print("[bold red]Exiting program...[/bold red]")
            break

if __name__ == "__main__":
    if os.geteuid() != 0:
        console.clear()
        console.print("[bold red]Error: This script must be run as root.[/bold red]")
    else:
        try:
            main_menu()
        except KeyboardInterrupt:
            console.print("\n[bold red]Program interrupted by user. Exiting safely...[/bold red]")
