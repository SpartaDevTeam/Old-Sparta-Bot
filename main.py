import discord
from discord.ext import commands

token = open("token.txt", "r").read()
prefix = "sb!"
bot = commands.Bot(command_prefix=prefix,
                   description="Description yet to be added...")


@bot.event
async def on_ready():
    print("Bot is ready...")


@bot.command(name="hello")
async def hello(ctx):
    await ctx.send("Hi, I am Sparta Bot!")


bot.run(token)
