import os
import subprocess
import random
import discord
import asyncio
import inspect
from discord.ext import commands

# Import Cogs
from cogs.misc import Miscellaneous
from cogs.serversettings import ServerSettings
from cogs.mod import Moderator

from otherscipts.helpers import update_presence
from otherscipts.data import Data

TOKEN = os.getenv('SPARTA_TOKEN')

PREFIX = "s!"
bot = commands.Bot(command_prefix=PREFIX,
                   description="I am Sparta Bot, a bot for the Official Sparta Gaming Discord server.",
                   help_command=None)

THEME_COLOR = discord.Colour.blue()

# Add Cogs
bot.add_cog(Miscellaneous(bot, THEME_COLOR))
bot.add_cog(ServerSettings(bot, THEME_COLOR))
bot.add_cog(Moderator(bot, THEME_COLOR))


@bot.event
async def on_ready():
    bot.loop.create_task(Data.auto_update_data())
    bot.loop.create_task(update_presence(bot, PREFIX))
    print("Bot is ready...")


@bot.event
async def on_member_join(member):
    guild: discord.Guild = member.guild
    channels = guild.channels

    if str(guild.id) not in Data.server_data:
        Data.server_data[str(guild.id)] = Data.create_new_data()
    data = Data.server_data[str(guild.id)]

    print(f"{member} has joined {guild} server...")

    join_role = guild.get_role(data["join_role"])
    if join_role is not None:
        await member.add_roles(join_role)

    # Welcome Message
    if data["welcome_msg"] is None:
        server_wlcm_msg = f"Welcome, {member.mention}, to the Official **{guild.name}** Server"
    else:
        server_wlcm_msg = data["welcome_msg"]
        server_wlcm_msg = server_wlcm_msg.replace(
            "[mention]", f"{member.mention}")

    for channel in channels:
        if str(channel).find("welcome") != -1:
            await channel.send(server_wlcm_msg)
            break


@bot.event
async def on_member_remove(member):
    guild = member.guild
    channels = guild.channels
    print(f"{member} has left the server...")

    # Leave Message
    for channel in channels:
        if str(channel).find("bye") != -1 or str(channel).find("leave") != -1:
            msg = f"Goodbye, **{str(member)}**, thank you for staying at **{guild.name}** Server\n"
            await channel.send(msg)
            break


# LABEL: AutoMod Commands
@bot.command(name="activateautomod")
@commands.has_guild_permissions(administrator=True)
async def activateautomod(ctx):
    if str(ctx.guild.id) not in Data.server_data:
        Data.server_data[str(ctx.guild.id)] = Data.create_new_data()

    Data.server_data[str(ctx.guild.id)]["active"] = True
    await ctx.send("Automod is now active in your server...")


@bot.command(name="stopautomod")
@commands.has_guild_permissions(administrator=True)
async def stopautomod(ctx):
    if str(ctx.guild.id) not in Data.server_data:
        Data.server_data[str(ctx.guild.id)] = Data.create_new_data()

    Data.server_data[str(ctx.guild.id)]["active"] = False
    await ctx.send("Automod is now inactive in your server...")


@bot.command(name="whitelistuser")
@commands.has_guild_permissions(administrator=True)
async def whitelistuser(ctx, user: discord.User = None):
    if user is None:
        ctx.send("Insufficient Arguments")
    else:
        if str(ctx.guild.id) not in Data.server_data:
            Data.server_data[str(ctx.guild.id)] = Data.create_new_data()

        Data.server_data[str(ctx.guild.id)]["users"].append(str(user.id))
        await ctx.send(f"Added {user.mention} to AutoMod user whitelist.")


@bot.command(name="whitelisturl")
@commands.has_guild_permissions(administrator=True)
async def whitelisturl(ctx, url: str = None):
    if url is None:
        ctx.send("Insufficient Arguments")
    else:
        if str(ctx.guild.id) not in Data.server_data:
            Data.server_data[str(ctx.guild.id)] = Data.create_new_data()

        Data.server_data[str(ctx.guild.id)]["urls"].append(url)
        await ctx.send(f"Added `{url}` to AutoMod URL whitelist.")


@bot.command(name="whitelistchannel")
@commands.has_guild_permissions(administrator=True)
async def whitelistchannel(ctx, channel: discord.TextChannel = None):
    if channel is None:
        ctx.send("Insufficient Arguments")
    else:
        if str(ctx.guild.id) not in Data.server_data:
            Data.server_data[str(ctx.guild.id)] = Data.create_new_data()

        Data.server_data[str(ctx.guild.id)]["channels"].append(
            str(channel.id))
        await ctx.send(f"Added {channel.mention} to AutoMod Channel whitelist.")


@bot.command(name="automodstatus")
async def automodstatus(ctx):
    status = Data.server_data[str(ctx.guild.id)]["active"]
    await ctx.send(f"AutoMod Active: **{status}**")


# LABEL: Programming Commands
@bot.command(name='eval', pass_context=True)
async def eval_(ctx, *, command):
    if ctx.author.id == 733532987794128897 or ctx.author.id == 400857098121904149:
        res = eval(command)
        if inspect.isawaitable(res):
            await res
        else:
            res
        comp = await ctx.send("Completed")
        await asyncio.sleep(3)
        await comp.delete()
    else:
        await ctx.send("You are not authorized to run this command.")


# LABEL: Fun Commands
@bot.command(name="coinflip")
async def coinflip(ctx):
    choices = ["Heads", "Tails"]
    rancoin = random.choice(choices)
    await ctx.send(rancoin)


@bot.command(name="roll")
async def roll(ctx):
    choices = [1, 2, 3, 4, 5, 6]
    ranroll = random.choice(choices)
    await ctx.send(ranroll)

@bot.command(name="choose", aliases=['ch'])
async def choose(ctx, *, choices: str):
    choicelist = choices.split(",")
    await ctx.send("I choose " + random.choice(choicelist))

@bot.command(name="avatar")
async def avatar(ctx, user: discord.Member = None):
    if user is None:
        user = ctx.author

    aembed = discord.Embed(
        color=THEME_COLOR,
        title=f"{user}"
    )

    aembed.set_image(url=f"{user.avatar_url}")
    await ctx.send(embed=aembed)


# LABEL: Debugging Commands
@bot.command(name="data")
async def data(ctx):
    is_owner = await bot.is_owner(ctx.author)
    if is_owner or ctx.author.id == 733532987794128897:  # for real sparta
        data_file = discord.File("data.json")
        await ctx.send(file=data_file)


@bot.event
async def on_message(message: discord.Message):
    author: discord.Member = message.author
    channel: discord.TextChannel = message.channel
    guild: discord.Guild = message.guild
    # print(str(author), ": ", message.content)

    await bot.process_commands(message)

    if str(guild.id) not in Data.server_data:
        Data.server_data[str(guild.id)] = Data.create_new_data()

    data = Data.server_data[str(guild.id)]

    if data["pay_respects"] and message.content.strip().lower() == "f":
        await channel.send(f"**{author.display_name}** has paid their respects...")

    if data["active"] and str(author.id) not in data["users"]:
        if not str(channel.id) in data["channels"]:
            perms = author.permissions_in(channel)
            if not perms.administrator:
                if "http://" in message.content or "https://" in message.content:
                    if len(data["urls"]) > 0:
                        for url in data["urls"]:
                            if not url in message.content:
                                await channel.purge(limit=1)
                                await channel.send(f"{author.mention}, you are not allowed to send links in this channel.")
                    else:
                        await channel.purge(limit=1)
                        await channel.send(f"{author.mention}, you are not allowed to send links in this channel.")

                elif len(message.attachments) > 0:
                    await channel.purge(limit=1)
                    await channel.send(f"{author.mention}, you are not allowed to send attachments in this channel.")


bot.run(TOKEN)
