import asyncio
import discord
from discord.ext import commands

with open("token.txt", "r") as file:
    token = file.read()
prefix = "s!"
bot = commands.Bot(command_prefix=prefix,
                   description="I am Sparta Bot, a bot for the Official Sparta Gaming Discord server.",
                   help_command=None)


async def update_presence():
    while True:
        server_count = len(bot.guilds)
        activity = discord.Activity(
            type=discord.ActivityType.watching, name=f"{server_count} servers || {prefix}help")
        await bot.change_presence(activity=activity)
        await asyncio.sleep(10)


warn_count = {}
muted_users = []
automod_active = False
automod_user_whitelist = []
automod_url_whitelist = ["https://discord.com", "https://discord.gg"]
theme_color = discord.Colour.purple()


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
            if rules_server != None:
                msg += f"Please check the rules at {rules_server.mention}\n"
            if self_roles_server != None:
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


@bot.group(name="help", invoke_without_command=True)
async def _help(ctx):
    await ctx.send(f"A DM for command help has been sent to {ctx.author.mention}.")

    embed = discord.Embed(title="Help", color=theme_color)

    embed.add_field(name="misc", value="Miscellaneous Commands")
    embed.add_field(name="mod", value="Moderator Commands")
    embed.add_field(name="automod", value="Auto Moderator Settings")

    await ctx.author.send("Here is the command help:", embed=embed)


@_help.command(name="misc")
async def misc_help(ctx):
    await ctx.send(f"A DM for Miscellaneous command help has been sent to {ctx.author.mention}.")
    embed = discord.Embed(title="Misc. Help", color=theme_color)

    embed.add_field(name=f"`{prefix}help <category>`",
                    value="Displays command help")
    embed.add_field(name=f"`{prefix}hello`", value="Say hello to the bot")
    embed.add_field(name=f"`{prefix}info`",
                    value="Displays the bot's information")
    embed.add_field(
        name=f"`{prefix}invite`", value="Get the link to invite Sparta Bot to your server")

    await ctx.author.send("Here is Miscellaneous command help:", embed=embed)


@_help.command(name="mod")
async def mod_help(ctx):
    await ctx.send(f"A DM for Moderator command help has been sent to {ctx.author.mention}.")
    embed = discord.Embed(title="Moderator Help", color=theme_color)

    embed.add_field(name=f"`{prefix}warn <user> <reason>`",
                    value="Warn a user for doing something")
    embed.add_field(name=f"`{prefix}clearwarn <user>`",
                    value="Clear a user's warns")
    embed.add_field(name=f"`{prefix}warncount <user>`",
                    value="Displays how many times a user has been warned")
    embed.add_field(name=f"`{prefix}mute <user>`", value="Mutes a user")
    embed.add_field(name=f"`{prefix}unmute <user>`", value="Unmutes a user")
    embed.add_field(name=f"`{prefix}ban <user> <reason>`",
                    value="Bans a user from the server")
    embed.add_field(name=f"`{prefix}kick <user> <reason>`",
                    value="Kicks a user from the server")

    await ctx.author.send("Here is Moderator command help:", embed=embed)


@_help.command(name="automod")
async def automod_help(ctx):
    await ctx.send(f"A DM for Auto Moderator settings help has been sent to {ctx.author.mention}.")
    embed = discord.Embed(title="Auto Moderator Help", color=theme_color)

    embed.add_field(name=f"`{prefix}activateautomod`",
                    value="Turns on Automod in your server")

    embed.add_field(name=f"`{prefix}stopautomod`",
    				value="Turns off Automod in your server")

    embed.add_field(name=f"`{prefix}whitelistuser <user>`",
                    value="Make a user immune to Auto Mod (Administrators are already immune)")

    embed.add_field(name=f"`{prefix}whitelisturl <url>`",
                    value="Allow a specific url to bypass the Auto Mod")

    await ctx.author.send("Here is Auto Moderator settings help:", embed=embed)


@bot.command(name="hello")
async def hello(ctx):
    await ctx.send("Hi, I am Sparta Bot!")


@bot.command(name="info")
async def info(ctx):
    embed = discord.Embed(title="Bot Information", color=theme_color)
    ping = round(bot.latency * 1000)
    guild_count = len(bot.guilds)
    member_count = 0

    for guild in bot.guilds:
        member_count += len(guild.members)

    embed.add_field(name="Ping", value=f"{ping}ms")
    embed.add_field(name="Servers", value=guild_count)
    embed.add_field(name="Users", value=member_count)

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
    if user == None or reason == None:
        await ctx.send("Insufficient arguments.")
    else:
        print(f"Warning user {user.name} for {reason}...")

        if str(user) not in warn_count:
            warn_count[str(user)] = 1
        else:
            warn_count[str(user)] += 1

        embed = discord.Embed(title=f"{user.name} has been warned")
        embed.add_field(name="Reason", value=reason)
        embed.add_field(name="This user has been warned",
                        value=f"{warn_count[str(user)]} time(s)")

        await ctx.send(content=None, embed=embed)


@bot.command(name="clearwarn")
@commands.has_guild_permissions(administrator=True)
async def clearwarn(ctx, user: discord.User = None):
    global warn_count
    if user == None:
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
async def mute(ctx, user: discord.User):
    if str(user) in muted_users:
        await ctx.send("This user has already been muted.")
    else:
        muted_users.append(str(user))
        await ctx.send(f"User {user.mention} has been muted! They cannot speak anymore.")


@bot.command(name="unmute")
@commands.has_guild_permissions(administrator=True)
async def unmute(ctx, user: discord.User):
    if str(user) in muted_users:
        muted_users.remove(str(user))
        await ctx.send(f"User {user.mention} has been unmuted! They can now speak.")
    else:
        await ctx.send("This user was never muted.")


@bot.command(name="ban")
@commands.has_guild_permissions(ban_members=True)
async def ban(ctx, user: discord.User = None, *, reason=None):
    if user == None or reason == None:
        await ctx.send("Insufficient arguments.")
    else:
        await ctx.guild.ban(user, reason=reason)
        await ctx.send(f"User {user.mention} has been banned for reason: **{reason}**.")


@bot.command(name="kick")
@commands.has_guild_permissions(kick_members=True)
async def kick(ctx, user: discord.User = None, *, reason=None):
    if user == None or reason == None:
        await ctx.send("Insufficient arguments.")
    else:
        await ctx.guild.kick(user, reason=reason)
        await ctx.send(f"User {user.mention} has been kick for reason: **{reason}**.")


@bot.command(name="activateautomod")
@commands.has_guild_permissions(administrator=True)
async def activateautomod(ctx):
    global automod_active
    automod_active = True
    await ctx.send("Automod is now active in your server...")


@bot.command(name="stopautomod")
@commands.has_guild_permissions(administrator=True)
async def stopautomod(ctx):
    global automod_active
    automod_active - False
    await ctx.send("Automod is now inactive in your server...")


@bot.command(name="whitelistuser")
@commands.has_guild_permissions(administrator=True)
async def whitelistuser(ctx, user: discord.User = None):
    if user == None:
        ctx.send(f"Insufficient Arguments")
    else:
        automod_user_whitelist.append(user)
        await ctx.send(f"Added {user.mention} to AutoMod user whitelist.")


@bot.command(name="whitelisturl")
@commands.has_guild_permissions(administrator=True)
async def whitelisturl(ctx, url: str):
    if url == None:
        ctx.send(f"Insufficient Arguments")
    else:
        automod_url_whitelist.append(url)
        await ctx.send(f"Added `{url}` to AutoMod URL whitelist.")


@bot.event
async def on_message(message):
    author = message.author
    channel = message.channel
    # print(str(author), ": ", message.content)

    await bot.process_commands(message)

    perms = author.guild_permissions

    if str(author) in muted_users:
        await channel.purge(limit=1)

    elif author not in automod_user_whitelist and not perms.administrator and automod_active:
        if "http://" in message.content or "https://" in message.content:
            for url in automod_url_whitelist:
                if not url in message.content:
                    await channel.purge(limit=1)
                    await channel.send(f"{author.mention}, you are not allowed to send links in this channel.")

        elif len(message.attachments) > 0:
            await channel.purge(limit=1)


bot.run(token)
