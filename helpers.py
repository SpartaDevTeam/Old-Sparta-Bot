import json
import asyncio
import discord


async def update_data(data):
    while True:
        with open("data.json", "r+") as data_file:
            json.dump(data, data_file)
        await asyncio.sleep(30)


async def update_presence(bot, prefix):
    while True:
        server_count = len(bot.guilds)
        activity = discord.Activity(
            type=discord.ActivityType.watching, name=f"{server_count} servers || {prefix}help")
        await bot.change_presence(activity=activity)
        await asyncio.sleep(10)


async def create_mute_role(guild):
    perms = discord.Permissions(send_messages=False)
    mute_role = await guild.create_role(name="Muted", color=discord.Color.dark_grey(), permissions=perms)

    for channel in guild.channels:
        await channel.set_permissions(mute_role, send_messages=False)

    return mute_role


def create_new_data():
    whitelist_entry = {
        "active": False,
        "users": [],
        "urls": [],
        "channels": [],
        "welcome_msg": None,
    }
    return whitelist_entry
