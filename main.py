import os
import subprocess
import discord
import asyncio
import traceback
import sys
import ast

from discord.ext import commands

# Import Cogs
from cogs.misc import Miscellaneous
from cogs.serversettings import ServerSettings
from cogs.mod import Moderator
from cogs.automod import AutoMod
from cogs.google import Google

# Minigame/Fun Cogs
from cogs.fun import Fun
#from cogs.hangman import Hangman
#from cogs.rps import RockPaperScissors

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
bot.add_cog(Fun(bot, THEME_COLOR))
bot.add_cog(Google(bot, THEME_COLOR))
#bot.add_cog(Hangman(bot, THEME_COLOR))
#bot.add_cog(RockPaperScissors(bot, THEME_COLOR))

previous_msg_sender_id = None


@bot.event
async def on_ready():
    bot.loop.create_task(Data.auto_update_data())
    bot.loop.create_task(update_presence(bot, PREFIX))
    print("Bot is ready...")

@bot.event
async def on_guild_join(guild):
    log_channel = bot.get_channel(773580297954394162)
    await log_channel.send(f"Joined - {guild.name}\nServer ID - {guild.id}\nOwner - {guild.owner}")
@bot.event
async def on_guild_remove(guild):
    log_channel = bot.get_channel(773580297954394162)
    await log_channel.send(f"Left - {guild.name}\nServer ID - {guild.id}\nOwner - {guild.owner}")

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

    # Welcome Channel
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

#Remove welcome channel
@bot.command(name="remove_welcome", aliases=['rwel', 'remwel'])
@commands.has_guild_permissions(manage_guild=True)
async def remove_welcome(ctx, *, channel):
    if str(ctx.guild.id) not in Data.server_data:
        Data.server_data[str(ctx.guild.id)] = Data.create_new_data()
    
    Data.server_data[str(ctx.guild.id)]["welcome_channel"] = channel
    await ctx.send("This server's welcome channel has been removed")

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
        server_leave_msg = server_leave_msg.replace("[member]", f"{member}")

    # Leave Channel
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


#Remove leave
@bot.command(name="remove_leave", aliases=['rleave', 'remleave'])
@commands.has_guild_permissions(manage_guild=True)
async def remove_welcome( ctx, *, channel):
    if str(ctx.guild.id) not in Data.server_data:
        Data.server_data[str(ctx.guild.id)] = Data.create_new_data()
    
    Data.server_data[str(ctx.guild.id)]["leave_channel"] = channel
    await ctx.send("This server's leave channel has been Removed")

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
def insert_returns(body):
    # insert return stmt if the last expression is a expression statement
    if isinstance(body[-1], ast.Expr):
        body[-1] = ast.Return(body[-1].value)
        ast.fix_missing_locations(body[-1])

    # for if statements, we insert returns into the body and the orelse
    if isinstance(body[-1], ast.If):
        insert_returns(body[-1].body)
        insert_returns(body[-1].orelse)

    # for with blocks, again we insert returns into the body
    if isinstance(body[-1], ast.With):
        insert_returns(body[-1].body)


@bot.command(name='eval')
async def eval_fn(ctx, *, cmd):
    """Evaluates input.
    Input is interpreted as newline seperated statements.
    If the last statement is an expression, that is the return value.
    Usable globals:
      - `bot`: the bot instance
      - `discord`: the discord module
      - `commands`: the discord.ext.commands module
      - `ctx`: the invokation context
      - `__import__`: the builtin `__import__` function
    Such that `>eval 1 + 1` gives `2` as the result.
    The following invokation will cause the bot to send the text '9'
    to the channel of invokation and return '3' as the result of evaluating
    >eval ```
    a = 1 + 2
    b = a * 2
    await ctx.send(a + b)
    a
    ```
    """
    if ctx.message.author.id not in [400857098121904149, 733532987794128897]:
        await ctx.send("You are not authorized to run this command")
        return

    fn_name = "_eval_expr"

    cmd = cmd.strip("` ")

    # add a layer of indentation
    cmd = "\n".join(f"    {i}" for i in cmd.splitlines())

    # wrap in async def body
    body = f"async def {fn_name}():\n{cmd}"

    parsed = ast.parse(body)
    body = parsed.body[0].body

    insert_returns(body)

    env = {
        'bot': ctx.bot,
        'discord': discord,
        'commands': commands,
        'ctx': ctx,
        '__import__': __import__
    }
    exec(compile(parsed, filename="<ast>", mode="exec"), env)

    result = (await eval(f"{fn_name}()", env))
    await ctx.send(result)


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

    if message.author.bot:
        return

    author: discord.Member = message.author
    channel: discord.TextChannel = message.channel
    guild: discord.Guild = message.guild
    # print(str(author), ": ", message.content)

    await bot.process_commands(message)

    if str(guild.id) not in Data.server_data:
        Data.server_data[str(guild.id)] = Data.create_new_data()

    data = Data.server_data[str(guild.id)]

    if message.content.replace('!', '') == bot.user.mention:
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
