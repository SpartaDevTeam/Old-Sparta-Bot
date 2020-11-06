import asyncio
import discord
from discord import utils
from discord.ext import commands
from typing import Union

from otherscipts.helpers import create_mute_role


class Moderator(commands.Cog):
    def __init__(self, bot, theme_color):
        self.bot = bot
        self.theme_color = theme_color
        self.warn_count = {}

    @commands.command(name="warn")
    @commands.has_guild_permissions(kick_members=True)
    async def warn(self, ctx, user: discord.Member = None, *, reason=None):
        if user is None or reason is None:
            await ctx.send("Insufficient arguments.")
        elif ctx.author.top_role.position <= user.top_role.position and ctx.guild.owner.id != ctx.author.id:
            await ctx.send("You cannot warn this user because their role is higher than or equal to yours.")
        else:
            print(f"Warning user {user.name} for {reason}...")

            if str(user) not in self.warn_count:
                self.warn_count[str(user)] = 1
            else:
                self.warn_count[str(user)] += 1

            embed = discord.Embed(
                title=f"{user.name} has been warned", color=self.theme_color)
            embed.add_field(name="Reason", value=reason)
            embed.add_field(name="This user has been warned",
                            value=f"{self.warn_count[str(user)]} time(s)")

            await ctx.send(content=None, embed=embed)

    @commands.command(name="clearwarn", aliases=['cw', 'removewarns', 'rw'])
    @commands.has_guild_permissions(kick_members=True)
    async def clearwarn(self, ctx, user: discord.Member = None):
        if user is None:
            self.warn_count = {}
            await ctx.send("Clearing all warns.")
        elif ctx.author.top_role.position <= user.top_role.position and ctx.guild.owner.id != ctx.author.id:
            await ctx.send("You cannot clear this user's warnings because their role is higher than or equal to yours.")
        else:
            self.warn_count[str(user)] = 0
            await ctx.send(f"Clearing warns for {user.mention}.")

    @commands.command(name="warncount")
    async def warncount(self, ctx, user: discord.Member):
        if str(user) not in self.warn_count:
            self.warn_count[str(user)] = 0

        count = self.warn_count[str(user)]
        await ctx.send(f"{user.mention} has been warned {count} time(s)")

    @commands.command(name="mute")
    @commands.has_guild_permissions(kick_members=True)
    async def mute(self, ctx, user: discord.Member = None, time: str = None):
        if user is None:
            await ctx.send("Insufficient arguments.")
        elif ctx.author.top_role.position <= user.top_role.position and ctx.guild.owner.id != ctx.author.id:
            await ctx.send("You cannot mute this user because their role is higher than or equal to yours.")
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

    @commands.command(name="unmute")
    @commands.has_guild_permissions(kick_members=True)
    async def unmute(self, ctx, user: discord.Member = None):
        if user is None:
            await ctx.send("Insufficient arguments.")
        elif ctx.author.top_role.position <= user.top_role.position and ctx.guild.owner.id != ctx.author.id:
            await ctx.send("You cannot unmute this user because their role is higher than or equal to yours.")
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

    @commands.command(name="ban")
    @commands.has_guild_permissions(ban_members=True)
    async def ban(self, ctx, user: Union[discord.Member, int], *, reason=None):
        if not isinstance(user, int):
            if ctx.author.top_role.position <= user.top_role.position \
                    and ctx.guild.owner_id != ctx.author.id:
                await ctx.send(
                    "You cannot ban this user because their role "
                    "is higher than or equal to yours."
                )
                return
        if isinstance(user, int):
            user_str = f"<@{user}>"
            user = discord.Object(id=user)
        else:
            user_str = user
        try:
            await user.send(
                f"You have been **banned** from **{ctx.guild}** server "
                f"due to the following reason:\n**{reason}**"
            )
        except Exception:
            pass
        await ctx.guild.ban(user, reason=reason)
        if reason:
            await ctx.send(
                f"User **{user_str}** has been banned for reason: "
                f"**{reason}**."
            )
        else:
            await ctx.send(f"User **{user_str}** has been banned.")

    @commands.command(name="tempban")
    @commands.has_guild_permissions(ban_members=True)
    async def tempban(self, ctx, user: Union[discord.Member, int], days: int = 1):
        if not isinstance(user, int):
            if ctx.author.top_role.position <= user.top_role.position \
                    and ctx.guild.owner.id != ctx.author.id:
                await ctx.send(
                    "You cannot temporarily ban this user because their "
                    "role is higher than or equal to yours."
                )
                return
        if isinstance(user, int):
            user_str = f"<@{user}>"
            user = discord.Object(id=user)
        else:
            user_str = user
        try:
            await user.send(
                f"You have been **temporarily banned** from "
                f"**{ctx.guild}** server for **{days} day(s)**"
            )
        except Exception:
            pass
        await ctx.guild.ban(user)
        await ctx.send(
            f"User **{user_str}** has been temporarily "
            f"banned for **{days} day(s)**"
        )
        # NOTE(circuit): using asyncio.sleep for unban is a VERY BAD IDEA
        # NOTE: I would highly recomment removing temban until
        # NOTE: you can use the database to unban, so unbanning
        # NOTE: still works after the bot restarts
        await asyncio.sleep(days * 86400)  # convert days to seconds
        await ctx.guild.unban(user)
        await ctx.send(
            f"**{user_str}** has been unbanned after a {days} day Temp Ban."
        )

    @commands.command(name="unban")
    @commands.has_guild_permissions(ban_members=True)
    @commands.guild_only()
    async def unban(
        self, ctx, user: Union[discord.User, int, str],
        *, reason=None
    ):
        if isinstance(user, int):
            user_str = f"<@{user}>"
            user = discord.Object(id=user)
        else:
            user_str = user
        
        if isinstance(user, str):
            guild_bans = await ctx.guild.bans()
            try:
                name, tag = user.split('#')
            except:
                await ctx.send(
                    "Please format the username like this: "
                    "Username#0000"
                )
                return
            banned_user = utils.get(
                guild_bans, user__name=name,
                user__discriminator=tag
            )
            if banned_user is None:
                await ctx.send("I could not find that user in the bans.")
                return
            await ctx.guild.unban(banned_user.user)
            try:
                await banned_user.send(
                    f"You have been unbanned with reason: {reason}"
                )
            except Exception:
                pass

        else:
            await ctx.guild.unban(user)
            try:
                await user.send(
                    f"You have been unbanned with reason: {reason}"
                )
            except Exception:
                pass

        await ctx.send(f"Unbanned **{user_str}**")

#    @commands.command(name="unban")
#    @commands.has_guild_permissions(ban_members=True)
#    async def unban(self, ctx, username: str = None, *, reason=None):
#        if username is None:
#            await ctx.send("Insufficient arguments.")
#
#        else:
#            banned_users = await ctx.guild.bans()
#            member_name, member_discriminator = username.split('#')
#
#            for ban_entry in banned_users:
#                user = ban_entry.user
#
#                if (user.name, user.discriminator) == (member_name, member_discriminator):
#                    await ctx.guild.unban(user)
#
#            try:
#                if reason:
#                    await ctx.send(f"User **{username}** has been unbanned for reason: **{reason}**.")
#                else:
#                    await ctx.send(f"User **{username}** has been unbanned.")
#                await user.send(f"You have been **unbanned** from **{ctx.guild}** server due to the following reason:\n**{reason}**")
#            except NameError:
#                await ctx.send(f"{username} is has not been banned in this server.")

    @commands.command(name="kick")
    @commands.has_guild_permissions(kick_members=True)
    async def kick(self, ctx, user: discord.Member = None, *, reason=None):
        if user is None:
            await ctx.send("Insufficient arguments.")
        elif ctx.author.top_role.position <= user.top_role.position and ctx.guild.owner.id != ctx.author.id:
            await ctx.send("You cannot kick this user because their role is higher than or equal to yours.")
        else:
            await ctx.guild.kick(user, reason=reason)
            if reason:
                await ctx.send(f"User **{user}** has been kicked for reason: **{reason}**.")
            else:
                await ctx.send(f"User **{user}** has been kicked.")
            await user.send(f"You have been **kicked** from **{ctx.guild}** server due to the following reason:\n**{reason}**")

    @commands.command(name="masskick")
    async def masskick(self, ctx):
        def check(m):
            return m.author == ctx.author

        await ctx.send("How many members do you want to kick?")
        msg = await self.bot.wait_for("message", check=check)

        for i in range(int(msg.content)):
            await ctx.send("Whom do you want to kick?")
            msg2 = await self.bot.wait_for("message", check=check)
            user = msg2.mentions[0]
            if ctx.author.top_role.position <= user.top_role.position and ctx.guild.owner.id != ctx.author.id:
                await ctx.send("You cannot kick this user because their role is higher than or equal to yours.")
            else:
                await user.kick()
                await ctx.send(f"User **{user}** has been kicked.")
                await user.send(f"You have been **kicked** from **{ctx.guild}** server")

    @commands.command(name="lockchannel", aliases=['lock'])
    @commands.has_guild_permissions(manage_guild=True)
    async def lockchannel(self, ctx, channel: discord.TextChannel = None):
        if channel is None:
            channel = ctx.channel

        for role in ctx.guild.roles:
            if role.permissions.administrator:
                await channel.set_permissions(role, send_messages=True, read_messages=True)
            elif role.name == "@everyone":
                await channel.set_permissions(role, send_messages=False)

        await ctx.send(f"🔒The channel {channel.mention} has been locked")

    @commands.command(name="unlockchannel", aliases=['unlock'])
    @commands.has_guild_permissions(manage_guild=True)
    async def unlockchannel(self, ctx, channel: discord.TextChannel = None):
        if channel is None:
            channel = ctx.channel

        await channel.set_permissions(ctx.guild.roles[0], send_messages=True)

        await ctx.send(f"🔓The channel {channel.mention} has been unlocked")

    @commands.command(name="slowmode", aliases=['sm'])
    @commands.has_guild_permissions(manage_guild=True)
    async def setdelay(self, ctx, seconds: int):
        await ctx.channel.edit(slowmode_delay=seconds)
        await ctx.send(f"Set the slowmode in this channel to **{seconds}** seconds!")
