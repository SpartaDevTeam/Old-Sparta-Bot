import discord
from discord.ext import commands

token = open("token.txt", "r").read()
prefix = "s!"
bot = commands.Bot(command_prefix=prefix,
                   description="Description yet to be added...")


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
    latency_ms = bot.latency * 1000
    await ctx.send(f"Ping(ms): {latency_ms}")


bot.run(token)
