import discord
from discord.ext import commands
import random

class ExtraSmart(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def cute(self, ctx, *, user: discord.Member = None):
        user = user or ctx.author  
        cuteness_level = random.randint(0, 150)
        embed = discord.Embed(
            description=f"{user.mention} has a cuteness level of **{cuteness_level}/150**! 🥰",
            color=0xE0FFFF
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def gay(self, ctx, *, user: discord.Member = None):
        user = user or ctx.author  
        gay_level = random.randint(0, 100)
        embed = discord.Embed(
            description=f"{user.mention} has a gay level of **{gay_level}/100**! 🌈",
            color=0xE0FFFF
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def lesbo(self, ctx, *, user: discord.Member = None):
        user = user or ctx.author  
        lesbo_level = random.randint(0, 100)
        embed = discord.Embed(
            description=f"{user.mention} has a lesbian level of **{lesbo_level}/100**! 🌈",
            color=0xE0FFFF
        )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ExtraSmart(bot))
