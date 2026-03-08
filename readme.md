# UFC Fight Notifier

Get SMS alerts on your phone before your selected UFC fights start — so you never miss a moment.

## How it works

1. You enter a UFC event (or leave blank for today's Fight Night).
2. The fight card loads and you **pick one or more fights** using an arrow-key selector.
3. For each selected fight, the program monitors the live event and sends you **3 SMS alerts** when that fight is about to start, spaced **2 minutes apart**:
   - Alert 1 — fight is up next
   - Alert 2 — starting very soon
   - Alert 3 — IT'S TIME
4. The program stops automatically once every selected fight has sent all 3 alerts.

## Prerequisites

- Python 3.10+
- A [Twilio](https://www.twilio.com/) account with:
  - An Account SID and Auth Token
  - A Messaging Service SID

## Installation

```sh
git clone https://github.com/YOUR_USERNAME/UFC-Notif.git
cd UFC-Notif
pip install -r requirements.txt
```

Copy the credentials template and fill in your values:

```sh
cp creds.example.py creds.py
```

Edit `creds.py`:

```python
account_sid           = 'ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
auth_token            = 'your_auth_token'
messaging_service_sid = 'MGxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
phone_receiver        = '+15140000000'
```

## Usage

```sh
python3 main.py
```

**Setup prompts:**

1. **Event number** — leave blank for today's Fight Night, or enter a number (e.g. `300` for UFC 300, `fight-night-march-22-2025` for a specific Fight Night).
2. **Fight selection** — an interactive list of the full fight card is shown. Use `↑ / ↓` to navigate and `Space` to select one or more fights. Press `Enter` to confirm.

The program then monitors the live event, refreshing every 60 seconds, and sends SMS alerts when each selected fight is about to start.

Press `Ctrl+C` at any time to exit.

## Configuration

All tunable constants are at the top of `main.py`:

| Constant | Default | Description |
|---|---|---|
| `POLL_INTERVAL` | `60` | Seconds between API refreshes |
| `NOTIF_GAP_SECONDS` | `120` | Seconds between the 3 alerts per fight |
| `NOTIFS_PER_FIGHT` | `3` | Number of alerts sent per fight |
| `MAX_CONSECUTIVE_ERRORS` | `5` | API failures before the program exits |

## Security

`creds.py` is listed in `.gitignore` and will **never be committed**. Use `creds.example.py` as a reference template.

## Dependencies

| Package | Purpose |
|---|---|
| `requests` | HTTP requests to the UFC API |
| `beautifulsoup4` | Scraping the event page for the fight ID |
| `twilio` | Sending SMS notifications |
| `rich` | Terminal UI (tables, panels, colors) |
| `questionary` | Interactive arrow-key fight selector |

## License

MIT
