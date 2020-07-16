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

    for channel in channels:
        # Channel Links
        if str(channel).find("rules") != -1:
            rules_server = guild.get_channel(int(channel.id))
            print("rules channel found")
        elif str(channel).find("self-roles") != -1:
            self_roles_channel = guild.get_channel(int(channel.id))
            print("self-roles channel found")

        # Welcome message
        if "welcome" in str(channel):
            print(f"{member} has joined the server...")

            msg = f"Welcome, {member.mention}, to the Official {guild.name} Server\n"
            if rules_server != None:
                msg += f"Please check the rules at {rules_server.mention}\n"
            if self_roles_server != None:
                msg += f"Get your self-role at {self_roles_channel.mention}.\n"

            await channel.send(msg)


@bot.command(name="hello")
async def hello(ctx):
    await ctx.send("Hi, I am Sparta Bot!")


bot.run(token)
