import discord
from discord.ext import commands

token = open("token.txt", "r").read()
prefix = "s!"
bot = commands.Bot(command_prefix=prefix,
                   description="Description yet to be added...")

warn_count = {}

@bot.event
async def on_ready():
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
        if "self-role" in str(channel):
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


@bot.command(name="hello")
async def hello(ctx):
    await ctx.send("Hi, I am Sparta Bot!")


@bot.command(name="ping")
async def ping(ctx):
    latency_ms = round(bot.latency * 1000)
    await ctx.send(f"Ping: {latency_ms}ms")


@bot.command(name="addmodrole")
async def addmodrole(ctx):
    role = ctx.message.role_mentions[0]
    if ctx.author.guild_permissions.administrator:
        mod_roles = open("modlist.txt", "a")
        mod_roles.writelines(str(role.id) + "\n")
        mod_roles.close()
        await ctx.send(f"Role {role.mention} has been added to Moderator Roles list.")
    else:
        await ctx.send("You are not allowed to use this command!")


@bot.command(name="warn")
async def warn(ctx, user: discord.User, *, reason):
    print(f"Warning user {user.name} for {reason}...")
    mod_roles = open("modlist.txt", "r")
    for role_id in mod_roles.readlines():
        role_id = role_id.replace("\n", "")
        if ctx.guild.get_role(int(role_id)) in ctx.author.roles:
            if str(user) not in warn_count:
                warn_count[str(user)] = 1
            else:
                warn_count[str(user)] += 1
            embed = discord.Embed(title=f"{user.name} has been warned")
            embed.add_field(name="Reason", value=reason)
            embed.add_field(name="This user has been warned",
                            value=f"{warn_count[str(user)]} time(s)")

            await ctx.send(content=None, embed=embed)
            break
    mod_roles.close()


bot.run(token)
