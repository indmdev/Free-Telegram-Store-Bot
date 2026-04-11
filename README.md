# Free Telegram Store Bot

[![GitHub stars](https://img.shields.io/github/stars/indmdev/Free-Telegram-Store-Bot?style=social)](https://github.com/indmdev/Free-Telegram-Store-Bot/stargazers)
[![GitHub issues](https://img.shields.io/github/issues/indmdev/Free-Telegram-Store-Bot)](https://github.com/indmdev/Free-Telegram-Store-Bot/issues)
[![License](https://img.shields.io/github/license/indmdev/Free-Telegram-Store-Bot)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)

> 100% Free Telegram Store Bot for selling and managing your products, services, and orders.

![Preview](https://i.ibb.co/6tvrHzH/v5-1.png)

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🛒 **Product Management** | Add, edit, and manage your products |
| 💳 **Order Processing** | Automated order handling and tracking |
| 💬 **Customer Support** | Built-in messaging with customers |
| 💰 **Payment Integration** | Support for multiple payment methods |
| 📊 **Sales Dashboard** | Track your sales and revenue |

## 🚀 Quick Start

### Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python | 3.10+ | [Download](https://www.python.org/downloads/) |
| Git | Any recent | [Download](https://git-scm.com/) |
| Ngrok | Free account | [Sign up](https://ngrok.com) |
| Telegram Bot | Via @BotFather | [Create](https://t.me/BotFather) |

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/indmdev/Free-Telegram-Store-Bot.git
cd Free-Telegram-Store-Bot

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp config.env.example config.env
```

### Configuration

Edit `config.env` with your credentials:

| Variable | Description | Where to get |
|----------|-------------|--------------|
| `BOT_TOKEN` | Your Telegram bot token | [@BotFather](https://t.me/Botfather) |
| `NGROK_URL` | Your Ngrok webhook URL | Ngrok dashboard |
| `STORE_CURRENCY` | Your store currency | e.g., USD, EUR |

### Running

```bash
# Start Ngrok (in a separate terminal)
ngrok http 5000

# Run the bot
python store_main.py
```

## 📞 Get Help

| Channel | Link |
|---------|------|
| Developer | [@InDMDev](https://t.me/InDMDev) |
| Updates | [@InDMDevBots](https://t.me/InDMDevBots) |

## 🧪 Demo

| Bot | Link |
|-----|------|
| Classic Bot | [@InDMShopBot](https://t.me/InDMShopBot) |
| V5 Shop | [@InDMShopV5Bot](https://t.me/inDMShopV5Bot) |

## ⚠️ Disclaimer

> **Note:** Use this program only for legal purposes. The developer is not responsible for any illegal activity.

## 🙏 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

README optimized with [Gingiris README Generator](https://gingiris.github.io/github-readme-generator/)
