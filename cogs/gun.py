import discord
from discord.ext import commands
import time

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time() 

    @commands.command(name="ping")
    async def ping(self, ctx):
        """Check the bot's ping (latency)."""
        bot_avatar_url = self.bot.user.avatar.url if self.bot.user.avatar else None

        start_time = time.time()
        message = await ctx.send("Calculating latency...")
        end_time = time.time()

        api_latency = round((end_time - start_time) * 1000, 2)  
        websocket_latency = round(self.bot.latency * 1000, 2)  

        embed = discord.Embed(color=discord.Color.blue())
        embed.set_author(name="Voxia Latency Information", icon_url=bot_avatar_url)
        embed.add_field(
            name="",
            value=f"**API Latency**: `{api_latency}`ms\n"
                  f"**WebSocket Latency**: `{websocket_latency}`ms\n"
                  f"**Message Latency**: `{api_latency}`ms"
        )
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url) 

        await message.edit(content=None, embed=embed)

    @commands.command(name="uptime")
    async def uptime(self, ctx):
        """Check how long the bot has been online."""
        bot_avatar_url = self.bot.user.avatar.url if self.bot.user.avatar else None

        current_time = time.time()
        uptime_seconds = current_time - self.start_time 
        uptime_str = self.convert_seconds_to_time(uptime_seconds)

        embed = discord.Embed(color=discord.Color.blue())
        embed.set_author(name="Voxia Uptime", icon_url=bot_avatar_url)
        embed.description = f"The bot has been up for: {uptime_str}"
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)  

        await ctx.send(embed=embed)

    @commands.command(name="avatar")
    async def avatar(self, ctx, member: discord.Member = None):
        """Get a user's avatar."""
        member = member or ctx.author  
        avatar_url = member.avatar.url if member.avatar else member.default_avatar.url

        embed = discord.Embed(color=0x2b2d31)  
        embed.set_title(f"{member.display_name}'s Avatar") 
        embed.set_image(url=avatar_url)  
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)  

        await ctx.send(embed=embed)

    @commands.command(name="banner")
    async def banner(self, ctx, member: discord.Member = None):
        """Get a user's banner."""
        member = member or ctx.author  

        if member.banner:
            banner_url = member.banner.url
            embed = discord.Embed(color=0x2b2d31)  
            embed.set_title(f"{member.display_name}'s Banner")  
            embed.set_image(url=banner_url)
            embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)  
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(color=0x2b2d31)
            embed.set_title("No Banner Found")
            embed.description = f"{member.display_name} does not have a banner."
            embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)  
            await ctx.send(embed=embed)

    def convert_seconds_to_time(self, seconds):
        """Convert seconds into a human-readable format (Days, Hours, Minutes, Seconds)."""
        days = int(seconds // 86400)
        seconds %= 86400
        hours = int(seconds // 3600)
        seconds %= 3600
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)

        uptime_str = f"{days}d {hours}h {minutes}m {seconds}s"
        return uptime_str

async def setup(bot):
    await bot.add_cog(General(bot))
