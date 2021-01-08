import random
import discord
from discord.ext import commands
import pyfiglet


class Fun(commands.Cog):
    def __init__(self, bot, color):
        self.bot = bot
        self.color = color

    @commands.command(
        name='8ball', brief='Answers a question randomly',
        description='Answers a question randomly'
    )
    async def eight_ball(self, ctx, *, question):
        respond_no = [
            'No.', 'Nope.', 'Highly Doubtful.', 'Not a chance.',
            'Not possible.', 'Don\'t count on it.'
        ]
        respond_yes = [
            'Yes.', 'Yup', 'Extremely Likely', 'It is possible',
            'Very possibly.'
        ]
        combined = [respond_no, respond_yes]
        group = random.choice([0, 1])
        answer = random.choice(combined[group])

        embed = discord.Embed(
            description=f"**Question:** {question}"
            f"\n\n**Answer:** {answer}",
            color=self.color
        )
        embed.set_author(
            name=str(ctx.message.author),
            url=ctx.message.author.avatar_url
        )
        await ctx.send(embed=embed)

    @commands.command(
        name='emojify', brief='Converts letters in a sentence to emojis',
        description='Converts letters in a sentence to emojis'
    )
    async def emojify(self, ctx, *, sentence):
        index = {
            'a': '🇦',
            'b': '🇧',
            'c': '🇨',
            'd': '🇩',
            'e': '🇪',
            'f': '🇫',
            'g': '🇬',
            'h': '🇭',
            'i': '🇮',
            'j': '🇯',
            'k': '🇰',
            'l': '🇱',
            'm': '🇲',
            'n': '🇳',
            'o': '🇴',
            'p': '🇵',
            'q': '🇶',
            'r': '🇷',
            's': '🇸',
            't': '🇹',
            'u': '🇺',
            'v': '🇻',
            'w': '🇼',
            'x': '🇽',
            'y': '🇾',
            'z': '🇿',
            '0': ':zero:',
            '1': ':one:',
            '2': ':two:',
            '3': ':three:',
            '4': ':four:',
            '5': ':five:',
            '6': ':six:',
            '7': ':seven:',
            '8': ':eight:',
            '9': ':nine:',
            '!': ':exclamation:',
            '#': ':hash:',
            '?': ':question:',
            '*': ':asterisk:'
        }
        sentence = sentence.lower()
        new_sentence = ''
        for char in sentence:
            if char in index:
                new_sentence += index[char]
            else:
                new_sentence += char
            new_sentence += ' '
        await ctx.send(new_sentence)

    @commands.command(name="coinflip")
    async def coinflip(self, ctx):
        choices = ["Heads", "Tails"]
        rancoin = random.choice(choices)
        await ctx.send(rancoin)

    @commands.command(name="roll")
    async def roll(self, ctx):
        choices = [1, 2, 3, 4, 5, 6]
        ranroll = random.choice(choices)
        await ctx.send(ranroll)

    @commands.command(name="choose", aliases=['ch'])
    async def choose(self, ctx, *, choices: str):
        choicelist = choices.split(",")
        await ctx.send("I choose " + random.choice(choicelist).strip())

    @commands.command(name="avatar", aliases=['av'])
    async def avatar(self, ctx, user: discord.Member = None):
        if user is None:
            user = ctx.author

        aembed = discord.Embed(
            color=self.color,
            title=f"{user}"
        )

        aembed.set_image(url=f"{user.avatar_url}")
        await ctx.send(embed=aembed)

    @commands.command(name='ascii')
    async def ascii(self, ctx, *, msg: str):
        txt = pyfiglet.figlet_format(msg, font='big')
        await ctx.send(f"```{txt}```")

    @commands.command(name="say")
    async def say(self, ctx, *, sentence: str):
        if len(ctx.message.mentions) + len(ctx.message.role_mentions) > 0:
            await ctx.send("You cannot mention people or roles using this command.")
            return

        if "@everyone" in ctx.message.content or "@here" in ctx.message.content:
            await ctx.send("You cannot mention people or roles using this command.")
            return

        await ctx.send(sentence)

    @commands.command(name="pog")
    async def pog(self, ctx):
        pog_gifs = [
            "https://tenor.com/view/pog-fish-fish-mouth-open-gif-17487624",
            "https://tenor.com/view/fish-pog-fish-poggers-fish-pog-champ-poggers-gif-16548474",
            "https://tenor.com/view/cat-happy-pog-cute-smile-gif-17223821",
            "https://tenor.com/view/vsauce-vsauce-pog-poggers-vsauce-poggers-pog-gif-18430372"
        ]

        await ctx.send(random.choice(pog_gifs))
