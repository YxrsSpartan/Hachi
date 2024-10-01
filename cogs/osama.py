from discord.ext import commands
import discord

class Osama(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='vote')
    async def vote(self, ctx):
        vote_url = 'https://top.gg/bot/1280119054925037609'  

        message = f"Click On The Button To [Vote Me](https://top.gg/bot/1280119054925037609)!"

        vote_button = discord.ui.Button(label="Vote", style=discord.ButtonStyle.link, url=vote_url, 
        emoji="<:topgg:1281234728527335474>") 

        view = discord.ui.View()
        view.add_item(vote_button)

        await ctx.send(content=message, view=view) 

async def setup(bot):
    await bot.add_cog(Osama(bot))
