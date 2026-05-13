# Free Telegram Store Bot

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Flask](https://img.shields.io/badge/flask-3.0-lightgrey)
![License](https://img.shields.io/github/license/indmdev/Free-Telegram-Store-Bot)

A free Telegram store bot for selling digital products or services, collecting orders, and managing a simple storefront workflow.

## Table of Contents
- [Features](#features)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Screenshots](#screenshots)
- [Notes](#notes)
- [License](#license)

## Features
- Telegram bot workflow for product listings and order handling
- Flask-based local service components
- Environment-based configuration with `config.env`
- Simple Python entrypoint for local deployment
- Easy to customize for private stores or service catalogs

## Project Structure

```text
.
├── store_main.py
├── purchase.py
├── utils.py
├── config.py
├── config.env
├── requirements.txt
└── guide.txt
```

## Requirements
- Python 3.10 or newer
- Git
- A Telegram bot token from [@BotFather](https://t.me/BotFather)
- An [ngrok](https://ngrok.com/) tunnel if your deployment flow needs a public callback URL

## Installation
1. Clone the repository:

   ```bash
   git clone https://github.com/indmdev/Free-Telegram-Store-Bot.git
   cd Free-Telegram-Store-Bot
   ```

2. Create and activate a virtual environment (recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

   On Windows:

   ```powershell
   .venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Configuration
1. Create your bot with [@BotFather](https://t.me/BotFather) and copy the bot token.
2. Open `config.env` and fill in the required values.
3. Add your ngrok URL if your bot flow depends on external callbacks.
4. Set the store currency and any additional project-specific values.

## Usage
1. Start ngrok if you need a public URL:

   ```bash
   ngrok http 5000
   ```

2. Run the bot from the project folder:

   ```bash
   python store_main.py
   ```

3. Open Telegram and test the bot with your configured bot account.

## Screenshots

![Store bot preview](https://i.ibb.co/6tvrHzH/v5-1.png)

## Notes
- This repository is presented as a free version of the author's Telegram store bot.
- For advanced customization, the original README points users to [@InDMDev](https://t.me/InDMDev).
- Use this project only for legal and compliant purposes.

## License
See [LICENSE](LICENSE).
