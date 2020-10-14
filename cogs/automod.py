import asyncio
import discord
from discord.ext import commands

from otherscipts.data import Data


class AutoMod(commands.Cog):
    def __init__(self, bot, theme_color):
        self.bot = bot
        self.theme_color = theme_color

    @commands.command(name="activateautomod", aliases=['enablemod'])
    @commands.has_guild_permissions(administrator=True)
    async def activateautomod(self, ctx):
        if str(ctx.guild.id) not in Data.server_data:
            Data.server_data[str(ctx.guild.id)] = Data.create_new_data()

        Data.server_data[str(ctx.guild.id)]["active"] = True
        await ctx.send("Automod is now active in your server...")

    @commands.command(name="stopautomod", aliases=['stopmod'])
    @commands.has_guild_permissions(administrator=True)
    async def stopautomod(self, ctx):
        if str(ctx.guild.id) not in Data.server_data:
            Data.server_data[str(ctx.guild.id)] = Data.create_new_data()

        Data.server_data[str(ctx.guild.id)]["active"] = False
        await ctx.send("Automod is now inactive in your server...")

    @commands.command(name="whitelistuser", aliases=['wuser'])
    @commands.has_guild_permissions(administrator=True)
    async def whitelistuser(self, ctx, user: discord.Member = None):
        if user is None:
            ctx.send("Insufficient Arguments")
        else:
            if str(ctx.guild.id) not in Data.server_data:
                Data.server_data[str(ctx.guild.id)] = Data.create_new_data()

            Data.server_data[str(ctx.guild.id)]["users"].append(str(user.id))
            await ctx.send(f"Added {user.mention} to AutoMod user whitelist.")

    @commands.command(name="whitelisturl", aliases=['wurl'])
    @commands.has_guild_permissions(administrator=True)
    async def whitelisturl(self, ctx, url: str = None):
        if url is None:
            ctx.send("Insufficient Arguments")
        else:
            if str(ctx.guild.id) not in Data.server_data:
                Data.server_data[str(ctx.guild.id)] = Data.create_new_data()

            Data.server_data[str(ctx.guild.id)]["urls"].append(url)
            await ctx.send(f"Added `{url}` to AutoMod URL whitelist.")

    @commands.command(name="whitelistchannel", aliases=['wchannel'])
    @commands.has_guild_permissions(administrator=True)
    async def whitelistchannel(self, ctx, channel: discord.TextChannel = None):
        if channel is None:
            ctx.send("Insufficient Arguments")
        else:
            if str(ctx.guild.id) not in Data.server_data:
                Data.server_data[str(ctx.guild.id)] = Data.create_new_data()

            Data.server_data[str(ctx.guild.id)]["channels"].append(
                str(channel.id))
            await ctx.send(f"Added {channel.mention} to AutoMod Channel whitelist.")

    @commands.command(name="automodstatus", aliases=['modstatus'])
    async def automodstatus(self, ctx):
        status = Data.server_data[str(ctx.guild.id)]["active"]
        await ctx.send(f"AutoMod Active: **{status}**")
