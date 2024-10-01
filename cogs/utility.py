import discord
from discord.ext import commands
import asyncio
from datetime import datetime
import platform
import psutil

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = datetime.utcnow()
        self.report_channel_id = 1280761523794477098  

    @commands.command(name='ping')
    async def ping(self, ctx):
        latency = self.bot.latency * 1000  
        embed = discord.Embed(
            description=f'<:latency:1285105853502062724> {ctx.author.mention}: **Hachi is currently experiencing a latency of `{latency:.0f}ms`**',
            color=discord.Color.blue()
        )

        await ctx.send(embed=embed)

    @commands.command(name='avatar', aliases=['av'])
    async def avatar(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        avatar_url = member.display_avatar.url

        embed = discord.Embed(
            description=f'<:icon_Download:1285222326891450390>**[Download]({avatar_url})**',
            color=discord.Color.blue()
        )
        embed.set_image(url=avatar_url)
        embed.set_footer(
            text=f'Requested by {ctx.author.name}', 
            icon_url=ctx.author.display_avatar.url
        )
        await ctx.send(embed=embed)

    @commands.command(name='banner')
    async def banner(self, ctx, member: discord.Member = None):
        member = member or ctx.author

        try:
            user = await self.bot.fetch_user(member.id)
        except discord.DiscordException as e:
            await ctx.send(f'Error fetching user: {e}')
            return

        banner_url = user.banner.url if user.banner else None
        if banner_url:
            embed = discord.Embed(
                description=f'<:icon_Download:1285222326891450390>**[Download]({banner_url})**',
                color=discord.Color.blue()
            )
            embed.set_image(url=banner_url)
        else:
            embed = discord.Embed(
                description=f'**{member.mention} does not have a banner.**',
                color=discord.Color.blue()
            )

        embed.set_footer(
            text=f'Requested by {ctx.author.name}', 
            icon_url=ctx.author.display_avatar.url
        )
        await ctx.send(embed=embed)

    @commands.command(name='uptime')
    async def uptime(self, ctx):
        now = datetime.utcnow()
        uptime_duration = now - self.start_time

        days, hours, minutes = uptime_duration.days, uptime_duration.seconds // 3600, (uptime_duration.seconds % 3600) // 60
        seconds = uptime_duration.seconds % 60

        uptime_str = f"{days}d {hours}h {minutes}m {seconds}s"

        embed = discord.Embed(
            description=f"{ctx.author.mention}: Hachi has been up for **{uptime_str}**",
            color=discord.Color.blue()
        )

        await ctx.send(embed=embed)

    @commands.command(name='invite', aliases=['inv'])
    async def invite(self, ctx):
        invite_url = 'https://discord.com/oauth2/authorize?client_id=1280119054925037609'
        support_server_url = 'https://discord.gg/KretHCmdNZ' 

        embed = discord.Embed(
            description=f"**[Invite Hachi]({invite_url})**\n**[Support Server]({support_server_url})**",
            color=discord.Color.blue()
        )

        invite_button = discord.ui.Button(label="Invite Hachi", style=discord.ButtonStyle.link, url=invite_url)
        support_button = discord.ui.Button(label="Hachi Support", style=discord.ButtonStyle.link, url=support_server_url)

        view = discord.ui.View()
        view.add_item(invite_button)
        view.add_item(support_button)

        await ctx.send(embed=embed, view=view)

    @commands.command(name='report')
    async def report(self, ctx):
        embed = discord.Embed(
            description="**If you have any issues to report, please click the `Report an Issue` button below. If you want to delete this message, click the `Delete` button.**",
            color=discord.Color.blue()
        )
        embed.set_footer(text='Requested by ' + ctx.author.name, icon_url=ctx.author.display_avatar.url)

        report_button = discord.ui.Button(label="Report an Issue", style=discord.ButtonStyle.secondary)
        delete_button = discord.ui.Button(label="Delete", style=discord.ButtonStyle.danger)

        view = discord.ui.View()
        view.add_item(report_button)
        view.add_item(delete_button)

        async def on_report_button_click(interaction):
            if interaction.user != ctx.author:
                return await interaction.response.send_message("You cannot interact with this button.", ephemeral=True)

            await interaction.response.send_message("**Please describe your issue in the DM I will send you.**", ephemeral=True)

            dm_channel = await interaction.user.create_dm()
            await dm_channel.send("Please describe your issue here. The team will be notified.")

            def check(msg):
                return msg.author == interaction.user and msg.channel == dm_channel

            try:
                user_msg = await self.bot.wait_for('message', timeout=300.0, check=check)
                
                report_channel = self.bot.get_channel(self.report_channel_id)
                if report_channel:
                    await report_channel.send(f"Report from {interaction.user}:\n{user_msg.content}")
            except asyncio.TimeoutError:
                await dm_channel.send("You took too long to respond. Please try again.")

        async def on_delete_button_click(interaction):
            if interaction.user != ctx.author:
                return await interaction.response.send_message("You cannot interact with this button.", ephemeral=True)
            
            await interaction.message.delete()

        report_button.callback = on_report_button_click
        delete_button.callback = on_delete_button_click

        message = await ctx.send(embed=embed, view=view)

        await asyncio.sleep(90)

        for item in view.children:
            item.disabled = True
        
        await message.edit(view=view)

    @commands.command(name='stats')
    async def stats(self, ctx):
        bot_ping = round(self.bot.latency * 1000)
        bot_id = self.bot.user.id
        bot_owner = "[zeryalssss](https://discord.com/users/1197668897629949972)" 
        total_servers = len(self.bot.guilds)
        total_channels = sum(len(guild.channels) for guild in self.bot.guilds)
        total_users = len(set(self.bot.get_all_members()))
        bot_uptime = datetime.utcnow() - self.start_time

        system_info = {
            "OS": platform.system(),
            "OS Version": platform.version(),
            "Architecture": platform.architecture()[0],
            "CPU": platform.processor(),
            "Physical Cores": psutil.cpu_count(logical=False),
            "Logical Cores": psutil.cpu_count(logical=True),
            "Physical Memory (RAM)": f"{psutil.virtual_memory().total / (1024 ** 3):.2f} GB",
            "Available RAM": f"{psutil.virtual_memory().available / (1024 ** 3):.2f} GB",
            "CPU Usage": f"{psutil.cpu_percent()}%",
        }

        bot_version = "1.1.0" 
        python_version = platform.python_version()

        embed = discord.Embed(
            color=discord.Color.blue()
        )

        embed.add_field(name="<a:esj_cloud:1279125702133940298>**Hachi Information**", value=(
            f"> <:BlueArrow:1274325911252107305> **Bot Mention**: {self.bot.user.mention}\n"
            f"> <:BlueArrow:1274325911252107305> **Bot ID**: {bot_id}\n"
            f"> <:BlueArrow:1274325911252107305> **Bot Owner**: {bot_owner}\n"
            f"> <:BlueArrow:1274325911252107305> **Bot Version**: {bot_version}\n"
            f"> <:BlueArrow:1274325911252107305> **Python Version**: {python_version}\n"
            f"> <:BlueArrow:1274325911252107305> **Bot Ping**: {bot_ping}ms\n"
            f"> <:BlueArrow:1274325911252107305> **Total Servers**: {total_servers}\n"
            f"> <:BlueArrow:1274325911252107305> **Total Channels**: {total_channels}\n"
            f"> <:BlueArrow:1274325911252107305> **Total Users**: {total_users}\n"
            f"> <:BlueArrow:1274325911252107305> **Uptime**: {bot_uptime.days}d {bot_uptime.seconds // 3600}h {bot_uptime.seconds % 3600 // 60}m {bot_uptime.seconds % 60}s"
        ), inline=False)

        embed.add_field(name="<:MekoServer:1274361730712997888>**System Information**", value=(
            f"> <:BlueArrow:1274325911252107305> **OS**: {system_info['OS']} {system_info['OS Version']} ({system_info['Architecture']})\n"
            f"> <:BlueArrow:1274325911252107305> **CPU**: {system_info['CPU']} ({system_info['Physical Cores']} physical cores, {system_info['Logical Cores']} logical cores)\n"
            f"> <:BlueArrow:1274325911252107305> **Memory (RAM)**: {system_info['Physical Memory (RAM)']} (Available: {system_info['Available RAM']})\n"
            f"> <:BlueArrow:1274325911252107305> **CPU Usage**: {system_info['CPU Usage']}%"
        ), inline=False)

        embed.set_footer(
            text=f'Requested by {ctx.author.name}', 
            icon_url=ctx.author.display_avatar.url
        )

        await ctx.send(embed=embed)
        
    @commands.command(name='about')
    async def about(self, ctx):
        description = (
            "**Hachi** is a versatile Discord bot designed to enhance your server's voice chat experience. "
            "With Hachi's** VoiceMaster features**, you can easily create temporary voice channels that automatically delete "
            "when empty, ensuring a clean and organized server. **Hachi** also offers a wide range of **utility commands**, "
            "general command, and more to help you manage your community efficiently.\n\n"
            "Whether you want to customize your voice channels, fetch user information, or simply have some fun, Hachi is here to assist you."
        )

        developers = (
            "**Developers & Contributors**\n"
            "> **[zeryalssss](https://discord.com/users/1197668897629949972) --- Head Developer**\n"
            "> **Version**: 1.1.0\n"
            "> **Language**: Python 3.10.15\n"
            "> **Library**: discord.py"
        )

        embed = discord.Embed(
            description=description,
            color=discord.Color.blue()
        )

        embed.add_field(
            name="Key Features",
            value=(
                "> <:BlueArrow:1274325911252107305> **VoiceMaster**: Temporary voice channels\n"
                "> <:BlueArrow:1274325911252107305> **Tts**: Text to speech fucntion\n"
                "> <:BlueArrow:1274325911252107305> **General**: avatar, banner, stats, and more"
            ),
            inline=False
        )

        embed.add_field(name="", value=developers, inline=False)

        embed.set_footer(
            text=f'Requested by {ctx.author.name}', 
            icon_url=ctx.author.display_avatar.url
        )

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Utility(bot))
