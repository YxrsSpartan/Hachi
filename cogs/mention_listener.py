import discord
from discord.ext import commands

class MentionListener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user or message.author.bot:
            return

        if self.bot.user.mentioned_in(message):
            mentions = [mention for mention in message.mentions if mention == self.bot.user]
            if mentions and (message.content.strip() == mentions[0].mention):
                embed = discord.Embed(
                    description=f"<:Blue_Information:1285085972194787388> **{message.author.mention} : My prefix is `?`**",
                    color=discord.Color.purple()
                )
                
                await message.channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(MentionListener(bot))
