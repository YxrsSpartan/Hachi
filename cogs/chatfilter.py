import discord
from discord.ext import commands
import aiosqlite

db_file = 'chatfilter.db'

class ChatFilter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.initialize_db())

    async def initialize_db(self):
        async with aiosqlite.connect(db_file) as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS chatfilter (
                    trigger TEXT NOT NULL,
                    guild INTEGER NOT NULL
                )
            """)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS bypass_users (
                    user_id INTEGER NOT NULL,
                    guild INTEGER NOT NULL
                )
            """)
            await conn.commit()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or message.author.guild_permissions.administrator:
            return
        
        async with aiosqlite.connect(db_file) as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT 1 FROM bypass_users WHERE user_id = ? AND guild = ?", (message.author.id, message.guild.id))
                bypass_user = await cursor.fetchone()
                
                if bypass_user:
                    return  

                await cursor.execute("SELECT trigger FROM chatfilter WHERE guild = ?", (message.guild.id,))
                data = await cursor.fetchall()
                if data:
                    for row in data:
                        trigger = row[0]
                        if trigger.lower() in message.content.lower():
                            await message.delete()
                            embed = discord.Embed(
                                color=0x2b2d31,
                                description=f"> 🚫 {message.author.mention}: That word is not allowed here."
                            )
                            await message.channel.send(embed=embed, delete_after=2)

    async def send_permission_error(self, ctx):
        embed = discord.Embed(
            color=0x2b2d31,
            description=f"> 🚫 {ctx.author.mention}, you need the `Manage Messages` permission to use this command."
        )
        await ctx.send(embed=embed)

    @commands.group(invoke_without_command=True)
    async def chatfilter(self, ctx):
        embed = discord.Embed(
            description="Manage blacklisted words and bypass users.",
            color=0x2b2d31
        )
        embed.add_field(name="Usage", value="```Syntax: ?chatfilter add <word>\nSyntax: ?chatfilter clear\nSyntax: ?chatfilter show\nSyntax: ?chatfilter bypass add <@user>\nSyntax: ?chatfilter bypass remove <@user>\nSyntax: ?chatfilter bypass show```", inline=False)
        await ctx.send(embed=embed)

    @chatfilter.command()
    async def add(self, ctx, *, trigger):
        if not ctx.author.guild_permissions.manage_messages:
            await self.send_permission_error(ctx)
            return
        async with aiosqlite.connect(db_file) as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("INSERT INTO chatfilter (trigger, guild) VALUES (?, ?)", (trigger, ctx.guild.id))
                await conn.commit()
            embed = discord.Embed(
                description=f"> ✅ {ctx.author.mention}: Successfully added `{trigger}` to the filter.",
                color=0x2b2d31
            )
            await ctx.send(embed=embed)

    @chatfilter.command()
    async def clear(self, ctx):
        if not ctx.author.guild_permissions.manage_messages:
            await self.send_permission_error(ctx)
            return
        async with aiosqlite.connect(db_file) as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("DELETE FROM chatfilter WHERE guild = ?", (ctx.guild.id,))
                await conn.commit()
            embed = discord.Embed(
                description=f"> ✅ {ctx.author.mention}: Successfully cleared all blacklisted words.",
                color=0x2b2d31
            )
            await ctx.send(embed=embed)

    @chatfilter.command()
    async def show(self, ctx):
        if not ctx.author.guild_permissions.manage_messages:
            await self.send_permission_error(ctx)
            return
        async with aiosqlite.connect(db_file) as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT trigger FROM chatfilter WHERE guild = ?", (ctx.guild.id,))
                data = await cursor.fetchall()
                if data:
                    word_list = "\n".join([f"`{idx + 1}` {row[0]}" for idx, row in enumerate(data)])
                    embed = discord.Embed(
                        description=word_list,
                        color=0x2b2d31
                    )
                    embed.set_author(name="Blacklisted Words", icon_url=ctx.author.display_avatar.url)
                    await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(
                        description=f"{ctx.author.mention}, no words are currently blacklisted.",
                        color=0x2b2d31
                    )
                    await ctx.send(embed=embed)

    @chatfilter.group(name="bypass", invoke_without_command=True)
    async def bypass(self, ctx):
        embed = discord.Embed(
            description="Manage bypass users for blacklisted words.",
            color=0x2b2d31
        )
        embed.add_field(name="Usage", value="```Syntax: ?chatfilter bypass add <@user>\nSyntax: ?chatfilter bypass remove <@user>\nSyntax: ?chatfilter bypass show```", inline=False)
        await ctx.send(embed=embed)

    @bypass.command(name="add")
    async def bypass_add(self, ctx, user: discord.Member):
        if not ctx.author.guild_permissions.manage_messages:
            await self.send_permission_error(ctx)
            return
        async with aiosqlite.connect(db_file) as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("INSERT INTO bypass_users (user_id, guild) VALUES (?, ?)", (user.id, ctx.guild.id))
                await conn.commit()
            embed = discord.Embed(
                description=f"> ✅ {ctx.author.mention}: `{user.display_name}` can now bypass the filter.",
                color=0x2b2d31
            )
            await ctx.send(embed=embed)

    @bypass.command(name="remove")
    async def bypass_remove(self, ctx, user: discord.Member):
        if not ctx.author.guild_permissions.manage_messages:
            await self.send_permission_error(ctx)
            return
        async with aiosqlite.connect(db_file) as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("DELETE FROM bypass_users WHERE user_id = ? AND guild = ?", (user.id, ctx.guild.id))
                await conn.commit()
            embed = discord.Embed(
                description=f"> ✅ {ctx.author.mention}: `{user.display_name}` can no longer bypass the filter.",
                color=0x2b2d31
            )
            await ctx.send(embed=embed)

    @bypass.command(name="show")
    async def bypass_show(self, ctx):
        if not ctx.author.guild_permissions.manage_messages:
            await self.send_permission_error(ctx)
            return
        async with aiosqlite.connect(db_file) as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT user_id FROM bypass_users WHERE guild = ?", (ctx.guild.id,))
                data = await cursor.fetchall()
                if data:
                    users = "\n".join([f"<@{row[0]}>" for row in data])
                    embed = discord.Embed(
                        description=f"Bypass Users:\n{users}",
                        color=0x2b2d31
                    )
                    await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(
                        description=f"No users are currently bypassing the filter.",
                        color=0x2b2d31
                    )
                    await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ChatFilter(bot))
