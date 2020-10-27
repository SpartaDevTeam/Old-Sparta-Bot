import json
import asyncio
import discord


async def update_presence(bot, prefix):
    while True:
        server_count = len(bot.guilds)
        activity = discord.Activity(
            type=discord.ActivityType.watching, name=f"{server_count} servers || s!help")
        await bot.change_presence(activity=activity)
        await asyncio.sleep(10)


async def create_mute_role(guild):
    perms = discord.Permissions(send_messages=False)
    mute_role = await guild.create_role(name="Muted", color=discord.Color.dark_grey(), permissions=perms)

    for channel in guild.channels:
        await channel.set_permissions(mute_role, send_messages=False)

    return mute_role
