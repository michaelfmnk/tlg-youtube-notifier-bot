from pymongo.mongo_client import MongoClient


class Storage:
    def __init__(self, connection_string: str):
        self.client = MongoClient(connection_string)
        self.db = self.client['yt_subs_bot']

    def get_chat(self, chat_id: int):
        return self.db.chats.find_one({"_id": chat_id})

    def get_chat_or_new(self, chat_id: int, creator_id: int):
        chat = self.get_chat(chat_id)
        if chat:
            return chat
        return self.create_chat(chat_id, creator_id)

    def create_chat(self, chat_id: int, creator_id: int):
        chat = {
            "_id": chat_id,
            "creator_id": creator_id,
            "channels": []
        }
        self.db.chats.insert_one(chat)
        return chat

    def add_channel(self, chat_id: int, channel_id: str):
        channel_obj = {
            "id": channel_id,
            "latest_video_sent": None
        }
        self.db.chats.update_one({"_id": chat_id}, {"$push": {"channels": channel_obj}})

    def get_all_chats(self):
        return list(self.db.chats.find())

    def set_latest_video_sent(self, chat_id: str, channel_id: str, video_id: str):
        self.db.chats.update_one({"_id": chat_id, "channels.id": channel_id},
                                 {"$set": {"channels.$.latest_video_sent": video_id}})

    def delete_chat(self, chat_id):
        self.db.chats.delete_one({"_id": chat_id})

    def set_paused(self, chat_id, paused):
        self.db.chats.update_one({"_id": chat_id}, {"$set": {"paused": paused}})

    def get_active_chats(self):
        return list(self.db.chats.find({"paused": {"$ne": True}}))
