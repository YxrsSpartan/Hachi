import discord
from discord.ext import commands
import asyncio

class RoleAssignment:
    def __init__(self):
        self.active = False
        self.guild = None
        self.role = None
        self.task = None
        self.progress = 0
        self.total_members = 0

role_assignment = RoleAssignment()

class Extra(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def send_cooldown_message(self, ctx, retry_after):
        embed = discord.Embed(
            description=f"> <a:cooldown:1287991046021709885> {ctx.author.mention}, please wait **{int(retry_after)}** seconds before using this command again.",
            color=0x2b2d31
        )
        await ctx.send(embed=embed)

    def create_progress_bar(self, current, total, length=20):
        progress = int(length * (current / total))
        bar = "█" * progress + "░" * (length - progress)
        return bar

    @commands.cooldown(1, 10, commands.BucketType.guild)
    @commands.has_permissions(manage_roles=True)
    @commands.command()
    async def roleall(self, ctx, role: discord.Role = None):
        if role is None:
            embed = discord.Embed(
                title="Invalid Usage",
                description=f"Please provide a role when using this command.\n"
                            f"**Usage:** `?roleall <@Role>`",
                color=0x2b2d31
            )
            await ctx.send(embed=embed)
            return

        if role_assignment.active:
            embed = discord.Embed(
                description=f"<:icons_warning:1287752336227303426> {ctx.author.mention}, a role assignment is already in progress.",
                color=0x2b2d31
            )
            await ctx.send(embed=embed)
            return

        role_assignment.active = True
        role_assignment.guild = ctx.guild
        role_assignment.role = role
        role_assignment.progress = 0


        members = ctx.guild.members
        role_assignment.total_members = len(members)

        embed = discord.Embed(
            title="Role Assignment Process",
            description=f"Assigning `{role.name}` to {role_assignment.total_members} members and bots...",
            color=0x2b2d31
        )
        embed.add_field(name="Progress", value=f"0/{role_assignment.total_members} (0.00%)\n{self.create_progress_bar(0, role_assignment.total_members)}")
        status_message = await ctx.send(embed=embed)

        for member in members:
            if not role_assignment.active:
                break
            try:
                await member.add_roles(role)
                role_assignment.progress += 1
            except Exception as e:
                print(f"Error assigning role to {member}: {e}")


            if role_assignment.progress % 10 == 0 or role_assignment.progress == role_assignment.total_members:
                progress_percentage = (role_assignment.progress / role_assignment.total_members) * 100
                progress_bar = self.create_progress_bar(role_assignment.progress, role_assignment.total_members)
                embed.set_field_at(0, name="Progress", value=f"{role_assignment.progress}/{role_assignment.total_members} ({progress_percentage:.2f}%)\n{progress_bar}")
                await status_message.edit(embed=embed)
                await asyncio.sleep(0.5)

        role_assignment.active = False

        embed.set_field_at(0, name="Progress", value=f"{role_assignment.total_members}/{role_assignment.total_members} (100%)\n{self.create_progress_bar(role_assignment.total_members, role_assignment.total_members)}")
        embed.description = f"<:Tick:1281994053713662002> Finished assigning `{role.name}` to all members and bots."
        await status_message.edit(embed=embed)

    @roleall.error
    async def roleall_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await self.send_cooldown_message(ctx, error.retry_after)
        elif isinstance(error, commands.MissingPermissions):
            await self.send_permission_error(ctx, error)

    @commands.group(invoke_without_command=True)
    @commands.has_permissions(manage_roles=True)
    async def role(self, ctx):
        embed = discord.Embed(
            description=f"<:settings:1287992160150360064> {ctx.author.mention}, please use `role status` or `role cancel`.",
            color=0x2b2d31
        )
        await ctx.send(embed=embed)

    @role.command(name="status")
    @commands.has_permissions(manage_roles=True)
    async def rolestatus(self, ctx):
        if not role_assignment.active:
            embed = discord.Embed(
                description=f"<:wickk:1281994107115278336> {ctx.author.mention}, no role assignment is in progress.",
                color=0x2b2d31
            )
            await ctx.send(embed=embed)
            return

        progress_percentage = (role_assignment.progress / role_assignment.total_members) * 100
        progress_bar = self.create_progress_bar(role_assignment.progress, role_assignment.total_members)
        embed = discord.Embed(
            title="Ongoing Role Assignment",
            description=f"Assigning `{role_assignment.role.name}`",
            color=0x2b2d31
        )
        embed.add_field(
            name="Progress",
            value=f"{role_assignment.progress}/{role_assignment.total_members} ({progress_percentage:.2f}%)\n{progress_bar}"
        )
        await ctx.send(embed=embed)

    @role.command(name="cancel")
    @commands.has_permissions(manage_roles=True)
    async def rolecancel(self, ctx):
        if not role_assignment.active:
            embed = discord.Embed(
                description=f"<:wickk:1281994107115278336> {ctx.author.mention}, no role assignment is in progress to cancel.",
                color=0x2b2d31
            )
            await ctx.send(embed=embed)
            return

        role_assignment.active = False
        embed = discord.Embed(
            description=f"<:icons_warning:1287752336227303426> {ctx.author.mention} has canceled the role assignment.",
            color=0x2b2d31
        )
        await ctx.send(embed=embed)

    async def send_permission_error(self, ctx, error):
        embed = discord.Embed(
            description=f"<:icons_warning:1287752336227303426> {ctx.author.mention}, you do not have the required permissions to run this command.\n"
                        f"Required permission: **{', '.join(error.missing_perms)}**.",
            color=0xe74c3c
        )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Extra(bot))
