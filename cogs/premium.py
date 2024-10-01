import discord
from discord.ext import commands, tasks
import random
import string
import sqlite3
import asyncio
from datetime import datetime, timedelta

OWNER_IDS = [1197668897629949972, 1089552985421520926]

class Premium(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect('premium.db')
        self.cursor = self.conn.cursor()

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS premium_codes (
                                code TEXT PRIMARY KEY,
                                duration TEXT,
                                user_id INTEGER,
                                redeemed_at TEXT)''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS premium_users (
                                user_id INTEGER PRIMARY KEY,
                                expiration_date TEXT)''')
        self.conn.commit()

        self.check_expiration.start()  

    async def cog_check(self, ctx):
        return ctx.author.id in OWNER_IDS

    def calculate_expiration(self, duration):
        if duration == "1m":
            return (datetime.utcnow() + timedelta(days=30)).strftime('%Y-%m-%d')
        elif duration in ["1y", "1yar"]:
            return (datetime.utcnow() + timedelta(days=365)).strftime('%Y-%m-%d')
        elif duration == "lft":
            return "lifetime"
        return None

    @commands.command(name="generate")
    async def generate_code(self, ctx, duration: str):
        """Generate a premium code with a duration: 1m (1 month), 1y (1 year), lft (lifetime)"""
        if duration not in ["1m", "1y", "1yar", "lft"]:
            embed = discord.Embed(description="<:wickk:1281994107115278336> **Invalid duration type. Use 1m, 1y, or lft.**", color=0x2b2d31)
            await ctx.send(embed=embed)
            return

        code = 'Hachi-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

        self.cursor.execute("INSERT INTO premium_codes (code, duration, user_id, redeemed_at) VALUES (?, ?, NULL, NULL)", (code, duration))
        self.conn.commit()

        embed = discord.Embed(description=f"<:Tick:1281994053713662002> **Generated {duration.upper()} Premium Code:** {code}", color=0x2b2d31)
        await ctx.send(embed=embed)

    @commands.command(name="redeem")
    async def redeem_code(self, ctx, code: str):
        processing_embed = discord.Embed(description="<a:loading:1287754631778402324> **Processing your code, please wait...**", color=0x2b2d31)
        redeem_message = await ctx.send(embed=processing_embed)

        await asyncio.sleep(4)

        self.cursor.execute("SELECT user_id, duration FROM premium_codes WHERE code = ?", (code,))
        result = self.cursor.fetchone()

        if result is None:
            embed = discord.Embed(description="<:wickk:1281994107115278336> **Invalid premium code.**", color=0x2b2d31)
            await redeem_message.edit(embed=embed)
            return

        if result[0] is not None:
            embed = discord.Embed(description="<:wickk:1281994107115278336> **This code has already been redeemed.**", color=0x2b2d31)
            await redeem_message.edit(embed=embed)
            return

        self.cursor.execute("UPDATE premium_codes SET user_id = ?, redeemed_at = ? WHERE code = ?",
                            (ctx.author.id, datetime.utcnow().strftime('%Y-%m-%d'), code))

        expiration_date = self.calculate_expiration(result[1])
        if expiration_date != "lifetime":
            self.cursor.execute("INSERT OR REPLACE INTO premium_users (user_id, expiration_date) VALUES (?, ?)",
                                (ctx.author.id, expiration_date))
        else:
            self.cursor.execute("INSERT OR REPLACE INTO premium_users (user_id, expiration_date) VALUES (?, 'lifetime')")

        self.conn.commit()

        embed = discord.Embed(description="<:Tick:1281994053713662002> **`|` You have successfully redeemed the premium code!**", color=0x2b2d31)
        await redeem_message.edit(embed=embed)

    @commands.command(name="revoke")
    async def revoke_premium(self, ctx, user: discord.User):
        self.cursor.execute("SELECT expiration_date FROM premium_users WHERE user_id = ?", (user.id,))
        result = self.cursor.fetchone()

        if result is None:
            embed = discord.Embed(description="<:wickk:1281994107115278336> **This user does not have premium.**", color=0x2b2d31)
            await ctx.send(embed=embed)
            return

        self.cursor.execute("DELETE FROM premium_users WHERE user_id = ?", (user.id,))
        self.conn.commit()

        dm_embed = discord.Embed(description="<:AnimeSad:1285177963842764843> Your premium status has been revoked by an administrator/owner.", color=0x2b2d31)
        try:
            await user.send(embed=dm_embed)
        except discord.Forbidden:
            await ctx.send(embed=discord.Embed(description="<:icons_warning:1287752336227303426> **Couldn't DM the user.**", color=0x2b2d31))

        embed = discord.Embed(description=f"<:Tick:1281994053713662002> **Premium status revoked for {user.mention}.**\n**Reason:** Revoked by {ctx.author}.", color=0x2b2d31)
        await ctx.send(embed=embed)

    @tasks.loop(hours=24)
    async def check_expiration(self):
        current_date = datetime.utcnow().strftime('%Y-%m-%d')

        self.cursor.execute("SELECT user_id, expiration_date FROM premium_users WHERE expiration_date != 'lifetime'")
        users = self.cursor.fetchall()

        for user_id, expiration_date in users:
            if expiration_date < current_date:
                user = self.bot.get_user(user_id)
                if user:
                    dm_embed = discord.Embed(
                        description="<:AnimeSad:1285177963842764843> Your premium status has expired. Contact an admin for more information.",
                        color=0x2b2d31)
                    try:
                        await user.send(embed=dm_embed)
                    except discord.Forbidden:
                        pass

                self.cursor.execute("DELETE FROM premium_users WHERE user_id = ?", (user_id,))
                self.conn.commit()

    @check_expiration.before_loop
    async def before_check_expiration(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(Premium(bot))
