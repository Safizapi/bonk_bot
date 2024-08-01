# bonk_bot
User-friendly async python framework for writing bots in bonk.io.
Supported python versions: 3.8+
## Features
- API is using async and await for handling several connections and requests at once
- Different bonk.io servers support
- Event-based (discord.py-like events)
## Installing
**Python 3.8 and higher required**

Go to your project's terminal and run the following command:
```
pip install bonk_bot
```
## Bot example

```py
import asyncio

from bonk_bot import bonk_guest_login, Game, Message

bot = bonk_guest_login("Safizapi")
bot.main_avatar = bot.avatars[1]


@bot.event
async def on_game_connect(game: Game):
    print(f"Connected game {game.room_name}")
    print(game.join_link)


@bot.event
async def on_error(error):
    print(error)


@bot.event
async def on_message(message: Message):
    if not message.author.is_bot and message.content == "!ping":
        await message.game.send_message("Pong!")


@bot.event
async def on_game_disconnect(game: Game):
    print(f"Disconnected from game {game.room_name}")


async def main():
    await bot.create_game(name="Cool room", max_players=4)

    await bot.run()


asyncio.run(main())
```
## Documentation
Coming soon
