#!/usr/bin/env python3
"""UFC Fight Notifier — SMS alerts before your selected fights start."""

import requests
import creds
import time
import os
import sys
import json
from dataclasses import dataclass, field
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from twilio.rest import Client

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.rule import Rule
from rich.columns import Columns
from rich.align import Align
from rich import box
from rich.prompt import Prompt
import questionary

# ── Twilio ─────────────────────────────────────────────────────────────────────
account_sid = creds.account_sid
auth_token  = creds.auth_token
receiver_phone = creds.phone_receiver
client = Client(account_sid, auth_token)
MESSAGING_SERVICE_SID = creds.messaging_service_sid

# ── Config ─────────────────────────────────────────────────────────────────────
DATA_FILE            = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fight-data.json")
POLL_INTERVAL        = 60   # seconds between API polls
NOTIF_GAP_SECONDS    = 120  # 2 min between each of the 3 alerts per fight
NOTIFS_PER_FIGHT     = 3
MAX_CONSECUTIVE_ERRORS = 5

HTTP_HEADERS = {
    "accept": "*/*",
    "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
    "origin": "https://www.ufc.com",
    "referer": "https://www.ufc.com/",
    "user-agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
    ),
}

SELECTOR_STYLE = questionary.Style([
    ("qmark",       "fg:#e5534b bold"),
    ("question",    "bold"),
    ("pointer",     "fg:#e5534b bold"),
    ("highlighted", "fg:#e5534b bold"),
    ("selected",    "fg:#e5534b"),
    ("answer",      "fg:#e5534b bold"),
    ("checkbox",    "fg:#e5534b"),
])

console = Console()


# ── Per-fight state ─────────────────────────────────────────────────────────────

@dataclass
class FightState:
    order:            int
    red:              str
    blue:             str
    notif_count:      int            = 0
    sequence_started: bool           = False
    last_notif_time:  datetime|None  = None
    log:              list           = field(default_factory=list)  # [{time, label}]

    def is_done(self) -> bool:
        return self.notif_count >= NOTIFS_PER_FIGHT

    def ready_for_next(self) -> bool:
        """True if enough time has passed since the last notification."""
        if self.last_notif_time is None:
            return True
        return datetime.now() >= self.last_notif_time + timedelta(seconds=NOTIF_GAP_SECONDS)

    def next_notif_in(self) -> str:
        """Human-readable countdown to the next notification."""
        if self.last_notif_time is None:
            return "now"
        remaining = (self.last_notif_time + timedelta(seconds=NOTIF_GAP_SECONDS)) - datetime.now()
        secs = max(0, int(remaining.total_seconds()))
        m, s = divmod(secs, 60)
        return f"{m}m {s:02d}s" if m else f"{s}s"


# ── Helpers ─────────────────────────────────────────────────────────────────────

def clear() -> None:
    os.system("clear" if os.name == "posix" else "cls")


def fighter_name(fighter: dict) -> str:
    n = fighter.get("Name", {})
    return f"{n.get('FirstName', '')} {n.get('LastName', '')}".strip()


def countdown_sleep(seconds: int) -> None:
    for remaining in range(seconds, 0, -1):
        m, s = divmod(remaining, 60)
        label = f"{m}m {s:02d}s" if m else f"{s}s"
        sys.stdout.write(f"\r  Next refresh in {label}...   ")
        sys.stdout.flush()
        time.sleep(1)
    sys.stdout.write("\r" + " " * 40 + "\r")
    sys.stdout.flush()


# ── Banner ──────────────────────────────────────────────────────────────────────

BANNER_LINES = [
    "     ████████   ████████   ████████████████   ██████████████",
    "    ████████    ███████   █████████████████  ███████████████",
    "    ████████   ████████   ████████████████  ████████████████",
    "   ████████   ████████                      ███████         ",
    "   ████████   ████████   ████████████████  ████████         ",
    "  ████████   ████████   ████████████████   ███████          ",
    "  ████████   ████████   ████████████████  ████████          ",
    " ████████   ████████   ████████           ███████           ",
    "████████████████████  ████████           █████████████████  ",
    "███████████████████   ████████           █████████████████  ",
    " █████████████████   ████████             ███████████████   ",
]


def print_banner() -> None:
    art = Text(justify="left")
    for line in BANNER_LINES:
        art.append(line + "\n", style="bold red")
    console.print(Align.center(Panel(art, border_style="red", padding=(0, 1), width=68)))


# ── UI components ────────────────────────────────────────────────────────────────

def build_fight_table(fight_card: list, tracked_orders: set[int]) -> Table:
    table = Table(
        box=box.ROUNDED,
        border_style="red",
        header_style="bold red",
        show_lines=True,
        padding=(0, 1),
    )
    table.add_column("#",           width=5,  justify="center")
    table.add_column("Segment",     width=8,  style="dim")
    table.add_column("Red Corner",  min_width=18, style="red")
    table.add_column("vs",          width=2,  justify="center", style="dim")
    table.add_column("Blue Corner", min_width=18, style="blue")
    table.add_column("Status",      width=12, justify="center")
    table.add_column("Result / Live Info", min_width=24)

    for fight in sorted(fight_card, key=lambda f: f.get("FightOrder", 0), reverse=True):
        order    = fight.get("FightOrder", "?")
        status   = fight.get("Status", "?")
        segment  = fight.get("CardSegment", "")
        fighters = fight.get("Fighters", [])
        red      = fighter_name(fighters[0]) if len(fighters) > 0 else "TBD"
        blue     = fighter_name(fighters[1]) if len(fighters) > 1 else "TBD"

        if status == "Final":
            status_txt = Text("✓ Final", style="bold green")
            winner = next((f for f in fighters if f.get("Outcome", {}).get("Outcome") == "Win"), None)
            loser  = next((f for f in fighters if f.get("Outcome", {}).get("Outcome") == "Loss"), None)
            if winner and loser:
                res      = fight.get("Result", {})
                method   = res.get("Method", "?")
                sub      = res.get("EndingSubmission")
                method_s = f"{method} ({sub})" if sub else method
                rnd, t   = res.get("EndingRound", "?"), res.get("EndingTime", "?")
                info     = f"[green]{fighter_name(winner)}[/green] · {method_s} R{rnd} ({t})"
            else:
                info = "Draw / No Contest"
        elif status == "Live":
            status_txt = Text("● Live", style="bold yellow")
            stats      = fight.get("LiveStats", {})
            rnd, clock = stats.get("Round", "?"), stats.get("Clock", "?")
            info       = f"[yellow]Round {rnd} — {clock}[/yellow]"
        elif status == "Upcoming":
            status_txt = Text("◦ Upcoming", style="dim")
            info       = ""
        else:
            status_txt = Text(status, style="dim")
            info       = ""

        if order in tracked_orders:
            order_cell = f"[bold yellow]► {order}[/bold yellow]"
        else:
            order_cell = str(order)

        table.add_row(order_cell, segment, red, "vs", blue, status_txt, info)

    return table


def build_notif_panel(fight_states: dict[int, FightState]) -> Panel:
    lines = []
    total_done  = sum(s.notif_count for s in fight_states.values())
    total_max   = len(fight_states) * NOTIFS_PER_FIGHT

    for order, state in sorted(fight_states.items(), reverse=True):
        done  = state.notif_count
        label = f"[dim]#{order}[/dim]  {state.red} vs {state.blue}"

        if state.is_done():
            dots = f"[green]{'●' * NOTIFS_PER_FIGHT}[/green]"
            note = "[green] ✓ done[/green]"
        elif state.sequence_started:
            dots = (
                f"[green]{'●' * done}[/green]"
                f"[dim]{'○' * (NOTIFS_PER_FIGHT - done)}[/dim]"
            )
            if state.ready_for_next():
                note = f"  [yellow]sending {done + 1}/{NOTIFS_PER_FIGHT}[/yellow]"
            else:
                note = f"  [dim]next in {state.next_notif_in()}[/dim]"
        else:
            dots = f"[dim]{'○' * NOTIFS_PER_FIGHT}[/dim]"
            note = "  [dim]waiting...[/dim]"

        lines.append(f"{dots}{note}  {label}")

    body  = "\n".join(lines) if lines else "[dim]No fights selected[/dim]"
    title = f"Alerts  {total_done}/{total_max}"
    return Panel(body, title=title, border_style="yellow", padding=(0, 1))


def build_stats_panel(event_data: dict) -> Panel:
    detail = event_data.get("LiveEventDetail", {})
    name   = detail.get("Name", "UFC Event")
    loc    = detail.get("Location", {})
    venue  = ", ".join(filter(None, [loc.get("Venue",""), loc.get("City",""), loc.get("State","")]))
    start  = detail.get("StartTime", "")
    try:
        date_str = datetime.strptime(start, "%Y-%m-%dT%H:%MZ").strftime("%B %d, %Y")
    except Exception:
        date_str = start
    body = f"[bold]{name}[/bold]\n[dim]{venue}[/dim]\n[dim]{date_str}[/dim]"
    return Panel(body, border_style="red", padding=(0, 1))


# ── Network ──────────────────────────────────────────────────────────────────────

def find_fight_id(event_number: str) -> str | None:
    url     = f"https://www.ufc.com/event/ufc-{event_number}"
    cookies = {"STYXKEY_region": "CANADA_FRENCH.CA.fr-ca.QUEBEC"}
    hdrs    = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
        "cache-control": "max-age=0",
        "user-agent": HTTP_HEADERS["user-agent"],
    }
    try:
        r = requests.get(url, cookies=cookies, headers=hdrs, timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        tag  = soup.find("script", {"type": "application/json",
                                    "data-drupal-selector": "drupal-settings-json"})
        if tag:
            data = json.loads(tag.string)
            return data.get("eventLiveStats", {}).get("event_fmid")
    except Exception as e:
        console.print(f"[red]Error fetching fight ID: {e}[/red]")
    return None


def fetch_live_data(fight_id: str) -> dict | None:
    url = f"https://d29dxerjsp82wz.cloudfront.net/api/v3/event/live/{fight_id}.json"
    try:
        r = requests.get(url, headers=HTTP_HEADERS, timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        console.print(f"[red]Failed to fetch live data: {e}[/red]")
        return None


def read_cached() -> dict | None:
    if os.path.exists(DATA_FILE) and os.path.getsize(DATA_FILE) > 0:
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return None


def save_data(data: dict) -> None:
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        console.print(f"[red]Error saving data: {e}[/red]")


# ── Notifications ────────────────────────────────────────────────────────────────

def send_sms(body: str) -> bool:
    try:
        client.messages.create(
            messaging_service_sid=MESSAGING_SERVICE_SID,
            body=body,
            to=receiver_phone,
        )
        return True
    except Exception as e:
        console.print(f"[red]SMS error: {e}[/red]")
        return False


def check_and_notify(fight_card: list, fight_states: dict[int, FightState]) -> None:
    """
    For each tracked fight:
      - Start the 3-alert sequence when the fight before it ends (or it goes Live).
      - Once started, fire alert 1 immediately, then alert 2 and 3 each 2 min apart.
    """
    for order, state in fight_states.items():
        if state.is_done():
            continue

        fight_before  = next((f for f in fight_card if f.get("FightOrder") == order + 1), None)
        target_fight  = next((f for f in fight_card if f.get("FightOrder") == order),     None)

        # Trigger the sequence when the previous fight ends or the target goes live
        if not state.sequence_started:
            prev_done   = fight_before is None or fight_before.get("Status") == "Final"
            target_live = target_fight is not None and target_fight.get("Status") in {"Live", "Final"}
            if prev_done or target_live:
                state.sequence_started = True

        # Send the next alert if the sequence is active and the gap has elapsed
        if state.sequence_started and state.ready_for_next():
            n = state.notif_count + 1
            messages = {
                1: f"UFC ALERT 🥊\n{state.red} vs {state.blue}\nYour fight is up next!  (1/3)",
                2: f"UFC ALERT 🔔\n{state.red} vs {state.blue}\nStarting very soon!  (2/3)",
                3: f"UFC ALERT 🔴\n{state.red} vs {state.blue}\nIT'S TIME — turn it on!  (3/3)",
            }
            if send_sms(messages[n]):
                state.notif_count     = n
                state.last_notif_time = datetime.now()
                state.log.append({"time": datetime.now().strftime("%H:%M:%S"), "label": f"Alert {n}/3"})


# ── Main loop ────────────────────────────────────────────────────────────────────

def run_monitor(fight_id: str, fight_states: dict[int, FightState]) -> None:
    error_streak   = 0
    tracked_orders = set(fight_states.keys())

    while not all(s.is_done() for s in fight_states.values()):
        # ── Fetch ────────────────────────────────────────────────────────────
        with console.status("[bold yellow]Fetching live data...", spinner="dots"):
            data = fetch_live_data(fight_id)

        if data is None:
            error_streak += 1
            if error_streak >= MAX_CONSECUTIVE_ERRORS:
                console.print(f"[red]API failed {MAX_CONSECUTIVE_ERRORS}× in a row. Exiting.[/red]")
                break
            console.print(
                f"[yellow]Fetch failed ({error_streak}/{MAX_CONSECUTIVE_ERRORS}). "
                f"Retrying in 30s...[/yellow]"
            )
            time.sleep(30)
            continue

        error_streak = 0
        if data != read_cached():
            save_data(data)

        fight_card = data.get("LiveEventDetail", {}).get("FightCard", [])

        # ── Render ───────────────────────────────────────────────────────────
        clear()
        print_banner()

        console.print(Columns([
            build_stats_panel(data),
            build_notif_panel(fight_states),
        ], equal=True, expand=True))
        console.print()

        console.print(Panel(
            build_fight_table(fight_card, tracked_orders),
            title=(
                "[bold red]Fight Card[/bold red]  ·  "
                f"[dim]tracking {len(tracked_orders)} fight(s)[/dim]"
            ),
            border_style="red",
            padding=(0, 0),
        ))

        now = datetime.now().strftime("%H:%M:%S")
        console.print(f"\n[dim]  Last updated: {now}  ·  Press Ctrl+C to exit[/dim]")

        # ── Notify ───────────────────────────────────────────────────────────
        check_and_notify(fight_card, fight_states)

        if all(s.is_done() for s in fight_states.values()):
            break

        # ── Wait ─────────────────────────────────────────────────────────────
        countdown_sleep(POLL_INTERVAL)

    # ── Summary ──────────────────────────────────────────────────────────────
    console.print()
    console.print(Rule("[bold green]All done[/bold green]"))
    console.print()

    summary_lines = []
    for order, state in sorted(fight_states.items(), reverse=True):
        summary_lines.append(
            f"[bold]{state.red} vs {state.blue}[/bold]  [dim](fight #{order})[/dim]"
        )
        for entry in state.log:
            summary_lines.append(f"  [green]✓[/green]  [{entry['time']}]  {entry['label']}")

    console.print(Panel(
        "\n".join(summary_lines),
        title="[bold green]Notification summary[/bold green]",
        border_style="green",
    ))


# ── Entry point ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    try:
        clear()
        print_banner()

        console.print(Panel(
            "[bold]Welcome to UFC Fight Notifier[/bold]\n\n"
            "Select one or more fights to track.\n"
            "For each fight you'll receive [yellow]3 SMS alerts[/yellow] when it's about to start,\n"
            "[dim]2 minutes apart[/dim] — so you have time to tune in.\n\n"
            "The program stops after the last selected fight has been fully notified.\n\n"
            "[dim]Press Space to select · Enter to confirm · Ctrl+C to quit[/dim]",
            border_style="yellow",
            padding=(1, 2),
        ))
        console.print()

        # ── Event selection ───────────────────────────────────────────────────
        console.print(Rule("[dim]Setup[/dim]"))
        console.print()
        console.print(
            "[dim]Leave blank for today's Fight Night, "
            "or enter an event number (e.g. [bold]300[/bold] for UFC 300)[/dim]"
        )
        event_number = Prompt.ask("  Event number", default="").strip()

        if not event_number:
            today        = datetime.now()
            event_number = (
                f"fight-night-{today.strftime('%B').lower()}-"
                f"{today.strftime('%d')}-{today.strftime('%Y')}"
            )
            console.print(f"  [dim]Auto-selected: ufc-{event_number}[/dim]")

        console.print()

        with console.status("[bold yellow]Looking up event...", spinner="dots"):
            fight_id = find_fight_id(event_number)

        if not fight_id:
            console.print("[red]Could not find the event. Check the event number and try again.[/red]")
            sys.exit(1)

        console.print(f"  [green]✓[/green] Event found  [dim](ID: {fight_id})[/dim]\n")

        # ── Load fight card ───────────────────────────────────────────────────
        with console.status("[bold yellow]Loading fight card...", spinner="dots"):
            preview_data = fetch_live_data(fight_id)

        fight_card_preview = (
            preview_data.get("LiveEventDetail", {}).get("FightCard", [])
            if preview_data else []
        )

        # ── Fight selection ───────────────────────────────────────────────────
        if fight_card_preview:
            choices = []
            for fight in sorted(fight_card_preview, key=lambda f: f.get("FightOrder", 99)):
                order    = fight.get("FightOrder", "?")
                segment  = fight.get("CardSegment", "")
                fighters = fight.get("Fighters", [])
                red      = fighter_name(fighters[0]) if len(fighters) > 0 else "TBD"
                blue     = fighter_name(fighters[1]) if len(fighters) > 1 else "TBD"

                if order == 1:
                    label = f"  ★  {red}  vs  {blue}  — MAIN EVENT  [{segment}]"
                else:
                    label = f"  {order}.  {red}  vs  {blue}  [{segment}]"

                choices.append(questionary.Choice(title=label, value=(order, red, blue)))

            selected = questionary.checkbox(
                "Select the fight(s) you want to be notified about:",
                choices=choices,
                style=SELECTOR_STYLE,
            ).ask()

            if not selected:
                raise KeyboardInterrupt

            fight_states: dict[int, FightState] = {
                order: FightState(order=order, red=red, blue=blue)
                for order, red, blue in selected
            }
        else:
            console.print("  [dim]Could not load fight card. Enter fight order number:[/dim]")
            order = int(input("  Fight order: "))
            fight_states = {order: FightState(order=order, red="?", blue="?")}

        console.print()
        console.print(
            f"  [green]✓[/green] Tracking [bold]{len(fight_states)}[/bold] fight(s)  ·  "
            f"[dim]{NOTIFS_PER_FIGHT} alerts per fight, {NOTIF_GAP_SECONDS // 60} min apart[/dim]"
        )
        console.print()

        run_monitor(fight_id, fight_states)

    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted. Goodbye.[/yellow]")
    except ValueError as e:
        console.print(f"[red]Invalid input: {e}[/red]")
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
