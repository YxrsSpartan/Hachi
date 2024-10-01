import discord
from discord.ext import commands
import aiohttp
from datetime import datetime

class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.join_channel_id = 1287081193447358495  
        self.leave_channel_id = 1287081223100960828  

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        owner = guild.owner
        member_count = guild.member_count
        server_invite_link = await self.generate_invite_code(guild)
        
        guild_creation_date = guild.created_at.strftime("%A, %B %d, %Y at %I:%M %p UTC")
        bot_joined_date = datetime.utcnow().strftime("%A, %B %d, %Y at %I:%M %p UTC")


        region = guild.region if hasattr(guild, 'region') else 'Unknown'
        boost_level = guild.premium_tier
        verification_level = guild.verification_level
        total_channels = len(guild.channels)
        total_roles = len(guild.roles)
        total_boosts = guild.premium_subscription_count

        embed = discord.Embed(
            title="📥 New Server Joined",
            description="Here are the details of the newly joined server:",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="Server Details", 
            value=(f"**Server Name**: {guild.name}\n"
                   f"**Owner**: {owner} (`{owner.id}`)\n"
                   f"**Member Count**: {member_count} members\n"
                   f"**Region**: {region}\n"
                   f"**Boost Level**: {boost_level}\n"
                   f"**Verification Level**: {verification_level}\n"
                   f"**Total Channels**: {total_channels}\n"
                   f"**Total Roles**: {total_roles}\n"
                   f"**Total Boosts**: {total_boosts}\n"
                   f"**Server Invite Link**: [Invite Link]({server_invite_link})\n"
                   f"**Server Creation Date**: {guild_creation_date}\n"
                   f"**Bot Joined Date**: {bot_joined_date}\n"
                   f"**Total Servers**: {len(self.bot.guilds)}"), 
            inline=False
        )
        
        await self.send_message_to_channel(self.join_channel_id, embed)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        owner = guild.owner
        member_count = guild.member_count
        
        guild_creation_date = guild.created_at.strftime("%A, %B %d, %Y at %I:%M %p UTC")
        bot_left_date = datetime.utcnow().strftime("%A, %B %d, %Y at %I:%M %p UTC")

        region = guild.region if hasattr(guild, 'region') else 'Unknown'
        boost_level = guild.premium_tier
        verification_level = guild.verification_level
        total_channels = len(guild.channels)
        total_roles = len(guild.roles)
        total_boosts = guild.premium_subscription_count

        embed = discord.Embed(
            title="📤 Server Left",
            description="Here are the details of the server that was left:",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="Server Details", 
            value=(f"**Server Name**: {guild.name}\n"
                   f"**Owner**: {owner} (`{owner.id}`)\n"
                   f"**Member Count**: {member_count} members\n"
                   f"**Region**: {region}\n"
                   f"**Boost Level**: {boost_level}\n"
                   f"**Verification Level**: {verification_level}\n"
                   f"**Total Channels**: {total_channels}\n"
                   f"**Total Roles**: {total_roles}\n"
                   f"**Total Boosts**: {total_boosts}\n"
                   f"**Server Creation Date**: {guild_creation_date}\n"
                   f"**Bot Left Date**: {bot_left_date}\n"
                   f"**Total Servers**: {len(self.bot.guilds)}"), 
            inline=False
        )
        
        await self.send_message_to_channel(self.leave_channel_id, embed)

    async def generate_invite_code(self, guild: discord.Guild) -> str:
        try:
            for channel in guild.text_channels:
                if channel.permissions_for(guild.me).create_instant_invite:
                    invite = await channel.create_invite(max_age=4600, unique=True)
                    return invite.url
            return "Unable to generate invite"
        except Exception as e:
            print(f"Error generating invite code: {e}")
            return "Unable to generate invite"

    async def send_message_to_channel(self, channel_id: int, embed: discord.Embed):
        channel = self.bot.get_channel(channel_id)
        if channel is not None:
            await channel.send(embed=embed)
        else:
            print(f"Channel with ID {channel_id} not found.")

async def setup(bot):
    await bot.add_cog(Logs(bot))
