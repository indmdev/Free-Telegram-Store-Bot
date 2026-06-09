# Free-Telegram-Store-Bot

I made this Bot Free 100%.

> Message me at [@InDMDev](https://t.me/InDMDev) for your advanced bot customizations.
> For more Bots like this, and to be the first to know when I publish free bots, join my channel: [@InDMDevBots](https://t.me/InDMDevBots)

# Digital Products Store — Telegram Bot

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![python-telegram-bot](https://img.shields.io/badge/python--telegram--bot-20.7-26A5E4?logo=telegram&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?logo=sqlalchemy&logoColor=white)
![SQLite](https://img.shields.io/badge/database-SQLite%20%7C%20PostgreSQL-003B57?logo=sqlite&logoColor=white)
![Platform](https://img.shields.io/badge/OS-Windows%20%7C%20Linux%20%7C%20macOS-555)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A Telegram bot for selling digital products (software license keys and downloadable files).
Customers browse a catalog, top up an internal wallet with crypto or a card, and spend that balance on products.
License keys are delivered automatically from inventory; file products are delivered as download links.
A full in-Telegram admin panel handles products, categories, stock, orders, disputes, users, broadcasts, and store settings.

Built with **Python**, **python-telegram-bot v20** (async), and **SQLAlchemy** (SQLite by default).

---

## Table of Contents

1. [Features](#features)
2. [Tech Stack](#tech-stack)
3. [Project Structure](#project-structure)
4. [Prerequisites](#prerequisites)
5. [Step 1 — Get your Telegram credentials](#step-1--get-your-telegram-credentials)
6. [Step 2 — Clone the repository](#step-2--clone-the-repository)
7. [Step 3 — Create a virtual environment](#step-3--create-a-virtual-environment)
8. [Step 4 — Install dependencies](#step-4--install-dependencies)
9. [Step 5 — Configure environment variables](#step-5--configure-environment-variables)
10. [Step 6 — Run the bot](#step-6--run-the-bot)
11. [Step 7 — Use the bot (`/start` and `/admin`)](#step-7--use-the-bot-start-and-admin)
12. [Optional — Real-time CryptoBot webhooks](#optional--real-time-cryptobot-webhooks)
13. [Optional — Keep the bot running 24/7](#optional--keep-the-bot-running-247)
14. [Database notes](#database-notes)
15. [Troubleshooting](#troubleshooting)
16. [Security notes](#security-notes)

---

## Features

- 🛒 Product catalog with categories and subcategories
- 🔑 Two product types: **license keys** (auto-delivered from inventory) and **downloadable files** (delivered as links)
- 💰 Internal wallet — users top up, then spend the balance on purchases
- 💳 Two top-up methods, both optional and independently toggled by config:
  - **CryptoBot** — pay with any cryptocurrency via [@CryptoBot](https://t.me/CryptoBot)
  - **Card** — native in-Telegram card payments via Telegram Payments
- 🛠 Full in-Telegram **admin panel**: products, categories, stock/restock, orders, disputes, users (ban/unban), broadcasts, and store settings
- ⏱ Background jobs for payment verification and periodic availability broadcasts

## Tech Stack

| Component | Version |
|-----------|---------|
| Python | 3.10+ recommended (3.9+ supported) |
| python-telegram-bot | 20.7 |
| SQLAlchemy | 2.0.23 |
| Database | SQLite (default) or PostgreSQL |

---

**How it fits together:** `bot.py` is the single wiring point — it validates config (`config/`), initializes the database (`database/`), then registers all the `handlers/`. Handlers talk to Telegram and call into `services/` (external APIs) and `utils/` (keyboards + helpers); all data access goes through `get_db_session()` in `database/db.py`.

---

## Prerequisites

Install these before you start:

- **Git** — [git-scm.com/downloads](https://git-scm.com/downloads)
- **Python 3.10+** — [python.org/downloads](https://www.python.org/downloads/)
  - On **Windows**, tick **“Add Python to PATH”** in the installer.
- A **Telegram account**

Verify your tools are installed:

**Windows (PowerShell):**
```powershell
git --version
python --version
```

**Linux / macOS:**
```bash
git --version
python3 --version
```

---

## Step 1 — Get your Telegram credentials

You need a **bot token** and your **admin Telegram ID**. The two payment keys are optional.

### 1a. Bot token (required)
1. Open [@BotFather](https://t.me/BotFather) in Telegram.
2. Send `/newbot` and follow the prompts (choose a name and a username ending in `bot`).
3. Copy the **API token** it gives you (looks like `1234567890:ABCdef...`).

### 1b. Your admin Telegram ID (required)
1. Open [@userinfobot](https://t.me/userinfobot) in Telegram.
2. Send any message; it replies with your numeric **Id** (e.g. `123456789`).
3. This ID is the only account that can access `/admin`.

### 1c. CryptoBot API key (optional — enables crypto top-ups)
1. Open [@CryptoBot](https://t.me/CryptoBot) → **Crypto Pay** → **My Apps** → create an app.
2. Copy the **API token**. Leave blank to disable the CryptoBot option.

### 1d. Telegram Payments provider token (optional — enables card top-ups)
1. Open [@BotFather](https://t.me/BotFather) → select your bot → **Payments**.
2. Connect a payment provider and copy the **provider token**. Leave blank to disable the Card option.
   > Card-provider availability is region-dependent — pick a provider supported in your country. Use the provider’s **TEST** token while developing.

---

## Step 2 — Clone the repository

**Windows (PowerShell) and Linux / macOS** (same commands):
```bash
git clone <YOUR_REPOSITORY_URL>
cd FreeTelegramStoreBot
```
> Replace `<YOUR_REPOSITORY_URL>` with your repo’s clone URL, and `FreeTelegramStoreBot` with the folder name if it differs.

---

## Step 3 — Create a virtual environment

A virtual environment keeps this project’s dependencies isolated.

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```
> If activation is blocked by execution policy, run once:
> `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned.`
> (or use the CMD activator: `venv\Scripts\activate.bat`).

**Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

When active, your shell prompt is prefixed with `(venv)`. To leave it later, run `deactivate`.

---

## Step 4 — Install dependencies

With the virtual environment active:

**Windows (PowerShell):**
```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

**Linux / macOS:**
```bash
python3 -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## Step 5 — Configure environment variables

Copy the example file to a real `.env` and fill in your values.

**Windows (PowerShell):**
```powershell
Copy-Item .env.example .env
notepad .env
```

**Linux / macOS:**
```bash
cp .env.example .env
nano .env
```

Fill in the variables:

| Variable | Required | Description |
|----------|:--------:|-------------|
| `BOT_TOKEN` | ✅ | Bot token from [@BotFather](https://t.me/BotFather) (Step 1a). |
| `ADMIN_TELEGRAM_ID` | ✅ | Your numeric Telegram ID (Step 1b). The only admin account. |
| `ADMIN_TELEGRAM_USERNAME` | ➖ | Your username without `@` (used in some messages). |
| `DATABASE_URL` | ➖ | Defaults to `sqlite:///bot_database.db`. Set a PostgreSQL URL to use Postgres. |
| `CRYPTO_BOT_API_KEY` | ➖ | CryptoBot Crypto Pay token (Step 1c). Blank disables crypto top-up. |
| `TELEGRAM_PROVIDER_TOKEN` | ➖ | Telegram Payments provider token (Step 1d). Blank disables card top-up. |
| `PAYMENT_CURRENCY` | ➖ | Currency for card invoices (default `USD`). Must be USD-denominated to match wallet amounts. |

> The bot **will not start** until at least `BOT_TOKEN` and `ADMIN_TELEGRAM_ID` are set — it validates these on startup and exits with a clear message if either is missing.

---

## Step 6 — Run the bot

The database is created and seeded automatically on first run — there is no separate setup command.

**Windows (PowerShell):**
```powershell
python bot.py
```

**Linux / macOS:**
```bash
python3 bot.py
```

You should see log lines ending with:
```
Bot started successfully!
```
Leave this terminal open — the bot runs as long as the process is running. Press **Ctrl+C** to stop it.

---

## Step 7 — Use the bot (`/start` and `/admin`)

With the bot running:

1. Open Telegram and search for your bot by the username you chose in Step 1a.
2. Send **`/start`** — you’ll get the welcome message and the main menu (Products, Top Up, Order History, Availability, Support).
3. Send **`/admin`** — if your Telegram ID matches `ADMIN_TELEGRAM_ID`, the **admin panel** opens (Product Management, User Management, Order Management, Store Settings, Broadcast).

> If `/admin` says access is denied or does nothing, your `ADMIN_TELEGRAM_ID` doesn’t match your account — recheck Step 1b, fix `.env`, and restart the bot.

**🎉 That’s it — your bot is live.** A typical first run as admin: open `/admin` → **Product Management** → create a category, then a product, then **Restock Keys** to add inventory. As a user, `/start` → **Top Up** to fund the wallet, then buy a product.

---

## Optional — Real-time CryptoBot webhooks

By default, CryptoBot payments are confirmed by polling every ~30 seconds (no extra setup). For **instant** confirmation, run the included webhook server alongside the bot.

1. Start the webhook server (separate terminal, same virtual environment):

   **Windows (PowerShell):**
   ```powershell
   python webhook_server.py
   ```
   **Linux / macOS:**
   ```bash
   python3 webhook_server.py
   ```
   It listens on port **5000**.

2. Expose it over HTTPS (e.g. with [ngrok](https://ngrok.com/)):
   ```bash
   ngrok http 5000
   ```

3. In [@CryptoBot](https://t.me/CryptoBot) → **Crypto Pay → My Apps → Webhooks**, set the URL to:
   ```
   https://<your-ngrok-or-domain>/webhook/cryptobot
   ```

> On Windows, you can launch the bot and the webhook server together with `start_with_webhooks.bat` (you still run ngrok yourself).
> Card payments need no webhook — Telegram delivers their confirmation through the bot’s normal update polling.

---

## Optional — Keep the bot running 24/7

### Linux (systemd)

Create `/etc/systemd/system/digitalstore-bot.service` (adjust paths and `User`):

```ini
[Unit]
Description: Digital Products Store Telegram Bot
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/home/youruser/FreeTelegramStoreBot
ExecStart=/home/youruser/FreeTelegramStoreBot/venv/bin/python bot.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Then enable and start it:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now digitalstore-bot
sudo systemctl status digitalstore-bot      # check it's running
journalctl -u digitalstore-bot -f            # follow logs
```

### Windows
Keep the `python bot.py` window open, or run it as a background/scheduled task (e.g. Task Scheduler), or host it on a Linux server using the steps above.

---

## Database notes

- **Default:** SQLite, stored in `bot_database.db` in the project folder. Created automatically on first run.
- **Backup:** simply copy the `bot_database.db` file.
- **Reset (deletes all data):** stop the bot, delete `bot_database.db`, and start the bot again to recreate an empty database.

  **Windows (PowerShell):**
  ```powershell
  Remove-Item bot_database.db
  ```
  **Linux / macOS:**
  ```bash
  rm bot_database.db
  ```
- **PostgreSQL (optional):** set `DATABASE_URL` to a Postgres URL, e.g.
  `postgresql+psycopg2://user:password@localhost:5432/digitalstore`
  (The `psycopg2-binary` driver is already in `requirements.txt`).
- **Upgrading an older database:** if you’re migrating an existing SQLite DB created before category fields were made optional, run once:
  `python migrations/001_make_category_id_nullable.py` (not needed for fresh installs).

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `Configuration error: BOT_TOKEN is required` | `.env` is missing or `BOT_TOKEN`/`ADMIN_TELEGRAM_ID` is empty. Recheck Step 5 and that `.env` is in the project root. |
| `/admin` denied or no response | `ADMIN_TELEGRAM_ID` doesn’t match your account. Re-get your ID (Step 1b), update `.env`, restart. |
| `ModuleNotFoundError` / import errors | The virtual environment isn’t active or deps aren’t installed. Re-do Step 3 and Step 4. |
| `python` not found (Windows) | Reinstall Python with **“Add Python to PATH”** ticked, or use the `py` launcher (`py bot.py`). |
| Activation blocked (Windows) | `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`, then re-activate. |
| Card button shows “not configured” | `TELEGRAM_PROVIDER_TOKEN` is blank or invalid — see Step 1d. |
| Crypto top-up not auto-confirming | Verify `CRYPTO_BOT_API_KEY`, check the console for API errors, or set up webhooks for instant confirmation. |
| Bot stops when you close the terminal | That’s expected — use the [24/7 section](#optional--keep-the-bot-running-247). |


## License

Released under the [MIT License](LICENSE).

> ⚠️ **Note: Use this program only for legal purposes.**
> InDMDev is not and will not be responsible for any illegal activity/activities you indulge in using any of our programs.
