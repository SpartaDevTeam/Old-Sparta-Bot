import random
import asyncio
import string
from discord.ext import commands

BOARD = \
    """\
    ```
    _______
    |     |
    |     {}
    |    {}{}{}
    |     {}
    |    {} {}
    |______\
    ```
    """


class Hanger():
    def __init__(self):
        self.lives = 7
        self.current_part = 1
        self.board = BOARD
        self.parts = {
            1: 'o',
            2: '/',
            3: '|',
            4: '\\',
            5: '|',
            6: '/',
            7: '\\'
        }
        self.current_parts = {
            1: ' ',
            2: ' ',
            3: ' ',
            4: ' ',
            5: ' ',
            6: ' ',
            7: ' '
        }

    async def get_board(self):
        cp = self.current_parts
        return self.board.format(
            cp[1], cp[2], cp[3], cp[4], cp[5], cp[6], cp[7]
        )

    async def add_part(self):
        self.lives -= 1
        self.current_parts[self.current_part] = self.parts[self.current_part]
        self.current_part += 1


class Game():
    def __init__(self, members, bot, channel):
        self.members = members
        self.bot = bot
        self.phrase = []
        self.guessed_chars = []
        self.guessed_phrase = []
        self.phraser = None
        self.guessers = []
        self.channel = channel
        self.hanger = Hanger()
        self.going = True

    async def play(self):
        await self._initialize()
        if self.going:
            await self._send_to_all(
                self.guessers + [self.phraser],
                "The game has started!"
            )
            await self.channel.send("The game has started!")
        last_choice = -1
        while self.going:
            last_choice += 1
            if last_choice > len(self.guessers)-1:
                last_choice = 0
            await self.channel.send(await self.show_board())
            round_guesser = self.guessers[last_choice]
            await self.get_guess(round_guesser)

            if self.hanger.lives == 0:
                await self.channel.send(await self.show_board())
                await self._send_to_all(
                    self.guessers + [self.phraser, self.channel],
                    "The man was hung, so the phraser, "
                    f"{self.phraser.mention}, wins!"
                )
                await self.channel.send(
                    f"The phrase was **{''.join(self.phrase)}**"
                )
                return

            found = False
            for char in self.guessed_phrase:
                if char == '-':
                    found = True
            if not found:
                await self.channel.send(await self.show_board())
                await self._send_to_all(
                    self.guessers + [self.phraser, self.channel],
                    f"{round_guesser.mention} wins!"
                )
                return

    async def show_board(self):
        phrase = await self.get_guessed_phrase()
        board = await self.hanger.get_board()
        to_send = board + f"**{phrase}**"
        return to_send

    async def get_guessed_phrase(self):
        current_phrase = ''
        for char in self.guessed_phrase:
            current_phrase += char
        return current_phrase

    async def get_guess(self, member):
        def check(msg):
            if msg.author.id != member.id:
                return False
            if msg.content not in ['1', '2']:
                return False
            if msg.channel.id != self.channel.id:
                return False
            return True
        await self.channel.send(
            f"{member.mention}, "
            "It's your turn to choose! Do you want to (1) guess a "
            "letter or (2) guess the phrase?"
        )
        try:
            choice = await self.bot.wait_for(
                'message', check=check, timeout=120
            )
        except asyncio.TimeoutError:
            await self.channel.send(
                f"Due to lack of response, {member.mention} "
                "has been removed from the game."
            )
            self.guessers.remove(member)
            if len(self.guessers) < 1:
                await self.channel.send(
                    "There are no more guessers, "
                    "so the game ends, and the phraser, "
                    f"{self.phraser.mention}, wins!"
                )
                self.going = False
            return
        if choice.content == '1':
            await self._guess_letter(member)
        else:
            await self._guess_phrase(member)

    async def _guess_phrase(self, member):
        await self.channel.send(f"{member.mention}, Please enter the phrase.")

        def check(msg):
            if msg.author.id != member.id:
                return False
            if msg.channel.id != self.channel.id:
                return False
            return True

        try:
            msg = await self.bot.wait_for('message', check=check, timeout=180)
            if len(msg.content) != len(self.phrase):
                await self.channel.send(
                    "That's not the same length as the actual phrase. "
                    "Make sure to include special chars like '."
                )
                return await self.get_guess(member)
        except asyncio.TimeoutError:
            await self.channel.send(
                "You will be skipped this round because you didn't respond"
            )
            return

        guess = msg.content.lower()
        if guess == ''.join(self.phrase):
            await self.channel.send("Correct!")
            self.guessed_phrase = self.phrase
        else:
            await self.channel.send("Sorry, but that's not right.")
            await self.hanger.add_part()

    async def _guess_letter(self, member):
        await self.channel.send(
            f"{member.mention}, Please enter a letter to guess."
        )

        def check(msg):
            if msg.author.id != member.id:
                return False
            if len(msg.content) > 1:
                return False
            if msg.content.lower() not in list(string.ascii_letters):
                return False
            if msg.channel.id != self.channel.id:
                return False
            return True

        try:
            msg = await self.bot.wait_for('message', check=check, timeout=60)
        except asyncio.TimeoutError:
            await self.channel.send(
                "You will be skiped this round because you didn't respond"
            )
            return

        guess = msg.content.lower()
        if guess in self.guessed_chars:
            await self.channel.send("That letter has already been guessed.")
            return await self.get_guess(member)
        self.guessed_chars.append(guess)
        if guess in self.phrase:
            for x, char in enumerate(self.phrase):
                if char == guess:
                    self.guessed_phrase[x] = guess
            await self.channel.send("Correct!")
        else:
            await self.hanger.add_part()
            await self.channel.send("Oops! That letter is not in the word.")

    async def _initialize(self):
        random.shuffle(self.members)
        self.phraser = self.members.pop()
        self.guessers = self.members

        await self._send_to_all(
            self.guessers,
            "You are a guesser! Please wait while "
            f"{self.phraser.mention} chooses a phrase."
        )
        await self.phraser.send(
            "You are the phraser! Please choose a phrase for other people "
            "to guess.\nIt must be less than 32 characters."
        )
        await self._get_phrase()

    async def _get_phrase(self):
        def check(msg):
            if msg.author.id != self.phraser.id:
                return False
            if msg.guild is not None:
                return False
            return True
        try:
            msg = await self.bot.wait_for('message', check=check, timeout=120)
        except asyncio.TimeoutError:
            await self.phraser.send(
                "You didn't choose a phrase, so the game ended."
            )
            await self.channel.send(
                "The phraser didn't choose a phrase, so the game ended."
            )
            self.going = False
            return
        phrase = msg.content.lower()
        if len(phrase) > 32:
            await self.phraser.send(
                f"That phrase is too long! {len(phrase)} > 32"
            )
            return await self._get_phrase()

        self.phrase = []
        self.guessed_phrase = []
        for char in phrase:
            self.phrase += char
            if char not in [c for c in string.ascii_letters]:
                self.guessed_phrase += char
            else:
                self.guessed_phrase += '-'
        return True

    async def _send_to_all(self, mlist, msg):
        for m in mlist:
            await m.send(msg)


class Hangman(commands.Cog):
    def __init__(self, bot, color):
        self.bot = bot
        self.color = color

    @commands.command(name='hm')
    @commands.guild_only()
    async def start_hangman(self, ctx):
        game_msg = await ctx.channel.send(
            f"{ctx.message.author} has opened a game of hangman! React "
            f"below to join. {ctx.message.author.mention}, the game "
            "will start when you type \"start game\""
        )
        await game_msg.add_reaction('✅')

        async def wait_for_game_start():
            def check(msg):
                if msg.author.id != ctx.message.author.id:
                    return False
                if msg.content.lower() not in ["start game", "cancel"]:
                    return False
                if msg.channel.id != ctx.channel.id:
                    return False
                return True

            try:
                msg = await self.bot.wait_for(
                    'message', check=check, timeout=600
                )
            except asyncio.TimeoutError:
                await ctx.send("Game timed out")
                return
            if msg.content.lower() == 'cancel':
                await ctx.send("Game Cancelled")
                return []
            users = set()
            update_msg = await ctx.channel.fetch_message(game_msg.id)
            for reaction in update_msg.reactions:
                async for user in reaction.users():
                    if not user.bot:
                        users.add(user.id)
            users.add(ctx.message.author.id)
            num_users = len(users)
            if num_users < 2:
                await ctx.send(
                    "There are not enough people to play. "
                    f"Minimum is 2, and you only have {num_users}."
                )
                return await wait_for_game_start()
            return users

        users = await wait_for_game_start()
        if users == []:
            return
        members = []
        for user_id in users:
            member = ctx.guild.get_member(user_id)
            members.append(member)
        await ctx.send("Starting Game")

        game = Game(members, self.bot, ctx.channel)
        await game.play()
