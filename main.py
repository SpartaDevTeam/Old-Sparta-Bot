import asyncio
import discord
from discord.ext import commands

with open("token.txt", "r") as file:
    token = file.read()
PREFIX = "s!"
bot = commands.Bot(command_prefix=PREFIX,
                   description="I am Sparta Bot, a bot for the Official Sparta Gaming Discord server.",
                   help_command=None)
theme_color = discord.Colour.purple()


async def update_presence():
    while True:
        server_count = len(bot.guilds)
        activity = discord.Activity(
            type=discord.ActivityType.watching, name=f"{server_count} servers || {PREFIX}help")
        await bot.change_presence(activity=activity)
        await asyncio.sleep(10)


async def create_mute_role(guild):
    perms = discord.Permissions(send_messages=False)
    mute_role = await guild.create_role(name="Muted", colour=discord.Color.dark_gray(), permissions=perms)

    for channel in guild.channels:
        await channel.set_permissions(mute_role, send_messages=False)

    return mute_role


misc_embed = discord.Embed(title="Misc. Help", color=theme_color)
misc_embed.add_field(
    name=f"`{PREFIX}help <category>`", value="Displays command help")
misc_embed.add_field(name=f"`{PREFIX}hello`", value="Say hello to the bot")
misc_embed.add_field(name=f"`{PREFIX}info`",
                     value="Displays the bot's information")
misc_embed.add_field(name=f"`{PREFIX}clear <count>`", value="Deletes messages")
misc_embed.add_field(
    name=f"`{PREFIX}invite`", value="Get the link to invite Sparta Bot to your server")


mod_embed = discord.Embed(title="Moderator Help", color=theme_color)
mod_embed.add_field(name=f"`{PREFIX}warn <user> <reason>`",
                    value="Warn a user for doing something")
mod_embed.add_field(name=f"`{PREFIX}clearwarn <user>`",
                    value="Clear a user's warns")
mod_embed.add_field(name=f"`{PREFIX}warncount <user>`",
                    value="Displays how many times a user has been warned")
mod_embed.add_field(name=f"`{PREFIX}mute <user>`", value="Mutes a user")
mod_embed.add_field(name=f"`{PREFIX}unmute <user>`", value="Unmutes a user")
mod_embed.add_field(
    name=f"`{PREFIX}tempmute <user> <time in seconds>`", value="Temporarily mutes a user")
mod_embed.add_field(name=f"`{PREFIX}ban <user> <reason>`",
                    value="Bans a user from the server")
mod_embed.add_field(name=f"`{PREFIX}kick <user> <reason>`",
                    value="Kicks a user from the server")


auto_embed = discord.Embed(title="Auto Moderator Help", color=theme_color)
auto_embed.add_field(name=f"`{PREFIX}activateautomod`",
                     value="Turns on Automod in your server")
auto_embed.add_field(name=f"`{PREFIX}stopautomod`",
                     value="Turns off Automod in your server")
auto_embed.add_field(name=f"`{PREFIX}whitelistuser <user>`",
                     value="Make a user immune to Auto Mod (Administrators are already immune)")
auto_embed.add_field(name=f"`{PREFIX}whitelisturl <url>`",
                     value="Allow a specific url to bypass the Auto Mod")


all_help_embeds = [misc_embed, mod_embed, auto_embed]
warn_count = {}
AUTOMOD_ACTIVE = False
automod_user_whitelist = []
automod_url_whitelist = ["https://discord.com", "https://discord.gg"]
CURRENT_HELP_MSG = None
CURRENT_HELP_USER = None
HELP_INDEX = 0
help_control_emojis = ["⬅️", "➡️"]


@bot.event
async def on_ready():
    bot.loop.create_task(update_presence())
    print("Bot is ready...")


@bot.event
async def on_member_join(member):
    guild = member.guild
    channels = guild.channels
    rules_server = None
    self_roles_server = None
    print(f"{member} has joined the server...")

    # Channel Links
    for channel in channels:
        if str(channel).find("rules") != -1:
            rules_server = channel
            print("rules channel found")
        if str(channel).find("self-roles") != -1:
            self_roles_channel = channel
            print("self-roles channel found")

    # Welcome Message
    for channel in channels:
        if str(channel).find("welcome") != -1:
            msg = f"Welcome, {member.mention}, to the Official **{guild.name}** Server\n"
            if rules_server:
                msg += f"Please check the rules at {rules_server.mention}\n"
            if self_roles_server:
                msg += f"Get your self-role at {self_roles_channel.mention}.\n"

            await channel.send(msg)
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


@bot.event
async def on_reaction_add(reaction: discord.Reaction, user: discord.User):
    global HELP_INDEX

    if reaction.message.id == CURRENT_HELP_MSG and user.id != 731763013417435247:
        if user.id == CURRENT_HELP_USER:
            channel: discord.TextChannel = reaction.message.channel

            if reaction.emoji == help_control_emojis[0]:
                HELP_INDEX -= 1

            if reaction.emoji == help_control_emojis[1]:
                HELP_INDEX += 1

            if HELP_INDEX < 0:
                HELP_INDEX = len(all_help_embeds) - 1
            elif HELP_INDEX >= len(all_help_embeds):
                HELP_INDEX = 0

            message: discord.Message = await channel.fetch_message(CURRENT_HELP_MSG)
            await message.edit(embed=all_help_embeds[HELP_INDEX])
            await message.remove_reaction(reaction.emoji, user)


@bot.group(name="help")
async def _help(ctx):
    msg: discord.Message = await ctx.send("Here is the command help:", embed=all_help_embeds[HELP_INDEX])

    for emoji in help_control_emojis:
        await msg.add_reaction(emoji)

    global CURRENT_HELP_MSG, CURRENT_HELP_USER
    CURRENT_HELP_MSG = msg.id
    CURRENT_HELP_USER = ctx.author.id


@bot.command(name="hello")
async def hello(ctx):
    await ctx.send("Hi, I am Sparta Bot!")


@bot.command(name="info")
async def info(ctx):
    embed = discord.Embed(title="Bot Information", color=theme_color)
    ping = round(bot.latency * 1000)
    guild_count = len(bot.guilds)
    members = []
    unique_member_count = 0

    for guild in bot.guilds:
        for member in guild.members:
            if not member in members:
                unique_member_count += 1
            members.append(member)

    embed.add_field(name="Ping", value=f"{ping}ms")
    embed.add_field(name="Servers", value=guild_count)
    embed.add_field(name="Users", value=len(members))
    embed.add_field(name="Unique Users", value=unique_member_count)

    await ctx.send(content=None, embed=embed)


@bot.command(name="invite")
async def invite(ctx):
    invite_url = "https://discord.com/oauth2/authorize?client_id=731763013417435247&permissions=8&scope=bot"
    embed = discord.Embed(
        title="Click here to invite Sparta Bot!", url=invite_url)
    await ctx.send(content=None, embed=embed)


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

        embed = discord.Embed(title=f"{user.name} has been warned", color=theme_color)
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
@commands.has_guild_permissions(administrator=True)
async def mute(ctx, user: discord.Member = None):
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
                mute_role = await create_mute_role(guild)

            await user.add_roles(mute_role)
            await ctx.send(f"User {user.mention} has been muted! They cannot speak.")


@bot.command(name="unmute")
@commands.has_guild_permissions(administrator=True)
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


@bot.command(name="tempmute")
@commands.has_guild_permissions(administrator=True)
async def tempmute(ctx, user: discord.Member = None, time: int = None):
    if user is None or time is None:
        await ctx.send("Insufficient arguments.")
    else:
        guild = ctx.guild
        mute_role = None

        for role in guild.roles:
            if role.name.lower() == "muted":
                mute_role = role
                break

        if not mute_role:
            mute_role = await create_mute_role(guild)

        await user.add_roles(mute_role)
        await ctx.send(f"User {user.mention} has been muted for {time} seconds!")
        await asyncio.sleep(time)
        await user.remove_roles(mute_role)
        await ctx.send(f"User {user.mention} has been unmuted after {time} seconds of TempMute! They can now speak.")


@bot.command(name="ban")
@commands.has_guild_permissions(ban_members=True)
async def ban(ctx, user: discord.User = None, *, reason=None):
    if user is None or reason is None:
        await ctx.send("Insufficient arguments.")
    else:
        await ctx.guild.ban(user, reason=reason)
        await ctx.send(f"User {user.mention} has been banned for reason: **{reason}**.")


@bot.command(name="kick")
@commands.has_guild_permissions(kick_members=True)
async def kick(ctx, user: discord.User = None, *, reason=None):
    if user is None or reason is None:
        await ctx.send("Insufficient arguments.")
    else:
        await ctx.guild.kick(user, reason=reason)
        await ctx.send(f"User {user.mention} has been kick for reason: **{reason}**.")


@bot.command(name="clear")
@commands.has_guild_permissions(manage_messages=True)
async def clear(ctx, count: int = None):
    if count is None:
        await ctx.send("Insufficient arguments.")
    else:
        await ctx.channel.purge(limit=count+1)
        await ctx.send(f"Cleared the last {count} message(s)!")
        await asyncio.sleep(3)
        await ctx.channel.purge(limit=1)


@bot.command(name="activateautomod")
@commands.has_guild_permissions(administrator=True)
async def activateautomod(ctx):
    global AUTOMOD_ACTIVE
    AUTOMOD_ACTIVE = True
    await ctx.send("Automod is now active in your server...")


@bot.command(name="stopautomod")
@commands.has_guild_permissions(administrator=True)
async def stopautomod(ctx):
    global AUTOMOD_ACTIVE
    AUTOMOD_ACTIVE = False
    await ctx.send("Automod is now inactive in your server...")


@bot.command(name="whitelistuser")
@commands.has_guild_permissions(administrator=True)
async def whitelistuser(ctx, user: discord.User = None):
    if user is None:
        ctx.send("Insufficient Arguments")
    else:
        automod_user_whitelist.append(user)
        await ctx.send(f"Added {user.mention} to AutoMod user whitelist.")


@bot.command(name="whitelisturl")
@commands.has_guild_permissions(administrator=True)
async def whitelisturl(ctx, url: str):
    if url:
        ctx.send("Insufficient Arguments")
    else:
        automod_url_whitelist.append(url)
        await ctx.send(f"Added `{url}` to AutoMod URL whitelist.")


@bot.event
async def on_message(message: discord.Message):
    author: discord.Member = message.author
    channel = message.channel
    # print(str(author), ": ", message.content)

    await bot.process_commands(message)

    if AUTOMOD_ACTIVE and author not in automod_user_whitelist:
        perms = author.guild_permissions
        if not perms.administrator:
            if "http://" in message.content or "https://" in message.content:
                for url in automod_url_whitelist:
                    if not url in message.content:
                        await channel.purge(limit=1)
                        await channel.send(f"{author.mention}, you are not allowed to send links in this channel.")

            elif len(message.attachments) > 0:
                await channel.purge(limit=1)


bot.run(token)
