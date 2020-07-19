import asyncio
import discord
from discord.ext import commands

with open("token.txt", "r") as file:
    token = file.read()
prefix = "s!"
bot = commands.Bot(command_prefix=prefix,
                   description="I am Sparta Bot, a bot for the Official Sparta Gaming Discord server.",
                   help_command=None)

mod_roles = open("modlist.txt", "a+")


def get_mod_list():
    mod_roles.seek(0)
    return [int(role_id.replace("\n", "")) for role_id in mod_roles.readlines()]


async def update_presence():
    while True:
        server_count = len(bot.guilds)
        activity = discord.Activity(
            type=discord.ActivityType.watching, name=f"{server_count} servers || {prefix}help")
        await bot.change_presence(activity=activity)
        await asyncio.sleep(10)


warn_count = {}
muted_users = []
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

    # Channel Links
    for channel in channels:
        if "rules" in str(channel):
            rules_server = channel
            print("rules channel found")
        if "self-roles" in str(channel):
            self_roles_channel = channel
            print("self-roles channel found")

    # Welcome Message
    for channel in channels:
        if "welcome" in str(channel):
            print(f"{member} has joined the server...")

            msg = f"Welcome, {member.mention}, to the Official **{guild.name}** Server\n"
            if rules_server != None:
                msg += f"Please check the rules at {rules_server.mention}\n"
            if self_roles_server != None:
                msg += f"Get your self-role at {self_roles_channel.mention}.\n"

            await channel.send(msg)


@bot.group(name="help", invoke_without_command=True)
async def _help(ctx):
    await ctx.send(f"A DM for command help has been sent to {ctx.author.mention}.")

    embed = discord.Embed(title="Help", color=theme_color)

    embed.add_field(name="misc", value="Miscellaneous Commands")
    embed.add_field(name="mod", value="Moderator Commands")

    await ctx.author.send("Here is the command help:", embed=embed)


@_help.command(name="misc")
async def misc_help(ctx):
    embed = discord.Embed(title="Misc. Help", color=theme_color)

    embed.add_field(name=f"{prefix}help", value="Displays command help")
    embed.add_field(name=f"{prefix}hello", value="Say hello to the bot")
    embed.add_field(name=f"{prefix}ping",
                    value="Get the bot's latency in milliseconds")

    await ctx.author.send("Here is Miscellaneous command help:", embed=embed)


@_help.command(name="mod")
async def mod_help(ctx):
    embed = discord.Embed(title="Moderator Help", color=theme_color)

    embed.add_field(name=f"{prefix}addmodrole",
                    value="Give a role the permission to use Moderation commands")
    embed.add_field(name=f"{prefix}warn",
                    value="Warn a user for doing something")
    embed.add_field(name=f"{prefix}warncount",
                    value="Displays how many times a user has been warned")
    embed.add_field(name=f"{prefix}mute", value="Mutes a user")
    embed.add_field(name=f"{prefix}unmute", value="Unmutes a user")
    embed.add_field(name=f"{prefix}ban", value="Bans a user from the server")

    await ctx.author.send("Here is Moderator command help:", embed=embed)


@bot.command(name="hello")
async def hello(ctx):
    await ctx.send("Hi, I am Sparta Bot!")


@bot.command(name="ping")
async def ping(ctx):
    latency_ms = round(bot.latency * 1000)
    await ctx.send(f"Ping: {latency_ms}ms")


@bot.command(name="addmodrole")
async def addmodrole(ctx):
    try:
        role = ctx.message.role_mentions[0]
        if ctx.author.guild_permissions.administrator:
            mod_roles.writelines(str(role.id) + "\n")
            mod_roles.flush()

            await ctx.send(f"Role {role.mention} has been added to Moderator Roles list.")
        else:
            await ctx.send("You are not allowed to use this command!")
    except IndexError:
        await ctx.send("Role not provided")


@bot.command(name="warn")
@commands.has_any_role(*get_mod_list())
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


@bot.command(name="warncount")
async def warncount(ctx, user: discord.User):
    if str(user) not in warn_count:
        warn_count[str(user)] = 0

    count = warn_count[str(user)]
    await ctx.send(f"{user.mention} has been warned {count} time(s)")


@bot.command(name="mute")
@commands.has_any_role(*get_mod_list())
async def mute(ctx, user: discord.User):
    if str(user) in muted_users:
        await ctx.send("This user has already been muted.")
    else:
        muted_users.append(str(user))
        await ctx.send(f"User {user.mention} has been muted! They cannot speak anymore.")


@bot.command(name="unmute")
@commands.has_any_role(*get_mod_list())
async def unmute(ctx, user: discord.User):
    if str(user) in muted_users:
        muted_users.remove(str(user))
        await ctx.send(f"User {user.mention} has been unmuted! They can now speak.")
    else:
        await ctx.send("This user was never muted.")


@bot.command(name="ban")
@commands.has_any_role(*get_mod_list())
async def ban(ctx, user: discord.User = None, *, reason=None):
    if user == None or reason == None:
        await ctx.send("Insufficient arguments.")
    else:
        await ctx.guild.ban(user, reason=reason)
        await ctx.send(f"User {user.mention} has been banned for reason: **{reason}**.")


# DON'T INCLUDE IN HELP
@bot.command(name="getmodlist")
async def getmodlist(ctx):
    file = discord.File(open("modlist.txt", "r"))
    await ctx.send(content=None, file=file)
    file.fp.close()


@bot.event
async def on_message(message):
    author = message.author
    channel = message.channel

    if str(author) in muted_users:
        await channel.purge(limit=1)

    await bot.process_commands(message)


bot.run(token)
