import os
import subprocess
import asyncio
import json
import discord
import random
import datetime
from discord.ext import commands
from discord import Member

# Import Cogs
from cogs.misc import Miscellaneous
from cogs.serversettings import ServerSettings

from otherscipts.helpers import create_mute_role, update_presence
from otherscipts.data import Data

TOKEN = os.getenv('SPARTA_TOKEN')

PREFIX = "s!"
bot = commands.Bot(command_prefix=PREFIX,
                   description="I am Sparta Bot, a bot for the Official Sparta Gaming Discord server.",
                   help_command=None)

THEME_COLOR = discord.Colour.blue()
warn_count = {}

# Add Cogs
bot.add_cog(Miscellaneous(bot, THEME_COLOR))
bot.add_cog(ServerSettings(bot, THEME_COLOR))


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


# LABEL: Moderator Commands
@bot.command(name="warn")
@commands.has_guild_permissions(administrator=True)
async def warn(ctx, user: discord.User = None, *, reason=None):
    if user is None or reason is None:
        await ctx.send("Insufficient arguments.")
    else:
        print(f"Warning user {user.name} for {reason}...")

        if str(user) not in warn_count:
            warn_count[str(user)] = 1
        else:
            warn_count[str(user)] += 1

        embed = discord.Embed(
            title=f"{user.name} has been warned", color=THEME_COLOR)
        embed.add_field(name="Reason", value=reason)
        embed.add_field(name="This user has been warned",
                        value=f"{warn_count[str(user)]} time(s)")

        await ctx.send(content=None, embed=embed)


@bot.command(name="clearwarn")
@commands.has_guild_permissions(administrator=True)
async def clearwarn(ctx, user: discord.User = None):
    global warn_count
    if user is None:
        warn_count = {}
        await ctx.send("Clearing all warns.")
    else:
        warn_count[str(user)] = 0
        await ctx.send(f"Clearing warns for {user.mention}.")


@bot.command(name="warncount")
async def warncount(ctx, user: discord.User):
    if str(user) not in warn_count:
        warn_count[str(user)] = 0

    count = warn_count[str(user)]
    await ctx.send(f"{user.mention} has been warned {count} time(s)")


@bot.command(name="mute")
@commands.has_guild_permissions(kick_members=True)
async def mute(ctx, user: discord.Member = None, time: str = None):
    if user is None:
        await ctx.send("Insufficient arguments.")
    else:
        guild = ctx.guild
        mute_role = None

        for role in guild.roles:
            if role.name.lower() == "muted":
                mute_role = role
                break

        if mute_role in user.roles:
            await ctx.send("This user is already muted.")
        else:
            if not mute_role:
                await ctx.send("This server does not have a `Muted` Role. Creating one right now.")
                await ctx.send("This may take some time.")
                mute_role = await create_mute_role(guild)

            if time is None:
                await user.add_roles(mute_role)
                await ctx.send(f"User {user.mention} has been muted! They cannot speak.")
            else:
                time_unit = None
                parsed_time = None

                if "s" in time:
                    time_unit = "seconds"
                    parsed_time = time[0:(len(time) - 1)]
                elif "m" in time:
                    time_unit = "minutes"
                    parsed_time = time[0:(len(time) - 1)]
                elif "h" in time:
                    time_unit = "hours"
                    parsed_time = time[0:(len(time) - 1)]
                else:
                    time_unit = "minutes"  # default to minutes if user doesn't provide a time unit
                    parsed_time = time[0:len(time)]

                await user.add_roles(mute_role)
                await ctx.send(f"User {user.mention} has been muted for {parsed_time} {time_unit}! They cannot speak.")

                if time_unit == "seconds":
                    await asyncio.sleep(int(parsed_time))
                elif time_unit == "minutes":
                    await asyncio.sleep(int(parsed_time) * 60)
                elif time_unit == "hours":
                    await asyncio.sleep(int(parsed_time) * 3600)

                await user.remove_roles(mute_role)
                await ctx.send(f"User {user.mention} has been unmuted after {parsed_time} {time_unit}! They can speak now.")


@bot.command(name="unmute")
@commands.has_guild_permissions(kick_members=True)
async def unmute(ctx, user: discord.Member = None):
    if user is None:
        await ctx.send("Insufficient arguments.")
    else:
        guild = ctx.guild
        mute_role = None

        for role in guild.roles:
            if role.name.lower() == "muted":
                mute_role = role
                break

        if mute_role in user.roles:
            if not mute_role:
                mute_role = await create_mute_role(guild)

            await user.remove_roles(mute_role)
            await ctx.send(f"User {user.mention} has been unmuted! They can now speak.")

        else:
            await ctx.send("This user was never muted.")


@bot.command(name="ban")
@commands.has_guild_permissions(ban_members=True)
async def ban(ctx, user: discord.User = None, *, reason=None):
    if user is None:
        await ctx.send("Insufficient arguments.")
    else:
        await ctx.guild.ban(user, reason=reason)
        if reason:
            await ctx.send(f"User **{user}** has been banned for reason: **{reason}**.")
        else:
            await ctx.send(f"User **{user}** has been banned.")
        await user.send(f"You have been **banned** from **{ctx.guild}** server due to the following reason:\n**{reason}**")


@bot.command(name="tempban")
@commands.has_guild_permissions(ban_members=True)
async def tempban(ctx, user: discord.User = None, days: int = 1):
    if user is None:
        await ctx.send("Insufficient arguments.")
    else:
        await ctx.guild.ban(user)
        await ctx.send(f"User **{user}** has been temporarily banned for **{days} day(s)**")
        await user.send(f"You have been **temporarily banned** from **{ctx.guild}** server for **{days} day(s)**")
        await asyncio.sleep(days * 86400)  # convert days to seconds
        await ctx.guild.unban(user)
        await ctx.send(f"**{user}** has been unbanned after a {days} day Temp Ban.")


@bot.command(name="unban")
@commands.has_guild_permissions(ban_members=True)
async def unban(ctx, username: str = None, *, reason=None):
    if username is None:
        await ctx.send("Insufficient arguments.")
    else:
        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = username.split('#')

        for ban_entry in banned_users:
            user = ban_entry.user

            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)

        try:
            if reason:
                await ctx.send(f"User **{username}** has been unbanned for reason: **{reason}**.")
            else:
                await ctx.send(f"User **{username}** has been unbanned.")
            await user.send(f"You have been **unbanned** from **{ctx.guild}** server due to the following reason:\n**{reason}**")
        except NameError:
            await ctx.send(f"{username} is has not been banned in this server.")


@bot.command(name="kick")
@commands.has_guild_permissions(kick_members=True)
async def kick(ctx, user: discord.User = None, *, reason=None):
    if user is None:
        await ctx.send("Insufficient arguments.")
    else:
        await ctx.guild.kick(user, reason=reason)
        if reason:
            await ctx.send(f"User **{user}** has been kicked for reason: **{reason}**.")
        else:
            await ctx.send(f"User **{user}** has been kicked.")
        await user.send(f"You have been **kicked** from **{ctx.guild}** server due to the following reason:\n**{reason}**")


@bot.command(name="lockchannel")
@commands.has_guild_permissions(administrator=True)
async def lockchannel(ctx, channel: discord.TextChannel = None):
    if channel is None:
        channel = ctx.channel

    for role in ctx.guild.roles:
        if role.permissions.administrator:
            await channel.set_permissions(role, send_messages=True, read_messages=True)
        elif role.name == "@everyone":
            await channel.set_permissions(role, send_messages=False)

    await ctx.send(f"🔒The channel {channel.mention} has been locked")


@bot.command(name="unlockchannel")
@commands.has_guild_permissions(administrator=True)
async def unlockchannel(ctx, channel: discord.TextChannel = None):
    if channel is None:
        channel = ctx.channel

    await channel.set_permissions(ctx.guild.roles[0], send_messages=True)

    await ctx.send(f"🔓The channel {channel.mention} has been unlocked")


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
@bot.command(name="eval")
async def eval_code(ctx, *, code):
    is_owner = await bot.is_owner(ctx.author)
    if is_owner or ctx.author.id == 733532987794128897:  # for real sparta
        # Some formatting before executing code
        print(code)
        code = code.strip("```")
        code = code.strip("py")
        code = code.strip("python")
        print(code)

        code_file = open("run.py", "w")
        code_file.write(code)
        code_file.close()

        cmd = subprocess.run(["python3", "run.py"], capture_output=True)
        output = cmd.stdout.decode()  # bytes => str

        os.remove("run.py")

        if len(output) == 0:
            output = "```There was an error in your code...```"
        else:
            output = f"```{output}```"

        output_embed = discord.Embed(title="Code Output", color=THEME_COLOR)
        output_embed.add_field(name=f"Code run by {ctx.author}:", value=output)

        await ctx.send(embed=output_embed)
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
