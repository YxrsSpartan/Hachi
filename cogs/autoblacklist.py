import discord
from discord.ext import commands
import aiosqlite
import aiohttp
import json
import time

class AutoBlacklist(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.blacklist_file = 'bl.db'
        self.owners = self.load_owners()
        self.command_usage = {}

        self.rate_limit = 12  
        self.rate_time = 5  
        self.log_channel_id = 1287081551137472552  

        self.bot.loop.create_task(self.initialize_db())
        self.bot.add_check(self.blacklist_check)

    async def initialize_db(self):
        async with aiosqlite.connect(self.blacklist_file) as conn:
            await conn.execute(""" 
                CREATE TABLE IF NOT EXISTS blacklisted_users (
                    user_id INTEGER PRIMARY KEY,
                    auto_blacklisted INTEGER DEFAULT 0
                )
            """)
            await conn.commit()

    def load_owners(self):
        """Loads the owner IDs from the config file."""
        try:
            with open('dv/blwoners.json', 'r') as f:
                config = json.load(f)
            return config.get('owners', [])
        except Exception as e:
            self.bot.loop.create_task(self.log_error(f"Error loading owners: {e}"))
            return []

    def is_owner(self, user_id):
        """Checks if the user is an owner."""
        return user_id in self.owners

    def track_command_usage(self, user_id):
        """Tracks command usage to detect spamming."""
        current_time = time.time()
        if user_id not in self.command_usage:
            self.command_usage[user_id] = []

        self.command_usage[user_id] = [timestamp for timestamp in self.command_usage[user_id] if current_time - timestamp < self.rate_time]
        self.command_usage[user_id].append(current_time)

        return len(self.command_usage[user_id]) > self.rate_limit

    async def blacklist_check(self, ctx):
        """Check to prevent blacklisted users from running commands."""
        user_id = ctx.author.id
        async with aiosqlite.connect(self.blacklist_file) as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT 1 FROM blacklisted_users WHERE user_id = ?", (user_id,))
                is_blacklisted = await cursor.fetchone()

                if is_blacklisted:
                    embed = discord.Embed(
                        description="<:Warning:1279036939999117412> **You are blacklisted from using the bot. Please join our [support](https://discord.gg/KretHCmdNZ) server to appeal.**",
                        color=0xD3D3D3
                    )
                    await ctx.send(embed=embed)
                    return False

                if self.track_command_usage(user_id) and not self.is_owner(user_id):
                    await cursor.execute("INSERT OR IGNORE INTO blacklisted_users (user_id, auto_blacklisted) VALUES (?, 1)", (user_id,))
                    await conn.commit()
                    embed = discord.Embed(
                        description=f"<:Warning:1279036939999117412> **{ctx.author.mention} has been auto-blacklisted for spamming commands.**",
                        color=0x2b2d31
                    )
                    await ctx.send(embed=embed)
                    await self.log_auto_blacklist(ctx.author)
                    return False

        return True

    async def log_auto_blacklist(self, user):
        """Logs auto-blacklist actions to a specific channel."""
        log_channel = self.bot.get_channel(self.log_channel_id)
        if log_channel:
            embed = discord.Embed(
                description=f"**{user}** has been auto-blacklisted for spamming commands.",
                color=0xD3D3D3
            )
            await log_channel.send(embed=embed)

    async def log_error(self, message):
        """Logs errors to a specific channel."""
        log_channel = self.bot.get_channel(self.log_channel_id)
        if log_channel:
            embed = discord.Embed(
                description=message,
                color=0xD3D3D3
            )
            await log_channel.send(embed=embed)

    def owner_only():
        """A decorator to restrict a command to bot owners."""
        async def predicate(ctx):
            return ctx.author.id in ctx.cog.owners
        return commands.check(predicate)

    @commands.group(invoke_without_command=True)
    async def blacklist(self, ctx):
        """Manage the blacklist."""
        embed = discord.Embed(
            description="Manage the blacklist with the following commands:\n"
                        "```Syntax: ?blacklist add <@user>\n"
                        "Syntax: ?blacklist remove <@user>\n"
                        "Syntax: ?blacklist list\n"
                        "Syntax: ?blacklist clear```",
            color=0xD3D3D3
        )
        await ctx.send(embed=embed)

    @blacklist.command()
    @owner_only()
    async def add(self, ctx, user: discord.Member):
        async with aiosqlite.connect(self.blacklist_file) as conn:
            await conn.execute("INSERT OR IGNORE INTO blacklisted_users (user_id) VALUES (?)", (user.id,))
            await conn.commit()
        embed = discord.Embed(
            description=f"> ✅ {ctx.author.mention}: `{user.display_name}` has been added to the blacklist.",
            color=0x2b2d31
        )
        await ctx.send(embed=embed)

    @blacklist.command()
    @owner_only()
    async def remove(self, ctx, user: discord.Member):
        async with aiosqlite.connect(self.blacklist_file) as conn:
            await conn.execute("DELETE FROM blacklisted_users WHERE user_id = ?", (user.id,))
            await conn.commit()
        embed = discord.Embed(
            description=f"> ✅ {ctx.author.mention}: `{user.display_name}` has been removed from the blacklist.",
            color=0x2b2d31
        )
        await ctx.send(embed=embed)

    @blacklist.command()
    @owner_only()
    async def list(self, ctx):
        async with aiosqlite.connect(self.blacklist_file) as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT user_id FROM blacklisted_users")
                data = await cursor.fetchall()
                if data:
                    users = "\n".join([f"<@{row[0]}>" for row in data])
                    embed = discord.Embed(
                        description=f"Blacklisted Users:\n{users}",
                        color=0x2b2d31
                    )
                else:
                    embed = discord.Embed(
                        description="No users are currently blacklisted.",
                        color=0x2b2d31
                    )
                await ctx.send(embed=embed)

    @blacklist.command()
    @owner_only()
    async def clear(self, ctx):
        async with aiosqlite.connect(self.blacklist_file) as conn:
            await conn.execute("DELETE FROM blacklisted_users")
            await conn.commit()
        embed = discord.Embed(
            description=f"> ✅ {ctx.author.mention}: All users have been removed from the blacklist.",
            color=0x2b2d31
        )
        await ctx.send(embed=embed)

    def cog_unload(self):
        """Removes the global check when the cog is unloaded."""
        self.bot.remove_check(self.blacklist_check)

async def setup(bot):
    await bot.add_cog(AutoBlacklist(bot))
