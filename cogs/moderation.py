import sqlite3
import discord
from discord.ext import commands
from discord import Embed
from discord.ext.commands import has_permissions, CheckFailure

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect('moderation.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS vc_bans (user_id INTEGER, notified INTEGER DEFAULT 0)''')
        self.conn.commit()

    def is_user_banned(self, user_id):
        self.cursor.execute('SELECT * FROM vc_bans WHERE user_id = ?', (user_id,))
        return self.cursor.fetchone() is not None

    def ban_user(self, user_id):
        if not self.is_user_banned(user_id):
            self.cursor.execute('INSERT INTO vc_bans (user_id, notified) VALUES (?, 0)', (user_id,))
            self.conn.commit()

    def unban_user(self, user_id):
        self.cursor.execute('DELETE FROM vc_bans WHERE user_id = ?', (user_id,))
        self.conn.commit()

    def has_been_notified(self, user_id):
        self.cursor.execute('SELECT notified FROM vc_bans WHERE user_id = ?', (user_id,))
        result = self.cursor.fetchone()
        return result is not None and result[0] == 1

    def set_notified(self, user_id, notified=True):
        self.cursor.execute('UPDATE vc_bans SET notified = ? WHERE user_id = ?', (1 if notified else 0, user_id))
        self.conn.commit()

    @commands.group(invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 10, commands.BucketType.default)
    async def vc(self, ctx):
        embed = Embed(
            description="Use `vc ban` or `vc unban` commands for moderation.\n\nUsage:\n"
                        "`?vc ban <@user>`: **Ban** a user from the voice channels.\n"
                        "`?vc unban <@user>`: **Unban** a user from the voice channels.",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)

    @vc.command(name='ban')
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 10, commands.BucketType.default)
    async def vc_ban(self, ctx, member: discord.Member):
        self.ban_user(member.id)

        if member.voice:
            await member.edit(voice_channel=None)
            embed = Embed(
                description=f"**<:Tick:1281994053713662002> {member.mention} has been banned from all voice channels and disconnected.**",
                color=discord.Color.blue()
            )
        else:
            embed = Embed(
                description=f"**<:icons_warning:1287752336227303426> {member.mention} has been banned from all voice channels.**",
                color=discord.Color.blue()
            )
        await ctx.send(embed=embed)

    @vc.command(name='unban')
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 10, commands.BucketType.default)
    async def vc_unban(self, ctx, member: discord.Member):
        if self.is_user_banned(member.id):
            self.unban_user(member.id)
            embed = Embed(
                description=f"**<:Tick:1281994053713662002> {member.mention} has been unbanned from voice channels.**",
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed)

            try:
                await member.send(embed=Embed(
                    description=f"**<:Tick:1281994053713662002> {member.mention}, you have been unbanned from joining voice channels.**",
                    color=discord.Color.blue()
                ))
            except discord.Forbidden:
                pass
        else:
            embed = Embed(
                description=f"**{member.mention} is not banned from voice channels.**",
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if self.is_user_banned(member.id):
            if after.channel:  
                await member.edit(voice_channel=None)  
                if not self.has_been_notified(member.id):
                    embed = Embed(
                        description=f"**<:icons_warning:1287752336227303426> {member.mention}, you are banned from joining voice channels.**",
                        color=discord.Color.blue()
                    )
                    try:
                        await member.send(embed=embed)
                    except discord.Forbidden:
                        pass
                    self.set_notified(member.id, True)

    @commands.command()
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 10, commands.BucketType.default)
    async def deafen(self, ctx, member: discord.Member = None):
        if member is None:
            embed = Embed(
                description="**Usage:** `?deafen <@user>` to deafen a member in a voice channel.",
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed)
            return

        if member.voice and member.voice.channel:
            if not member.voice.deaf:
                await member.edit(deafen=True)
                embed = Embed(
                    description=f"**<:deafened:1288095279928836098> {member.mention} has been deafened in {member.voice.channel.name}.**",
                    color=discord.Color.blue()
                )
                await ctx.send(embed=embed)
            else:
                embed = Embed(
                    description=f"**{member.mention} is already deafened in {member.voice.channel.name}.**",
                    color=discord.Color.blue()
                )
                await ctx.send(embed=embed)
        else:
            embed = Embed(
                description=f"**{member.mention} is not in a voice channel.**",
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 10, commands.BucketType.default)
    async def undeafen(self, ctx, member: discord.Member = None):
        if member is None:
            embed = Embed(
                description="**Usage:** `?undeafen <@user>` to undeafen a member in a voice channel.",
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed)
            return

        if member.voice and member.voice.channel:
            if member.voice.deaf:
                await member.edit(deafen=False)
                embed = Embed(
                    description=f"**<:icon_2:1288095220738822205> {member.mention} has been undeafened in {member.voice.channel.name}.**",
                    color=discord.Color.blue()
                )
                await ctx.send(embed=embed)
            else:
                embed = Embed(
                    description=f"**{member.mention} is not deafened in {member.voice.channel.name}.**",
                    color=discord.Color.blue()
                )
                await ctx.send(embed=embed)
        else:
            embed = Embed(
                description=f"**{member.mention} is not in a voice channel.**",
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed)

    @vc_ban.error
    @vc_unban.error
    @deafen.error
    @undeafen.error
    async def permission_error(self, ctx, error):
        if isinstance(error, CheckFailure):
            embed = Embed(
                description="**<:icons_warning:1287752336227303426> You do not have the required permissions to run this command.**",
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            embed = Embed(
                description=f"**<:icons_warning:1287752336227303426> This command is on cooldown. Please try again in {round(error.retry_after, 1)} seconds.**",
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed)

    def cog_unload(self):
        self.conn.close()


async def setup(bot):
    await bot.add_cog(Moderation(bot))
