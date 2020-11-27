import datetime
import discord
import inspect
import urbandictionary as ud
import re
from discord.ext import commands
import functools
import googletrans
import urllib.request
import urllib.parse
import wikipediaapi

class Google(commands.Cog):
    def __init__(self, bot, theme_color):
        self.bot = bot
        self.theme_color = theme_color

    """
    @commands.command(name='translate')
    async def _translate(self, ctx, langs="", *, text):

        def convert(s: str) -> dict:
            a = s.lower().split()
            res = {
                a[i]: a[i + 1]
                for i in range(len(a)) if a[i] in ("from", "to")
            }
            res["from"] = res.get("from") or "auto"
            res["to"] = res.get("to") or "en"
            return res

        try:
            langdict = convert(langs)
        except IndexError:
            raise commands.BadArgument("Invalid language format.")
        translator = googletrans.Translator()
        tmp = functools.partial(
            translator.translate,
            text,
            src=langdict["from"],
            dest=langdict["to"])
        try:
            async with ctx.typing():
                res = await self.bot.loop.run_in_executor(None, tmp)
        except ValueError as e:
            raise commands.BadArgument(e.args[0].capitalize())
        await ctx.send(res.text.replace("@", "@\u200b"))

    @commands.command(pass_context=True)
    async def urban(self, ctx, *, word):
        ': Search the Urban Dictionary'

        def linkify(s):
            s = str(s)
            s = s.replace("[word]", "[").replace("[/word]", "]")
            links = re.findall('\\[(.*?)\\]', s)
            r = s
            for link in links:
                r = r.replace('[' + link + ']', '[{}]({})'.format(
                    link, ('http://api.urbandictionary.com/v0/define?term=' +
                           link.replace(' ', '+').lower().replace('-', ''))))
            return r

        try:
            a = ud.define(word.replace(" ", "+"))[0]
            if len(a.definition) <= 2000:
                embed = discord.Embed(
                    title=f'\U0001f4d6 {word} ',
                    colour=discord.Colour.dark_purple(),
                    description=f'''{linkify(a.definition)}''',
                    url=
                    f'''http://api.urbandictionary.com/v0/define?term={word}'''
                )
                embed.add_field(
                    name='Examples', value=f'''{linkify(a.example)}''')
                embed.add_field(
                    name='Upvotes',
                    value=
                    f'''{a.upvotes} ({(a.upvotes/(a.upvotes+a.downvotes))*100:.2f}%)'''
                )
                embed.add_field(
                    name='Downvotes',
                    value=
                    f'''{a.downvotes} ({(a.downvotes/(a.upvotes+a.downvotes))*100:.2f}%)'''
                )
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(
                    title=f'\U0001f4d6 {word}',
                    colour=discord.Colour.dark_purple(),
                    description=
                    f'''{a.definition[:1960]}[...continue reading](http://api.urbandictionary.com/v0/define?term={word})''',
                    url=
                    f'''http://api.urbandictionary.com/v0/define?term={word}'''
                )
                embed.add_field(
                    name='Examples', value=f'''{linkify(a.example)}''')
                embed.add_field(
                    name='Upvotes',
                    value=
                    f'''{a.upvotes} ({(a.upvotes/(a.upvotes+a.downvotes))*100:.2f}%)'''
                )
                embed.add_field(
                    name='Downvotes',
                    value=
                    f'''{a.downvotes} ({(a.downvotes/(a.upvotes+a.downvotes))*100:.2f}%)'''
                )
                await ctx.send(embed=embed)
        except IndexError:
            await ctx.send(
                f'''Unable to find {word} in Urban dictionary''',
                delete_after=3)

    @commands.command(passcontext=True)
    async def youtube(self, ctx, *, youtube):
        ': Search YouTube '

        query_string = urllib.parse.urlencode({
            'search_query': youtube,
        })
        html_content = urllib.request.urlopen(
            'http://www.youtube.com/results?' + query_string)
        search_results = re.findall('href=\\"\\/watch\\?v=(.{11})',
                                    html_content.read().decode())
        await ctx.send('http://www.youtube.com/watch?v=' + search_results[0])
    """
    
    @commands.command(name='wiki')
    async def google_search(self, ctx, *args):
        wiki_wiki = wikipediaapi.Wikipedia('en')

        page_py = wiki_wiki.page(args)
        page_py = wiki_wiki.page(args)
        print("Page - Exists: %s" % page_py.exists())
        # Page - Exists: True

        page_missing = wiki_wiki.page('NonExistingPageWithStrangeName')
        print("Page - Exists: %s" %     page_missing.exists())
        # Page - Exists: False

        wiki_wiki = wikipediaapi.Wikipedia('en')

        print("Page - Title: %s" % page_py.title)
            # Page - Title: Python (programming language)

        print("Page - Summary: %s" % page_py.summary[0:60])
            # Page - Summary: Python is a widely used high-level programming language for
        embed = discord.Embed(
        title =page_py.title ,
        description = page_py.summary[0:2000],
        colour = self.theme_color
        )
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Google(bot))
