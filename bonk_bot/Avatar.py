class Avatar:
    def __init__(self, bot, json_data: dict):
        self.bot = bot
        self.json_data: dict = json_data

    def set_as_bot_avatar(self):
        self.bot.main_avatar = Avatar(self.bot, self.json_data)
