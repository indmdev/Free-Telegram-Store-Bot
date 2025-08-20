# gunicorn_config.py
import os
import telebot
import logging

logger = logging.getLogger(__name__)

def post_fork(server, worker):
    """
    Gunicorn hook to set the webhook after the worker is forked.
    """
    webhook_url = os.getenv('WEBHOOK_URL')
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')

    if webhook_url and bot_token:
        try:
            bot = telebot.TeleBot(bot_token)
            bot.remove_webhook()
            bot.set_webhook(url=webhook_url)
            logger.info(f"Webhook set successfully to {webhook_url} for worker {worker.pid}")
        except Exception as e:
            logger.error(f"Failed to set webhook for worker {worker.pid}: {e}")
    else:
        logger.warning("WEBHOOK_URL or TELEGRAM_BOT_TOKEN not set. Webhook not configured.")
