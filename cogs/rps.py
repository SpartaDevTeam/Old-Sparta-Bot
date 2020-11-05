from discord.ext import commands
import discord
import asyncio

choices = {
    '1': 'Rock',
    '2': 'Paper',
    '3': 'Scissors',
    None: '...nothing?'
}


class Player:
    def __init__(self, obj, bot):
        self.obj = obj
        self.bot = bot
        self.lives = 3
        self.choice = None

    async def get_choice(self):
        await self.obj.send(
            "Please choose an option: (1): Rock, (2): Paper, or (3): Scissors"
        )

        def check(msg):
            if msg.author.id != self.obj.id:
                return False
            if msg.content.lower() not in ['1', '2', '3']:
                return False
            return True
        try:
            msg = await self.bot.wait_for('message', check=check, timeout=60)
        except asyncio.TimeoutError:
            self.choice = None
            description = "You didn't choose anything, so you lose a life."
            await self.obj.send(description)
            self.lives -= 1
            return
        choice = msg.content
        self.choice = choice


class Game:
    def __init__(self, ctx, bot, players, color):
        self.ctx = ctx
        self.bot = bot
        self.players = [Player(p, bot) for p in players]
        self.color = color

    async def determine_winner(self, choices):
        if choices[0] == choices[1]:
            return None
        if choices[0] is None:
            return 1
        if choices[1] is None:
            return 0
        if choices[0] == '1':
            if choices[1] == '2':
                return 1
            return 0
        if choices[0] == '2':
            if choices[1] == '3':
                return 1
            return 0
        if choices[0] == '3':
            if choices[1] == '1':
                return 1
            return 0

    async def play(self):
        game_over = False
        while not game_over:
            tasks = []
            for p in self.players:
                t = asyncio.create_task(p.get_choice())
                tasks.append(t)
            for t in tasks:
                await t
            pchoices = [p.choice for p in self.players]
            winner_num = await self.determine_winner(pchoices)
            if None in pchoices:
                msg = ''
                for x, _ in enumerate(pchoices):
                    p = self.players[x]
                    if p.choice is None:
                        msg += f"{p.obj.mention} didn't choose anything, "\
                            "so they loose a point.\n"
                    else:
                        msg += f"{p.obj.mention} chose {choices[p.choice]}\n"
            elif winner_num is None:
                msg = f"Both {self.players[0].obj.mention} and "\
                    f"{self.players[1].obj.mention} chose "\
                    f"{choices[self.players[0].choice]}"
            else:
                winner = self.players[winner_num]
                loser = self.players[winner_num-1]
                loser.lives -= 1
                msg = f"{winner.obj.mention} chose {choices[winner.choice]} "\
                    f"and beat {loser.obj.mention} who chose "\
                    f"{choices[loser.choice]}."
            for x, p in enumerate(self.players):
                if p.lives == 0:
                    winner = self.players[x-1]
                    msg += f"\n{winner.obj.mention} completely "\
                        f"destroyed {p.obj.mention}!"
                    game_over = True

            embed = discord.Embed(
                title='Rock Paper Scissors', color=self.color, description=msg
            )
            embed.add_field(
                name='Lives', value=f"{self.players[0].obj}: "
                f"{self.players[0].lives} Lives \n{self.players[1].obj}: "
                f"{self.players[1].lives} Lives"
            )
            await self.ctx.send(embed=embed)
            for p in self.players:
                await p.obj.send(embed=embed)


class RockPaperScissors(commands.Cog):
    def __init__(self, bot, color):
        self.bot = bot
        self.color = color

    @commands.command(name='rps')
    @commands.guild_only()
    async def start_rps_game(self, ctx, target: discord.User):
        if target is None or target.id not in [m.id for m in ctx.guild.members]:
            await ctx.send("I can't find that user")
            return
        if target.bot:
            await ctx.send("You can't challenge a bot")
            return
        if target.id == ctx.message.author.id:
            await ctx.send("You can't play yourself")
            return
        await ctx.send(
            f"{target.mention}, {ctx.message.author.mention} "
            "is challenging you to a game of rock-paper-scissors!"
            "\nType \"accept\" to accept, or \"decline\" to decline."
        )

        def check(message):
            if message.author.id != target.id:
                return False
            if message.content.lower() not in [
                'accept', 'yes', 'deny', 'no', 'decline'
            ]:
                return False
            return True
        try:
            msg = await self.bot.wait_for('message', check=check, timeout=120)
        except asyncio.TimeoutError:
            await ctx.send(
                f"{ctx.message.author.mention}, the challenge timed out!"
            )
            return
        if msg.content.lower() in ['deny', 'no', 'decline']:
            await ctx.send("Cancelled")
            return
        await ctx.send("Game started!")
        game = Game(ctx, self.bot, [ctx.message.author, target], self.color)
        await game.play()
