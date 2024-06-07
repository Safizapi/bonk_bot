import asyncio
from bonkBot.BonkBot import bonk_login
from bonkBot.GameTypes import Teams, Modes


async def main():
    bot = bonk_login("go_harder_daddy", "123")

    # room = [room for room in bot.get_rooms() if room.name == "OG_NEW_PLAYER"][0]
    # game = room.join()

    game = bot.create_game()
    for i in game.players:
        print(i.__dict__)
    print(game.__dict__)
    await game.connect()
    await game.set_mode(Modes.Grapple())
    await game.set_rounds(9)
    await game.toggle_team_lock(True)
    await game.toggle_teams(True)
    await game.toggle_bot_ready(True)
    player = game.players[0]
    await player.balance(-100)
    await player.move_to_team(Teams.Red())
    await player.give_host()
    for i in game.players:
        print(i.__dict__)
    print(game.__dict__)
    await game.leave()
    await bot.run()


asyncio.run(main())
