import discord
from discord.ext import commands
from pymongo import MongoClient
import asyncio

class ServerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.mongo_uri = 'mongodb+srv://SpaceMusic:shivamop@cluster0.kgvij.mongodb.net/myFirstDatabase?retryWrites=true&w=majority'
        self.client = MongoClient(self.mongo_uri)
        self.db = self.client['discord_bot']
        self.autoroles_collection = self.db['autoroles']
        self.settings_collection = self.db['settings']

    async def check_permissions(self, ctx, permissions):
        if ctx.author.guild_permissions.administrator:
            return True

        missing_permissions = [
            perm.replace('_', ' ').title()
            for perm, has_perm in permissions.items() if not has_perm
        ]
        if missing_permissions:
            embed = discord.Embed(
                description=f"<:wickk:1281994107115278336> {ctx.author.mention}: You are missing the following permissions to run this command:\n" + "\n".join(missing_permissions),
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed)
            return False
        return True

    @commands.group(aliases=['guild'], invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    async def server(self, ctx):
        embed = discord.Embed(
            description="Use the following subcommands to manage the server:",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="Commands:",
            value="`?server setname <new name>`\n`?server seticon <image URL>`\n`?autoroles add <@role>`\n`?autoroles remove <@role>`\n`?autoroles list`\n`?pingonjoin enable | disable`",
            inline=False
        )
        embed.set_footer(text="[optional] • <required>")
        await ctx.send(embed=embed)

    @server.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.has_permissions(manage_guild=True)
    async def seticon(self, ctx, link: str):
        permissions = ctx.guild.me.guild_permissions
        if not await self.check_permissions(ctx, permissions):
            return

        try:
            async with self.bot.session.get(link) as response:
                if response.status != 200:
                    embed = discord.Embed(
                        description="<:wickk:1281994107115278336> Couldn't retrieve the image. Please ensure the URL is correct.",
                        color=discord.Color.blue()
                    )
                    return await ctx.send(embed=embed)
                
                data = await response.read()

            await ctx.guild.edit(icon=data)
            embed = discord.Embed(
                description=f"<:Tick:1281994053713662002> {ctx.author.mention}: The server icon has been successfully updated.",
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                description=f"<:wickk:1281994107115278336> An error occurred while changing the icon: {e}",
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed)

    @server.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.has_permissions(manage_guild=True)
    async def setname(self, ctx, *, name: str):
        permissions = ctx.guild.me.guild_permissions
        if not await self.check_permissions(ctx, permissions):
            return

        try:
            await ctx.guild.edit(name=name)
            embed = discord.Embed(
                description=f"<:Tick:1281994053713662002> {ctx.author.mention}: The server name has been successfully changed to `{name}`.",
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                description=f"<:wickk:1281994107115278336> An error occurred while changing the server name: {e}",
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed)

    @commands.group(invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    async def autoroles(self, ctx):
        permissions = ctx.guild.me.guild_permissions
        if not await self.check_permissions(ctx, permissions):
            return

        embed = discord.Embed(
            description="Use the following subcommands to manage autoroles:",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="Commands:",
            value="`?autoroles add <@role>`\n`?autoroles remove <@role>`\n`?autoroles list`",
            inline=False
        )
        embed.set_footer(text="[optional] • <required>")
        await ctx.send(embed=embed)

    @autoroles.command()
    @commands.has_permissions(manage_guild=True)
    async def add(self, ctx, role: discord.Role):
        permissions = ctx.guild.me.guild_permissions
        if not await self.check_permissions(ctx, permissions):
            return

        guild_id = str(ctx.guild.id)
        self.autoroles_collection.update_one(
            {"guild_id": guild_id},
            {"$addToSet": {"roles": role.id}},
            upsert=True
        )
        embed = discord.Embed(
            description=f"<:Tick:1281994053713662002> {ctx.author.mention}: The role **{role.name}** has been added to the autoroles list.",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)

    @autoroles.command()
    @commands.has_permissions(manage_guild=True)
    async def remove(self, ctx, role: discord.Role):
        permissions = ctx.guild.me.guild_permissions
        if not await self.check_permissions(ctx, permissions):
            return

        guild_id = str(ctx.guild.id)
        result = self.autoroles_collection.update_one(
            {"guild_id": guild_id},
            {"$pull": {"roles": role.id}}
        )
        if result.modified_count > 0:
            embed = discord.Embed(
                description=f"<:Tick:1281994053713662002> {ctx.author.mention}: The role **{role.name}** has been removed from the autoroles list.",
                color=discord.Color.blue()
            )
        else:
            embed = discord.Embed(
                description=f"<:wickk:1281994107115278336> {ctx.author.mention}: The role **{role.name}** was not found in the autoroles list.",
                color=discord.Color.blue()
            )
        await ctx.send(embed=embed)

    @autoroles.command()
    async def list(self, ctx):
        permissions = ctx.guild.me.guild_permissions
        if not await self.check_permissions(ctx, permissions):
            return

        guild_id = str(ctx.guild.id)
        result = self.autoroles_collection.find_one({"guild_id": guild_id})
        if result and "roles" in result:
            roles = result["roles"]
            roles_list = "\n".join([f"<@&{role_id}>" for role_id in roles])
            embed = discord.Embed(
                description=roles_list,
                color=discord.Color.blue()
            )
        else:
            embed = discord.Embed(
                description=f"<:wickk:1281994107115278336> {ctx.author.mention}: No roles are currently in the autoroles list.",
                color=discord.Color.blue()
            )
        await ctx.send(embed=embed)

    @commands.group(invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    async def pingonjoin(self, ctx):
        permissions = ctx.guild.me.guild_permissions
        if not await self.check_permissions(ctx, permissions):
            return

        embed = discord.Embed(
            description="Use the following subcommands to manage ping notifications on member join:",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="Commands:",
            value="`?pingonjoin enable <#channel>` to enable notifications in a specified channel\n`?pingonjoin disable` to disable notifications",
            inline=False
        )
        embed.set_footer(text="[optional] • <required>")
        await ctx.send(embed=embed)

    @pingonjoin.command()
    @commands.has_permissions(manage_guild=True)
    async def enable(self, ctx, channel: discord.TextChannel):
        permissions = ctx.guild.me.guild_permissions
        if not await self.check_permissions(ctx, permissions):
            return

        guild_id = str(ctx.guild.id)
        self.settings_collection.update_one(
            {"guild_id": guild_id},
            {"$set": {"pingonjoin": True, "pingonjoin_channel": channel.id}},
            upsert=True
        )
        embed = discord.Embed(
            description=f"<:Tick:1281994053713662002> {ctx.author.mention}: Ping notifications on member join have been enabled in {channel.mention}.",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)

    @pingonjoin.command()
    @commands.has_permissions(manage_guild=True)
    async def disable(self, ctx):
        permissions = ctx.guild.me.guild_permissions
        if not await self.check_permissions(ctx, permissions):
            return

        guild_id = str(ctx.guild.id)
        self.settings_collection.update_one(
            {"guild_id": guild_id},
            {"$set": {"pingonjoin": False, "pingonjoin_channel": None}},
            upsert=True
        )
        embed = discord.Embed(
            description=f"<:Tick:1281994053713662002> {ctx.author.mention}: Ping notifications on member join have been disabled.",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild_id = str(member.guild.id)
        
        result = self.autoroles_collection.find_one({"guild_id": guild_id})
        if result and "roles" in result:
            roles = result["roles"]
            roles_to_add = [discord.Object(id=role_id) for role_id in roles]
            await member.add_roles(*roles_to_add, reason="Assigned by autoroles system")

        settings = self.settings_collection.find_one({"guild_id": guild_id})
        if settings and settings.get("pingonjoin", False):
            channel_id = settings.get("pingonjoin_channel")
            if channel_id:
                channel = member.guild.get_channel(channel_id)
                if channel:
                    message = await channel.send(f"Welcome {member.mention}! 🎉 Enjoy your stay!")
                    await asyncio.sleep(6)
                    await message.delete()

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def picperms(self, ctx, user: discord.User = None):
        permissions = ctx.guild.me.guild_permissions
        if not await self.check_permissions(ctx, permissions):
            return

        if not isinstance(ctx.channel, discord.TextChannel):
            embed = discord.Embed(
                description="<:wickk:1281994107115278336> This command can only be used in a text channel.",
                color=discord.Color.blue()
            )
            return await ctx.send(embed=embed)

        if user is None:
            embed = discord.Embed(
                description="<:wickk:1281994107115278336> Usage: `?picperms <@user>`\nGrant media permissions to the mentioned user in this channel.",
                color=discord.Color.blue()
            )
            return await ctx.send(embed=embed)

        overwrite = discord.PermissionOverwrite()
        overwrite.attach_files = True
        overwrite.embed_links = True

        try:
            await ctx.channel.set_permissions(user, overwrite=overwrite)
            embed = discord.Embed(
                description=f"<:Tick:1281994053713662002> {ctx.author.mention}: **Media permissions** have been granted to {user.mention} in this channel.",
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                description=f"<:wickk:1281994107115278336> An error occurred while granting permissions: {e}",
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ServerCog(bot))
