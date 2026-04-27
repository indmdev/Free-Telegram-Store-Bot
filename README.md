[![License](https://img.shields.io/github/license/indmdev/Free-Telegram-Store-Bot)](./LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](#setup)
[![Telegram](https://img.shields.io/badge/Telegram-Bot-26A5E4?logo=telegram&logoColor=white)](#overview)

# Free Telegram Store Bot

Free Telegram Store Bot is a Python-based Telegram storefront for selling digital products and managing orders directly inside Telegram. It combines a Flask webhook app, a Telegram bot interface, SQLite-backed data storage, and payment integrations in one project.

## Table of Contents
- [Overview](#overview)
- [What it includes](#what-it-includes)
- [Setup](#setup)
- [Configuration](#configuration)
- [How to run](#how-to-run)
- [Project structure](#project-structure)
- [Notes](#notes)

## Overview

This project is useful if you want to:

- list products and categories in Telegram
- accept and manage orders
- handle admin and customer flows from one bot
- run the bot with a webhook-based deployment model

## What it includes

- Telegram bot built with `telebot`
- Flask webhook endpoint for receiving updates
- SQLite-based local data storage
- category, product, order, and purchase handlers
- payment-related configuration hooks
- environment-based configuration via `config.env`

## Setup

### Requirements
- Python 3.10+
- Git
- An ngrok account or another public webhook URL
- A Telegram bot token from [@BotFather](https://t.me/BotFather)

### Install
```bash
git clone https://github.com/indmdev/Free-Telegram-Store-Bot.git
cd Free-Telegram-Store-Bot
pip install -r requirements.txt
```

## Configuration

Edit `config.env` and set at least:

```env
TELEGRAM_BOT_TOKEN=your_bot_token
NGROK_HTTPS_URL=https://your-public-url.ngrok-free.app
STORE_CURRENCY=USD
STORE_NAME=Telegram Store
```

If you use ngrok locally, start it before running the bot so Telegram can reach your webhook URL.

## How to run

```bash
python store_main.py
```

After startup, Telegram requests will be delivered to the configured webhook URL and the bot can begin serving users.

## Project structure

```text
store_main.py      Main Flask + Telegram bot entry point
config.py          Runtime configuration and validation
InDMDevDB.py       Database helpers
InDMCategories.py  Category and product navigation logic
purchase.py        Purchase and checkout flows
utils.py           Shared helpers
guide.txt          Original quick guide
```

## Notes

- Keep secrets in `config.env`, not in source control.
- Review the code and payment configuration before using it in production.
- The original author also links to advanced paid customizations in the repository.

## License

See [`LICENSE`](./LICENSE).
