import os, asyncio, logging

from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

from yt_subs_bot.handlers.handlers import ChatHandlers
from yt_subs_bot.notifier import Notifier
from yt_subs_bot.storage import Storage
from yt_subs_bot.youtube import YouTubeClient


def create_properties():
    return {
        "yt_api_key": os.environ.get("YT_API_KEY"),
        "telegram_token": os.environ.get("TELEGRAM_TOKEN"),
        "connection_string": os.environ.get("CONNECTION_STRING"),
        "poll_interval": int(os.environ.get("POLL_INTERVAL", 60)),
        "log_level": os.environ.get("LOG_LEVEL", "INFO").upper() or "INFO"
    }


def schedule_task(notifier: Notifier, poll_interval: int):
    logging.log(logging.INFO, "Scheduling notifier task")

    async def task():
        while True:
            await notifier.run()
            await asyncio.sleep(poll_interval)

    loop = asyncio.get_event_loop()
    loop.create_task(task())
    logging.log(logging.INFO, "Notifier task scheduled")


def register_handlers(app, handlers):
    logging.log(logging.INFO, "Registering handlers")
    app.add_handler(CommandHandler('attach_chat', handlers.attach_chat_handler))
    app.add_handler(CommandHandler('detach_chat', handlers.detach_chat_handler))
    app.add_handler(CommandHandler('pause_chat', handlers.pause_chat_handler))
    app.add_handler(CommandHandler('resume_chat', handlers.resume_chat_handler))
    app.add_handler(CommandHandler('add_channel', handlers.ask_add_channel_handler))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handlers.text_handler))
    logging.log(logging.INFO, "Handlers registered")


def main():
    props = create_properties()
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=props["log_level"])
    logging.info("Starting bot with properties: {}".format(props))

    app = ApplicationBuilder().token(props["telegram_token"]).build()
    storage = Storage(props["connection_string"])
    youtube_client = YouTubeClient(props["yt_api_key"])
    handlers = ChatHandlers(storage, youtube_client)
    notifier = Notifier(storage, youtube_client, app.bot)

    register_handlers(app, handlers)
    schedule_task(notifier, props["poll_interval"])

    logging.log(logging.INFO, "Starting polling")
    app.run_polling()
