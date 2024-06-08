import asyncio
from bonkBot.BonkBot import bonk_account_login
from bonkBot.Game import Game, Player, Message

bot = bonk_account_login("test_account_2", "2")


@bot.on("game_connect")
async def on_connect(game: Game):
    print(f"Connected game {game.room_name}")


@bot.on("player_join")
async def on_player_join(game: Game, player: Player):
    await game.send_message(f"Hi, {player.username}")


@bot.on("message")
async def on_message(game: Game, message: Message):
    print(f"[{game.room_name}] {message.author.username}: {message.content}")


@bot.on("bot_kick")
async def on_bot_ban(game: Game):
    print(f"Bot was kicked from game {game.room_name}")


@bot.on("game_disconnect")
async def on_game_disconnect(game: Game):
    print(f"Disconnected from game {game.room_name}")


async def main():
    room = [x for x in bot.get_rooms() if x.name == "wdb"][0]

    game = await room.join()
    game2 = await bot.create_game()

    await bot.run()


asyncio.run(main())
