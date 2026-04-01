# Free Telegram Store Bot 🤖

> 🛒 A 100% free Telegram bot for selling products and managing orders

A complete Telegram store solution for selling products and services. No fees, no subscriptions — just a powerful bot that handles your entire e-commerce workflow.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Telegram](https://img.shields.io/badge/Telegram-Bot-blue)](https://t.me)

## ✨ Features

- 🛍️ **Product Management** — Add, edit, remove products easily
- 💳 **Order Processing** — Automated order workflow
- 📦 **Inventory Tracking** — Real-time stock management
- 💬 **Customer Chat** — Direct messaging with buyers
- 📊 **Sales Dashboard** — Track orders and revenue
- 🌐 **Multi-currency** — Support for various currencies

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Telegram Bot Token (from [@BotFather](https://t.me/Botfather))
- Ngrok account (for local development)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/indmdev/Free-Telegram-Store-Bot.git
cd Free-Telegram-Store-Bot

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp config.env.example config.env

# 4. Edit config.env with your settings
# - Add your Telegram Bot Token
# - Add your Ngrok URL
# - Set your store currency

# 5. Run the bot
python store_main.py
```

### Setup with Ngrok (Local Development)

```bash
# 1. Sign up at https://ngrok.com and get your auth token

# 2. Start Ngrok
ngrok http 5000

# 3. Copy the forwarding URL to your config.env

# 4. Set up your bot with @BotFather
# - Create a new bot
# - Copy the API token to config.env
```

## 📱 Demo

Test the bot directly:

| Version | Link | Description |
|---------|------|-------------|
| **Latest** | [@InDMShopV5Bot](https://t.me/InDMShopV5Bot) | New version with all features |
| **Classic** | [@InDMShopBot](https://t.me/InDMShopBot) | Original version |

## 📸 Screenshots

![Interface](https://i.ibb.co/6tvrHzH/v5-1.png)

## 🛠️ Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Start the store bot |
| `/products` | Browse available products |
| `/orders` | View your orders |
| `/cart` | View shopping cart |
| `/help` | Get help with commands |

## ⚙️ Configuration

Edit `config.env`:

```env
BOT_TOKEN=your_telegram_bot_token
NGROK_URL=https://your-ngrok-url.ngrok.io
CURRENCY=USD
ADMIN_ID=your_telegram_user_id
```

## 🔧 API Reference

### Bot Methods

```
store_main.py
├── handle_start()      # Initialize bot
├── handle_products()   # List products
├── handle_order()      # Process order
└── handle_payment()    # Handle payments
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📢 Stay Updated

- [Telegram Channel](https://t.me/InDMDevBots) — Get notified about new releases
- [Contact Developer](https://t.me/InDMDev) — Custom bot development

## ⚠️ Disclaimer

Use this program only for legal purposes. The developer is not responsible for any illegal activity.

## 📄 License

This project is MIT License — see the [LICENSE](LICENSE) file for details.

---

*README optimized with [Gingiris README Generator](https://gingiris.github.io/github-readme-generator/)*
