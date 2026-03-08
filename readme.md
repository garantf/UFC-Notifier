<div align="center">

<img src="assets/logo.png" alt="UFC" width="480"/>

### Fight Notifier

**Get SMS and/or email alerts before your selected UFC fights start.**

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![Twilio](https://img.shields.io/badge/SMS-Twilio-red?logo=twilio&logoColor=white)
![Gmail](https://img.shields.io/badge/Email-Gmail-red?logo=gmail&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

</div>

---

## How it works

1. Run the script and enter the UFC event number (or leave blank for today's Fight Night).
2. The full fight card loads — use the **arrow-key selector** to pick one or more fights.
3. Choose how to receive alerts: **SMS**, **Email**, or **both**.
4. The program monitors the live event and sends you **3 alerts** per fight when it's about to start, spaced **2 minutes apart**:

| Alert | Timing | Message |
|:---:|---|---|
| 1/3 | Fight before yours just ended | *"Your fight is up next!"* |
| 2/3 | +2 min | *"Starting very soon!"* |
| 3/3 | +4 min | *"IT'S TIME — turn it on!"* |

5. The program exits automatically once all selected fights have sent their 3 alerts.

---

## Screenshots

### Startup & fight selection

```
╭──────────────────────────────────────────────────────────────────╮
│      ████████   ████████   ████████████████   ██████████████     │
│     ████████    ███████   █████████████████  ███████████████     │
│     ████████   ████████   ████████████████  ████████████████     │
│    ████████   ████████                      ███████              │
│    ████████   ████████   ████████████████  ████████              │
│   ████████   ████████   ████████████████   ███████               │
│   ████████   ████████   ████████████████  ████████               │
│  ████████   ████████   ████████           ███████                │
│ ████████████████████  ████████           █████████████████       │
│ ███████████████████   ████████           █████████████████       │
│  █████████████████   ████████             ███████████████        │
╰──────────────────────────────────────────────────────────────────╯

╭─────────────────────────────────────────────────────────────────╮
│                                                                 │
│  Welcome to UFC Fight Notifier                                  │
│                                                                 │
│  Select one or more fights to track.                            │
│  For each fight you'll receive 3 SMS alerts when it's about     │
│  to start, 2 minutes apart.                                     │
│                                                                 │
│  Press Space to select · Enter to confirm · Ctrl+C to quit      │
│                                                                 │
╰─────────────────────────────────────────────────────────────────╯

──────────────────────────────────── Setup ────────────────────────────────────

  Event number (): 323

  ✓ Event found  (ID: 1293)
  ✓ Loading fight card...

? Select the fight(s) you want to be notified about:
 ❯ ◉   ★  Merab Dvalishvili  vs  Petr Yan  — MAIN EVENT  [Main]
   ◯   2.  Sean Strickland  vs  Dricus du Plessis  [Main]
   ◉   3.  Brandon Moreno  vs  Amir Albazi  [Main]
   ◯   4.  Sergei Pavlovich  vs  Tai Tuivasa  [Prelim]
   ◯   5.  Joaquin Buckley  vs  Vicente Luque  [Prelim]
   ◯   6.  Jailton Almeida  vs  Curtis Blaydes  [Prelim]

? How do you want to receive alerts?
 ❯ ◉ SMS  (Twilio)
   ◯ Email  (Gmail)
```

### Live monitoring view

```
╭──────────────────────────────────────────────────────────────────╮
│  ... UFC logo ...                                                │
╰──────────────────────────────────────────────────────────────────╯

╭──────────────────────────────╮  ╭──────────────────────────────────╮
│  UFC 323: Dvalishvili vs Yan │  │  Alerts  3/6                     │
│  T-Mobile Arena, Las Vegas   │  │                                  │
│  December 6, 2025            │  │  ●●○  next in 1m 43s  #3 Moreno │
╰──────────────────────────────╯  │  ○○○  waiting...      #1 Main   │
                                  ╰──────────────────────────────────╯

╭─ Fight Card · tracking 2 fight(s) ────────────────────────────────────────────────────────────────╮
│  #    Segment   Red Corner              vs   Blue Corner             Status      Result / Live Info │
│ ──────────────────────────────────────────────────────────────────────────────────────────────── │
│  ► 1   Main     Merab Dvalishvili       vs   Petr Yan                ◦ Upcoming                   │
│    2   Main     Sean Strickland         vs   Dricus du Plessis       ◦ Upcoming                   │
│  ► 3   Main     Brandon Moreno          vs   Amir Albazi             ● Live      Round 2 — 3:45   │
│    4   Prelim   Sergei Pavlovich        vs   Tai Tuivasa             ✓ Final     Pavlovich · KO R1│
│    5   Prelim   Joaquin Buckley         vs   Vicente Luque           ✓ Final     Buckley · UD R3  │
│    6   Prelim   Jailton Almeida         vs   Curtis Blaydes          ✓ Final     Almeida · Sub R2 │
╰───────────────────────────────────────────────────────────────────────────────────────────────────╯

  Last updated: 22:14:38  ·  Press Ctrl+C to exit

  Next refresh in 47s...
```

### Completion summary

```
────────────────────────────────── All done ──────────────────────────────────

╭─ Notification summary ──────────────────────────────────────────────────────╮
│  Brandon Moreno vs Amir Albazi  (fight #3)                                  │
│    ✓  [22:03:11]  Alert 1/3                                                 │
│    ✓  [22:05:11]  Alert 2/3                                                 │
│    ✓  [22:07:12]  Alert 3/3                                                 │
│                                                                             │
│  Merab Dvalishvili vs Petr Yan  (fight #1)                                  │
│    ✓  [23:41:05]  Alert 1/3                                                 │
│    ✓  [23:43:06]  Alert 2/3                                                 │
│    ✓  [23:45:07]  Alert 3/3                                                 │
╰─────────────────────────────────────────────────────────────────────────────╯
```

---

## Prerequisites

- Python 3.10+
- **For SMS** — a [Twilio](https://www.twilio.com/) account with an Account SID, Auth Token, and Messaging Service SID
- **For Email** — a Gmail account with an [App Password](https://support.google.com/accounts/answer/185833) enabled

---

## Installation

```sh
git clone https://github.com/garantf/UFC-Notifier.git
cd UFC-Notifier
pip install -r requirements.txt
```

Copy the credentials template and fill in your values:

```sh
cp creds.example.py creds.py
```

Edit `creds.py`:

```python
# Twilio — for SMS
account_sid           = 'ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
auth_token            = 'your_auth_token'
messaging_service_sid = 'MGxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
phone_receiver        = '+15140000000'      # E.164 format

# Gmail — for Email
email_user      = 'your_gmail@gmail.com'
email_password2 = 'your_16_char_app_password'
email_receiver  = 'receiver@example.com'   # or number@txt.bell.ca for email-to-SMS
```

---

## Usage

```sh
python3 main.py
```

| Prompt | Description |
|---|---|
| **Event number** | Leave blank for today's Fight Night, or enter a number (`300` for UFC 300) or a slug (`fight-night-march-22-2025`) |
| **Fight selection** | `↑ / ↓` to navigate, `Space` to check/uncheck, `Enter` to confirm |
| **Alert method** | Choose SMS, Email, or both — `Space` to toggle, `Enter` to confirm |

---

## Configuration

All tunable constants live at the top of `main.py`:

| Constant | Default | Description |
|---|---|---|
| `POLL_INTERVAL` | `60` | Seconds between live API refreshes |
| `NOTIF_GAP_SECONDS` | `120` | Seconds between each of the 3 alerts |
| `NOTIFS_PER_FIGHT` | `3` | Number of alerts per fight |
| `MAX_CONSECUTIVE_ERRORS` | `5` | API failures tolerated before exiting |

---

## Dependencies

| Package | Purpose |
|---|---|
| `requests` | HTTP calls to the UFC live API |
| `beautifulsoup4` | Scrapes the event page to find the fight ID |
| `twilio` | Sends SMS notifications |
| `rich` | Terminal UI — tables, panels, colors |
| `questionary` | Interactive arrow-key fight & method selector |
| `smtplib` *(stdlib)* | Sends email notifications via Gmail SMTP |

---

## Security

`creds.py` is in `.gitignore` and will never be committed. Use `creds.example.py` as the reference template. Never hardcode credentials in `main.py`.

---

## License

MIT © [garantf](https://github.com/garantf)
