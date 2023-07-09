from unittest import TestCase

from yt_subs_bot.youtube import YouTubeClient


class TestYouTubeClient(TestCase):
    def test_get_videos_by_channel_id(self):
        yt = YouTubeClient("")
        channel_id = yt.get_channel_id("pewdiepie")
        videos = yt.get_videos_by_channel_id(channel_id)

        videos.sort(key=lambda v: v["published_at"], reverse=True)

        print(videos)
