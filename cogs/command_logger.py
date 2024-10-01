import discord
from discord.ext import commands

LOG_CHANNEL_ID = 1287081318672498798 

class CommandLogger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command(self, ctx):
        embed = discord.Embed(
            title="Command Used",
            description=(
                f"**Command:** {ctx.command}\n"
                f"**Aliases:** {', '.join(ctx.command.aliases) if ctx.command.aliases else 'None'}\n"
                f"**Server:** {ctx.guild.name}\n"
                f"**User:** {ctx.author.name}#{ctx.author.discriminator}\n"
                f"**User ID:** {ctx.author.id}\n"
                f"**Server ID:** {ctx.guild.id}"
            ),
            color=discord.Color.blue(),
            timestamp=ctx.message.created_at
        )

        embed.set_thumbnail(url=ctx.author.avatar.url)  

        channel = self.bot.get_channel(LOG_CHANNEL_ID)

        if channel is None:
            print(f"Failed to find log channel with ID: {LOG_CHANNEL_ID}")
            return

        try:
            await channel.send(embed=embed)
        except Exception as e:
            print(f"Error sending embed: {e}")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        pass

async def setup(bot):
    await bot.add_cog(CommandLogger(bot))
