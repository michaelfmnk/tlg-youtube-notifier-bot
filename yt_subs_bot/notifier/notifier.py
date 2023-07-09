import asyncio
import itertools
import logging

from telegram import Bot

from yt_subs_bot.storage import Storage
from yt_subs_bot.youtube import YouTubeClient


class Notifier:
    def __init__(self, storage: Storage, youtube_client: YouTubeClient, bot: Bot):
        self.storage = storage
        self.youtube_client = youtube_client
        self.bot = bot

    async def run(self):
        logging.debug("Scheduled task started")
        chats = self.storage.get_active_chats()
        logging.debug("Found " + str(len(chats)) + " chats")
        for chat in chats:
            try:
                await self.check_and_notify(chat)
            except Exception as e:
                logging.error("Error while checking chat {}: {}".format(chat["_id"], e))

    async def check_and_notify(self, chat: dict):
        logging.debug("Checking chat " + str(chat["_id"]))
        new_videos = []
        for channel in chat["channels"]:
            channel_id = channel["id"]
            try:
                new_videos_in_channel = await self.get_new_videos_in_channel_for_chat(channel, chat)
                new_videos.extend(new_videos_in_channel)
                if new_videos:
                    self.storage.set_latest_video_sent(chat["_id"], channel_id, new_videos_in_channel[-1]["video_id"])
            except Exception as e:
                logging.error("Error while checking channel {} for chat {}: {}"
                              .format(channel_id, chat["_id"], e), e)

        new_videos = sorted(new_videos, key=lambda v: v["published_at"])
        for video in new_videos:
            await self.notify(chat, video)
            await asyncio.sleep(0.1)

    async def get_new_videos_in_channel_for_chat(self, channel, chat):
        channel_id = channel["id"]
        latest_video_sent = channel["latest_video_sent"]
        latest_videos = self.youtube_client.get_videos_by_channel_id(channel_id)
        latest_videos = list(itertools.takewhile(lambda v: v["video_id"] != latest_video_sent, latest_videos))
        latest_videos.sort(key=lambda v: v["published_at"])

        logging.debug("Found {} new videos for channel {} in chat {}"
                      .format(len(latest_videos), channel_id, chat["_id"]))
        return latest_videos

    async def notify(self, chat, video):
        link = f"https://www.youtube.com/watch?v={video['video_id']}"
        await self.bot.send_message(chat_id=chat["_id"], text=link)
