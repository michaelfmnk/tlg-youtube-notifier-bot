import requests
import logging


class YouTubeClient:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def get_channel_id(self, channel_handle: str) -> str | None:
        base_url = "https://www.googleapis.com/youtube/v3/channels"
        params = {
            "part": "id",
            "forUsername": channel_handle,
            "key": self.api_key
        }
        result_channel_id: str | None = None
        try:
            response = requests.get(base_url, params=params)
            data = response.json()
            if "items" in data and len(data["items"]) > 0:
                channel_id = data["items"][0]["id"]
                result_channel_id = channel_id
        except IOError:
            pass

        return result_channel_id

    def get_videos_by_channel_id(self, channel_id: str, limit: int = 5):
        base_url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "part": "snippet",
            "channelId": channel_id,
            "maxResults": limit,
            "order": "date",
            "type": "video",
            "key": self.api_key
        }
        videos = []
        try:
            response = requests.get(base_url, params=params)
            data = response.json()
            if "items" in data and len(data["items"]) > 0:
                for item in data["items"]:
                    video = {
                        "title": item["snippet"]["title"],
                        "video_id": item["id"]["videoId"],
                        "date": item["snippet"]["publishedAt"],
                    }
                    videos.append(video)
        except IOError:
            logging.error("Error getting videos for channel id: %s", channel_id)
        return videos

    def get_channel_id_by_link(self, link: str) -> str | None:
        channel_name = link.split("@")[1]
        return self.get_channel_id(channel_name)
