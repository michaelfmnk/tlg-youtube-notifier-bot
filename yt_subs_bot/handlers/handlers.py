from yt_subs_bot.storage import Storage
from telegram import Update, constants
from telegram.ext import ContextTypes
from yt_subs_bot.youtube import YouTubeClient


class ChatHandlers:
    def __init__(self, storage: Storage, yt: YouTubeClient):
        self.storage = storage
        self.yt = yt

    async def pause_chat_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.message.chat.id
        chat = self.storage.get_chat(chat_id=chat_id)
        if chat:
            self.storage.set_paused(chat_id=chat_id, paused=True)
            await update.message.reply_text('Chat paused')
        else:
            await update.message.reply_text('Chat not found')

    async def resume_chat_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.message.chat.id
        chat = self.storage.get_chat(chat_id=chat_id)
        if chat:
            self.storage.set_paused(chat_id=chat_id, paused=False)
            await update.message.reply_text('Chat resumed')
        else:
            await update.message.reply_text('Chat not found')

    async def detach_chat_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.message.chat.id
        chat = self.storage.get_chat(chat_id=chat_id)
        if chat:
            self.storage.delete_chat(chat_id=chat_id)
            await update.message.reply_text('Chat detached')
        else:
            await update.message.reply_text('Chat not found')

    async def attach_chat_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_type = update.message.chat.type
        if chat_type != constants.ChatType.GROUP:
            await update.message.reply_text('This command can only be used in a group chat')
            return
        chat_id = update.message.chat.id
        creator_id = update.message.from_user.id
        chat = self.storage.get_chat_or_new(chat_id=chat_id, creator_id=creator_id)
        if chat:
            await update.message.reply_text('Chat attached')
        else:
            await update.message.reply_text('Error while attaching chat')

    @staticmethod
    async def ask_add_channel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text('Please, send me channel handle or link to channel')
        context.user_data['state'] = 'waiting_for_channel_handle'

    async def text_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        state = context.user_data.get('state')
        context.user_data['state'] = None
        if state == 'waiting_for_channel_handle':
            await self.handle_add_channel(update)

    async def handle_add_channel(self, update: Update):
        message_text: str = update.message.text
        chat_id: int = update.message.chat.id
        chat = self.storage.get_chat(chat_id)
        if not chat:
            creator_id = update.message.from_user.id
            self.storage.create_chat(chat_id, creator_id)

        channel_id = self.yt.get_channel_id(message_text)
        if not channel_id:
            channel_id = self.yt.get_channel_id_by_link(message_text)
            if not channel_id:
                await update.message.reply_text('Could not identify channel')
                return

        self.storage.add_channel(chat_id, channel_id)
        await update.message.reply_text('Channel added')
