import asyncio
import discord
from discord.ext import commands
import datetime

from otherscipts.data import Data


class Miscellaneous(commands.Cog):
    def __init__(self, bot, theme_color):
        self.bot = bot
        self.theme_color = theme_color

        self.help_index = 0
        self.current_help_msg = None
        self.current_help_user = None
        self.help_control_emojis = ["⬅️", "➡️"]

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.Member):
        if reaction.message.id == self.current_help_msg and user.id != 731763013417435247:
            if user.id == self.current_help_user:
                channel: discord.TextChannel = reaction.message.channel

                if reaction.emoji == self.help_control_emojis[0]:
                    self.help_index -= 1

                if reaction.emoji == self.help_control_emojis[1]:
                    self.help_index += 1

                if self.help_index < 0:
                    self.help_index = len(self.all_help_embeds) - 1
                elif self.help_index >= len(self.all_help_embeds):
                    self.help_index = 0

                message: discord.Message = await channel.fetch_message(self.current_help_msg)
                await message.edit(embed=self.all_help_embeds[self.help_index])
                await message.remove_reaction(reaction.emoji, user)

    @commands.command(name="help")
    async def _help(self, ctx):
        PREFIX = Data.server_data[str(ctx.guild.id)]["prefix"]

        misc_embed = discord.Embed(title="Misc. Help", color=self.theme_color)
        misc_embed.add_field(
            name=f"`{PREFIX}help`", value="Displays command help")
        misc_embed.add_field(
            name=f"`{PREFIX}hello`", value="Say hello to the bot")
        misc_embed.add_field(name=f"`{PREFIX}info`",
                             value="Displays the bot's information")
        misc_embed.add_field(
            name=f"`{PREFIX}clear <count>`", value="Deletes messages")
        misc_embed.add_field(name=f"`{PREFIX}nuke`",
                             value="Deletes all messages in a channel")
        misc_embed.add_field(name=f"`{PREFIX}invite`",
                             value="Get the link to invite Sparta Bot to your server")
        misc_embed.add_field(name=f"`{PREFIX}github`",
                             value="Get the link to the GitHub Repository")
        misc_embed.add_field(name=f"`{PREFIX}support`",
                             value="Get an invite to the Sparta Bot Support Server")
        misc_embed.add_field(name=f"`{PREFIX}vote`",
                             value="Get an links to Top.gg page and DBL page.")
        misc_embed.add_field(name=f"`{PREFIX}reminder <time> <reminder>`",
                             value="It will remind you via dms. Use s,m,h,d for timings.")
        misc_embed.add_field(name=f"`{PREFIX}afk <reason>`",
                             value="Lets others know that you are AFK when someone mentions you.")

        server_settings_embed = discord.Embed(
            title="Server Settings Commands Help", color=self.theme_color)
        server_settings_embed.add_field(
            name=f"`{PREFIX}welcomemessage <message>`", value="Change the default Welcome Message. Use `[mention]` to mention the user, and mention any channel to show it in the message")
        server_settings_embed.add_field(
            name=f"`{PREFIX}leavemessage <message>`", value="Change the default Leave Message. Use `[member]` to write the user's name, and mention any channel to show it in the message")
        server_settings_embed.add_field(
            name=f"`{PREFIX}welcomechannel <channel>`", value="Change the default channel to show Welcome Message.")
        server_settings_embed.add_field(
            name=f"`{PREFIX}leavechannel <channel>`", value="Change the default channel to show Leave Message.")
        server_settings_embed.add_field(
            name=f'`{PREFIX}remove_welcome null`',value='Removes welcome')
        server_settings_embed.add_field(
            name=f'`{PREFIX}remove_leave null`',value='Removes leave')
        server_settings_embed.add_field(
            name=f"`{PREFIX}joinrole <role>`", value="Gives this role to all new members who join the server")
        server_settings_embed.add_field(
            name=f"`{PREFIX}serverinfo`", value="Displays server information")
        server_settings_embed.add_field(
            name=f"`{PREFIX}userinfo <user>`", value="Displays user information")
        server_settings_embed.add_field(
            name=f"`{PREFIX}enablerespects`", value="Enables Respects (press f)")
        server_settings_embed.add_field(
            name=f"`{PREFIX}disablerespects`", value="Disables Respects")
        server_settings_embed.add_field(
            name=f"`{PREFIX}prefix <prefix>`", value="Sets the prefix in the current server")

        mod_embed = discord.Embed(title="Moderator Help", color=self.theme_color)

        mod_embed.add_field(name=f"`{PREFIX}warn <user> <reason>`",
                            value="Warn a user for doing something")
        mod_embed.add_field(name=f"`{PREFIX}clearwarn <user>`",
                            value="Clear a user's warns")
        mod_embed.add_field(name=f"`{PREFIX}warncount <user>`",
                            value="Displays how many times a user has been warned")
        mod_embed.add_field(name=f"`{PREFIX}mute <user> <time>`",
                            value="Mutes a user. You can optionally provide a time as well. Ex: 5s, 4m, 2h")
        mod_embed.add_field(name=f"`{PREFIX}unmute <user>`",
                            value="Unmutes a user")
        mod_embed.add_field(name=f"`{PREFIX}ban <user> <reason>`",
                            value="Bans a user from the server")
        mod_embed.add_field(name=f"`{PREFIX}unban <username with #number> <reason>`",
                            value="Unbans a user from the server")
        mod_embed.add_field(name=f"`{PREFIX}kick <user> <reason>`",
                            value="Kicks a user from the server")
        mod_embed.add_field(name=f"`{PREFIX}masskick`",
                            value="Kick multiple users from your server")
        mod_embed.add_field(name=f"`{PREFIX}lockchannel <channel>`",
                            value="Locks a channel so only Administrators can use it")
        mod_embed.add_field(name=f"`{PREFIX}unlockchannel <channel>`",
                            value="Unlocks a channel so every server member can use it")
        mod_embed.add_field(name=f"`{PREFIX}slowmode <seconds>`",
                            value="Adds slowmode for a channel, alias is sm")

        auto_embed = discord.Embed(
            title="Auto Moderator Help", color=self.theme_color)
        auto_embed.add_field(name=f"`{PREFIX}activateautomod`",
                             value="Turns on Automod in your server")
        auto_embed.add_field(name=f"`{PREFIX}stopautomod`",
                             value="Turns off Automod in your server")
        auto_embed.add_field(name=f"`{PREFIX}whitelistuser <user>`",
                             value="Make a user immune to Auto Mod (Administrators are already immune)")
        auto_embed.add_field(name=f"`{PREFIX}whitelisturl <url>`",
                             value="Allow a specific url to bypass the Auto Mod")
        auto_embed.add_field(name=f"`{PREFIX}whitelistchannel <channel>`",
                             value="Allow a specific channel to bypass the Auto Mod")
        auto_embed.add_field(name=f"`{PREFIX}automodstatus`",
                             value="Displays the status of AutoMod in your server")

        programming_embed = discord.Embed(
            title="Programming Commands Help", color=self.theme_color)
        programming_embed.add_field(
            name=f"`{PREFIX}eval <code in codeblocks>`", value="Allows you to run Python3 code in Discord")

        fun_embed = discord.Embed(title="Fun Commands Help", color=self.theme_color)
        fun_embed.add_field(name=f"`{PREFIX}coinflip`", value="Flip a coin")
        fun_embed.add_field(name=f"`{PREFIX}roll`", value="Roll a dice")
        fun_embed.add_field(name=f"`{PREFIX}avatar <user>`",
                            value="Display a users avatar")
        fun_embed.add_field(name=f"`{PREFIX}choose`",
                            value="Chooses an option for you, divide options using a comma(,)")
        fun_embed.add_field(name=f"`{PREFIX}8ball`", value='Magic crystal ball')
        fun_embed.add_field(name=f"`{PREFIX}emojify`", value='Turn all the letters in a sentence into emojis')
        #fun_embed.add_field(name=f"`{PREFIX}hangman`", value="Start a game of hangman")
        #fun_embed.add_field(name=f"`{PREFIX}rps`", value='Play a game of rock-paper-scissors')
        fun_embed.add_field(name=f"`{PREFIX}say`", value='Make Sparta Bot speak for you!')
        fun_embed.add_field(name=f'`{PREFIX}ascii`',value='Turns text into 7-bit binary numbers')
        fun_embed.add_field(name=f"`{PREFIX}pog`", value="Express yourself even better with POG gifs!")

        self.all_help_embeds = [misc_embed, server_settings_embed, mod_embed, auto_embed, programming_embed, fun_embed]

        msg: discord.Message = await ctx.send("Here is the command help:", embed=self.all_help_embeds[self.help_index])

        for emoji in self.help_control_emojis:
            await msg.add_reaction(emoji)

        self.current_help_msg = msg.id
        self.current_help_user = ctx.author.id

    @commands.command(name="hello")
    async def hello(self, ctx):
        await ctx.send("Hi, I am Sparta Bot!")

    @commands.command(name="info", aliases=['bi'])
    async def info(self, ctx):
        embed = discord.Embed(title="Bot Information", color=self.theme_color)
        ping = round(self.bot.latency * 1000)
        guild_count = len(self.bot.guilds)
        member_count = 0

        for guild in self.bot.guilds:
            member_count += guild.member_count

        embed.add_field(name="Ping", value=f"{ping}ms", inline=False)
        embed.add_field(name="Servers", value=guild_count, inline=False)
        embed.add_field(name="Total Users", value=member_count, inline=False)

        await ctx.send(content=None, embed=embed)

    @commands.command(name="invite")
    async def invite(self, ctx):
        invite_url = "https://discord.com/oauth2/authorize?client_id=731763013417435247&scope=bot&permissions=403176703"
        embed = discord.Embed(
            title="Click here to invite Sparta Bot!", url=invite_url, color=self.theme_color)
        await ctx.send(content=None, embed=embed)

    @commands.command(name="github")
    async def github(self, ctx):
        repo_url = "https://github.com/SpartaDevTeam/Old-Sparta-Bot"
        embed = discord.Embed(
            title="Click here to go to the GitHub Repository!", url=repo_url, color=self.theme_color)
        await ctx.send(content=None, embed=embed)
        await ctx.send("We are currently working on rewritting Sparta Bot, this link lead you to the old GitHub Repo")

    @commands.command(name="support")
    async def support(self, ctx):
        await ctx.send("Support Server - https://discord.gg/RrVY4bP")

    @commands.command(name="vote")
    async def vote(self, ctx):
        embed = discord.Embed(color=self.theme_color, title="Vote for Sparta Bot")
        embed.add_field(name="Vote every 12 hours", value="[top.gg](https://top.gg/bot/731763013417435247)", inline=False)
        embed.add_field(name="Vote every 24 hours", value="[dbl](https://botsfordiscord.com/bot/731763013417435247)", inline=False)
        embed.add_field(name="Join Support Server", value="[Click here](https://discord.gg/qAs3Zr2cnU)", inline=False)

        await ctx.send(embed=embed)

    @commands.command(name="clear")
    @commands.has_guild_permissions(manage_messages=True)
    async def clear(self, ctx, count: int = None):
        if count is None:
            await ctx.send("Insufficient arguments.")
        else:
            await ctx.channel.purge(limit=count+1)
            rtmsg = await ctx.send(f"Cleared the last {count} message(s)!")
            await asyncio.sleep(3)
            await rtmsg.delete()

    @commands.command(name="nuke")
    @commands.has_guild_permissions(manage_channels=True)
    async def nuke(self, ctx):
        temp_channel: discord.TextChannel = await ctx.channel.clone()
        await temp_channel.edit(position=ctx.channel.position)
        await ctx.channel.delete(reason="Nuke")
        embed = discord.Embed(
            color=self.theme_color, description=f"{ctx.author.mention} Nuked This Channel!")
        embed.set_image(
            url="https://media.tenor.com/images/04dc5750f44e6d94c0a9f8eb8abf5421/tenor.gif")
        await temp_channel.send(embed=embed)

    @commands.command(name="reminder", aliases=["remind", "remindme", "remind_me", "rm"])
    async def reminder(self, ctx, time=None, *, reminder=None):
        embed = discord.Embed(color=self.theme_color,
                              timestamp=datetime.datetime.utcnow())
        seconds = 0
        if time.lower().endswith("d"):
            seconds += int(time[:-1]) * 60 * 60 * 24
            counter = f"{seconds // 60 // 60 // 24} days"
        elif time.lower().endswith("h"):
            seconds += int(time[:-1]) * 60 * 60
            counter = f"{seconds // 60 // 60} hours"
        elif time.lower().endswith("m"):
            seconds += int(time[:-1]) * 60
            counter = f"{seconds // 60} minutes"
        elif time.lower().endswith("s"):
            seconds += int(time[:-1])
            counter = f"{seconds} seconds"

        if reminder is None:
            # Error message
            embed.add_field(name='Warning', value='Please specify what do you want me to remind you about.')

        if seconds == 0:
            embed.add_field(name='Warning', value='Please specify a proper duration.')

        if len(embed.fields) == 0:
            await ctx.send(f"Alright, I will remind you about **{reminder}** in **{counter}**.")
            await asyncio.sleep(seconds)
            await ctx.author.send(f"Hi, you asked me to remind you about **{reminder} {counter} ago**.")
            return

        await ctx.send(embed=embed)

    @commands.command(name="afk")
    async def afk(self, ctx, *, reason=None):
        embed = discord.Embed(color=self.theme_color, timestamp=datetime.datetime.utcnow())

        if str(ctx.guild.id) not in Data.server_data:
            Data.server_data[str(ctx.guild.id)] = Data.create_new_data()

        data = Data.server_data[str(ctx.guild.id)]

        # Error messages
        if reason is None:
            embed.add_field(name='Warning', value='Please specify a reason.')

        for afk_user_entry in data["afks"]:
            afk_user_id = str(afk_user_entry["user"])

            if str(ctx.author.id) == afk_user_id:
                embed.add_field(name='Warning', value='You are already AFK.')
                break

        if len(embed.fields) == 0:
            afk_entry = {
                "user": str(ctx.author.id),
                "reason": reason
            }

            Data.server_data[str(ctx.guild.id)]["afks"].append(afk_entry)
            await ctx.send(f"**{ctx.author}** is now AFK because **{reason}**")
            return

        await ctx.send(embed=embed)
