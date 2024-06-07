import asyncio
from bonkBot.BonkBot import bonk_account_login
from bonkBot.Game import Game, Player

bot = bonk_account_login("Safizapi_", "I've just changed password")


@bot.on("game_connect")
async def on_connect(game: Game):
    print(f"Connected game {game.room_name}")


@bot.on("player_join")
async def on_player_join(game: Game, player: Player):
    await game.send_message(f"Hi, {player.username}")


@bot.on("game_disconnect")
async def on_game_disconnect(game: Game):
    print(f"Disconnected from game {game.room_name}")


async def main():
    game = bot.create_game()

    await game.connect()
    await game.send_message("New room!")

    await bot.run()


asyncio.run(main())
