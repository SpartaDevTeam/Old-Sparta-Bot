import os
import subprocess
import random
import discord
import asyncio
import inspect
import traceback
import sys
from discord.ext import commands

# Import Cogs
from cogs.misc import Miscellaneous
from cogs.serversettings import ServerSettings
from cogs.mod import Moderator
from cogs.automod import AutoMod

from otherscipts.helpers import update_presence
from otherscipts.data import Data

TOKEN = os.getenv('SPARTA_TOKEN')

intents = discord.Intents.default()
intents.members = True


def get_prefix(client, message):
    if str(message.guild.id) not in Data.server_data:
        Data.server_data[str(message.guild.id)] = Data.create_new_data()

    data = Data.server_data[str(message.guild.id)]
    return data["prefix"]


PREFIX = get_prefix
bot = commands.Bot(
    command_prefix=PREFIX,
    description="I am Sparta Bot, a bot for the Official Sparta Gaming Discord server.",
    intents=intents,
    help_command=None,
    case_insensitive=True
)

THEME_COLOR = discord.Colour.blue()

# Add Cogs
bot.add_cog(Miscellaneous(bot, THEME_COLOR))
bot.add_cog(ServerSettings(bot, THEME_COLOR))
bot.add_cog(Moderator(bot, THEME_COLOR))
bot.add_cog(AutoMod(bot, THEME_COLOR))

previous_msg_sender_id = None


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

    # Welcome Chanel
    wel_channel = None

    if data["welcome_channel"] is None:
        for channel in channels:
        if str(channel).find("welcome") != -1:
            wel_channel = channel
            break
    else:
        wel_channel = guild.get_channel(int(data["welcome_channel"]))

    try:
        await wel_channel.send(server_wlcm_msg)
    except AttributeError:
        print("DEBUG: No welcome channel has been set or found.")


@bot.event
async def on_member_remove(member):
    guild = member.guild
    channels = guild.channels

    if str(guild.id) not in Data.server_data:
        Data.server_data[str(guild.id)] = Data.create_new_data()
    data = Data.server_data[str(guild.id)]

    print(f"{member} has left the {guild.name}...")

    # Leave Message
    if data["leave_msg"] is None:
        server_leave_msg = f"Goodbye, **{str(member)}**, thank you for staying at **{guild.name}** Server"
    else:
        server_leave_msg = data["leave_msg"]
        server_leave_msg = server_leave_msg.replace(
            "[member]", f"{member}")

    for channel in channels:
        if str(channel).find("bye") != -1 or str(channel).find("leave") != -1:
            await channel.send(server_leave_msg)
            break

    # Welcome Chanel
    lv_channel = None

    if data["leave_channel"] is None:
        for channel in channels:
        if str(channel).find("bye") != -1 or str(channel).find("leave") != -1:
            lv_channel = channel
            break
    else:
        lv_channel = guild.get_channel(int(data["leave_channel"]))

    try:
        await lv_channel.send(server_leave_msg)
    except AttributeError:
        print("DEBUG: No leave channel has been set or found.")


@bot.event
async def on_command_error(ctx, error):
    try:
        error = error.original
    except Exception:
        pass
    if type(error) is discord.ext.commands.errors.CommandNotFound:
        return
    elif type(error) is discord.ext.commands.errors.BadArgument:
        pass
    elif type(error) is discord.ext.commands.errors.MissingRequiredArgument:
        pass
    elif type(error) is discord.ext.commands.errors.NoPrivateMessage:
        pass
    elif type(error) is discord.ext.commands.errors.MissingPermissions:
        pass
    elif type(error) is discord.ext.commands.errors.NotOwner:
        pass
    elif type(error) is discord.ext.commands.errors.CommandOnCooldown:
        pass
    elif type(error) is discord.ext.commands.errors.ChannelNotFound:
        pass
    elif type(error) is discord.ext.commands.errors.BadUnionArgument:
        pass
    elif type(error) is discord.ext.commands.errors.BotMissingPermissions:
        pass
    elif type(error) is discord.errors.Forbidden:
        error = "I don't have permission to do that!"
    else:
        print(f"Error {type(error)}: {error}")
        traceback.print_exception(
            type(error), error, error.__traceback__, file=sys.stderr
        )

        embed = discord.Embed(
            title='Error!',
            description='An unexpected error ocurred.\
                Please report this to the dev.',
        )
        embed.add_field(
            name='Error Message:',
            value=f"{type(error)}:\n{error}",
            inline=False
        )
    await ctx.send(f"{error}")


# LABEL: Programming Commands
@bot.command(name='eval', pass_context=True)
async def eval_(ctx, *, code):
    if ctx.author.id == 733532987794128897 or ctx.author.id == 400857098121904149:
        formatted_code = code.strip("```").strip("py").strip("python")
        res = eval(formatted_code)

        if inspect.isawaitable(res):
            await res
        else:
            res

        embed = discord.Embed(
            title="Code Evaluation Complete!", color=THEME_COLOR)
        embed.set_footer(
            text=f"Requested by {ctx.author}",
            icon_url=ctx.author.avatar_url
        )
        embed.add_field(name="Code:", value=f"```py\n{formatted_code}```")

        await ctx.send(embed=embed)
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
    await ctx.send("I choose " + random.choice(choicelist).strip())


@bot.command(name="avatar", aliases=['av'])
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
    global previous_msg_sender_id

    author: discord.Member = message.author
    channel: discord.TextChannel = message.channel
    guild: discord.Guild = message.guild
    # print(str(author), ": ", message.content)

    await bot.process_commands(message)

    if str(guild.id) not in Data.server_data:
        Data.server_data[str(guild.id)] = Data.create_new_data()

    data = Data.server_data[str(guild.id)]

    if len(message.mentions) != 0 and message.mentions[0] == bot.user:
        pre = data["prefix"]
        await channel.send(f"The prefix in this server is `{pre}`")

    for afk_user_entry in data["afks"]:
        afk_user_id = int(afk_user_entry["user"])
        afk_reason = afk_user_entry["reason"]
        afk_user = guild.get_member(afk_user_id)

        if afk_user.id == author.id and afk_user_id == previous_msg_sender_id:
            Data.server_data[str(guild.id)]["afks"].remove(afk_user_entry)
            await channel.send(f"**{afk_user}** is no longer AFK.")

        elif afk_user in message.mentions:
            await channel.send(f"**{afk_user}** is currently AFK because **{afk_reason}**.")

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
                                msg1 = await channel.send(f"{author.mention}, you are not allowed to send links in this channel.")
                                await asyncio.sleep(2)
                                await msg1.delete()
                    else:
                        await channel.purge(limit=1)
                        msg2 = await channel.send(f"{author.mention}, you are not allowed to send links in this channel.")
                        await asyncio.sleep(3)
                        await msg2.delete()

                elif len(message.attachments) > 0:
                    await channel.purge(limit=1)
                    msg3 = await channel.send(f"{author.mention}, you are not allowed to send attachments in this channel.")
                    await asyncio.sleep(3)
                    await msg3.delete()

    previous_msg_sender_id = author.id


bot.run(TOKEN)
