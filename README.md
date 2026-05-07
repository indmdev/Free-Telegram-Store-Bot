# Free Telegram Store Bot

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](#quick-start)
[![License](https://img.shields.io/github/license/indmdev/Free-Telegram-Store-Bot)](LICENSE)
[![Stars](https://img.shields.io/github/stars/indmdev/Free-Telegram-Store-Bot?style=social)](https://github.com/indmdev/Free-Telegram-Store-Bot)

A free Telegram store bot for selling digital products, managing orders, and handling simple storefront operations from chat.

![Classic bot preview](https://i.ibb.co/6tvrHzH/v5-1.png)

## Table of Contents

- [Why this project](#why-this-project)
- [Features](#features)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [How it works](#how-it-works)
- [Project structure](#project-structure)
- [Demo and support](#demo-and-support)
- [Legal notice](#legal-notice)

## Why this project

This repo gives you a ready-made Telegram commerce bot without a paid template or closed-source setup. It is a good fit if you want to:

- launch a simple Telegram storefront quickly
- manage products and orders inside Telegram
- customize the bot for your own product catalog

## Features

- Product and category management for store admins
- Order management flow inside Telegram chats
- User-facing storefront with buttons and simple navigation
- Webhook-based bot setup using Flask + pyTelegramBotAPI
- Environment-based configuration through `config.env`
- Optional custom bot work and upgraded hosted version from the author

## Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/indmdev/Free-Telegram-Store-Bot.git
cd Free-Telegram-Store-Bot
```

### 2. Install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

### 3. Create a Telegram bot

- Open [@BotFather](https://t.me/BotFather)
- Create a new bot
- Copy the bot token

### 4. Expose a public webhook URL

The bot expects a public HTTPS endpoint. The original setup uses [ngrok](https://ngrok.com/):

```bash
ngrok http 5000
```

Copy the HTTPS forwarding URL.

### 5. Configure `config.env`

```env
NGROK_HTTPS_URL=https://your-ngrok-url.ngrok-free.app
TELEGRAM_BOT_TOKEN=123456:telegram-bot-token
STORE_CURRENCY=USD
```

### 6. Start the bot

```bash
python store_main.py
```

If the webhook is valid, the app will register it automatically and start serving Telegram updates.

## Configuration

The default environment file includes:

- `NGROK_HTTPS_URL`: public HTTPS URL for Telegram webhooks
- `TELEGRAM_BOT_TOKEN`: token created in BotFather
- `STORE_CURRENCY`: checkout currency shown in the store

## How it works

- `store_main.py` starts the Flask app and Telegram bot
- Incoming webhook events are passed to the bot handler
- Product, category, purchase, and DB helpers are split into separate modules
- Payments and order flows are handled in the supporting Python files

## Project structure

```text
store_main.py       Flask app + Telegram webhook entrypoint
InDMCategories.py   category-related logic
InDMDevDB.py        database helpers
purchase.py         purchase and order flow
config.env          local runtime configuration
requirements.txt    Python dependencies
```

## Demo and support

- Upgraded bot: [@InDMShopV5Bot](https://t.me/inDMShopV5Bot)
- Demo bot: [@InDMShopBot](https://t.me/InDMShopBot)
- Demo market: [@InDMMarketbot](https://t.me/InDMMarketbot)
- Author contact: [@InDMDev](https://t.me/InDMDev)
- Updates channel: [@InDMDevBots](https://t.me/InDMDevBots)

## Legal notice

Use this project only for legal purposes. The original author states they are not responsible for illegal activity carried out with this software.
