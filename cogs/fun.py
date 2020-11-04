import random
import discord
from discord.ext import commands


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
