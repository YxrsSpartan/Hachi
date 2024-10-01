import discord
from discord.ext import commands
import asyncio
import os

class Paginator(discord.ui.View):
    def __init__(self, bot, pages, ctx, invoker):
        super().__init__(timeout=60)  
        self.bot = bot
        self.pages = pages
        self.ctx = ctx
        self.invoker = invoker
        self.current_page = 0

        self.prev_button = discord.ui.Button(label='Previous', style=discord.ButtonStyle.secondary, disabled=True)
        self.next_button = discord.ui.Button(label='Next', style=discord.ButtonStyle.secondary)

        self.prev_button.callback = self.prev_page
        self.next_button.callback = self.next_page

        self.add_item(self.prev_button)
        self.add_item(self.next_button)

    async def send_initial_message(self):
        self.message = await self.ctx.send(embed=self.pages[self.current_page], view=self)

    async def prev_page(self, interaction: discord.Interaction):
        if interaction.user.id != self.invoker:
            return await interaction.response.send_message("You cannot interact with this paginator.", ephemeral=True)

        if self.current_page > 0:
            self.current_page -= 1
            await self.message.edit(embed=self.pages[self.current_page])
            self.update_buttons()
            await interaction.response.defer()

    async def next_page(self, interaction: discord.Interaction):
        if interaction.user.id != self.invoker:
            return await interaction.response.send_message("You cannot interact with this paginator.", ephemeral=True)

        if self.current_page < len(self.pages) - 1:
            self.current_page += 1
            await self.message.edit(embed=self.pages[self.current_page])
            self.update_buttons()
            await interaction.response.defer()

    def update_buttons(self):
        self.prev_button.disabled = self.current_page == 0
        self.next_button.disabled = self.current_page == len(self.pages) - 1
        self.message.edit(view=self)

    async def start(self):
        await self.send_initial_message()

class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.owner_ids = {1197668897629949972, 1089552985421520926}  

    async def cog_check(self, ctx):
        return ctx.author.id in self.bot.owner_ids  

    async def confirmation(self, ctx, action: str):
        """Sends a confirmation message and waits for the owner's confirmation."""
        embed = discord.Embed(
            color=0x2b2d31,
            description=f"⚠️ **{action}** confirmation required! Type `yes` to confirm."
        )
        await ctx.send(embed=embed)

        def check(m):
            return m.author.id == ctx.author.id and m.content.lower() == 'yes'

        try:
            await self.bot.wait_for('message', check=check, timeout=15.0)
            return True
        except asyncio.TimeoutError:
            await ctx.send(embed=discord.Embed(color=0x2b2d31, description="Confirmation timed out."))
            return False

    @commands.command(aliases=["rl"])
    async def reloadall(self, ctx):
        """Reload all bot cogs."""
        await ctx.send(embed=discord.Embed(color=0x2b2d31, description="Reloading all cogs..."))
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                try:
                    await self.bot.reload_extension(f"cogs.{filename[:-3]}")
                except Exception as e:
                    await ctx.send(embed=discord.Embed(color=0x2b2d31, description=f"❌ Failed to reload `{filename}`: {e}"))
        await ctx.send(embed=discord.Embed(color=0x2b2d31, description="✅ All cogs reloaded successfully."))

    @commands.command()
    async def restart(self, ctx):
        """Restarts the bot with confirmation."""
        if await self.confirmation(ctx, "Bot restart"):
            await ctx.send(embed=discord.Embed(color=0x2b2d31, description="🔄 Restarting bot..."))
            await self.bot.close()  
            await asyncio.sleep(2)
            await self.bot.start(self.bot.token)

    @commands.command()
    async def shutdown(self, ctx):
        """Shuts down the bot with confirmation."""
        if await self.confirmation(ctx, "Bot shutdown"):
            await ctx.send(embed=discord.Embed(color=0x2b2d31, description="🔻 Shutting down bot..."))
            await self.bot.close()  

    @commands.command(aliases=["guilds"])
    async def servers(self, ctx):
        """Lists all servers the bot is in, paginated."""
        i = 0
        k = 1
        l = 0
        mes = ""
        number = []
        messages = []
        for guild in self.bot.guilds:
            mes += f"`{k}` **{guild.name}** ({guild.id}) - `{guild.member_count}` members\n"
            k += 1
            l += 1
            if l == 10:
                messages.append(mes)
                number.append(discord.Embed(color=0x2b2d31, description=messages[i]))
                i += 1
                mes = ""
                l = 0

        if mes:  
            messages.append(mes)
            number.append(discord.Embed(color=0x2b2d31, description=messages[i]))

        paginator = Paginator(self.bot, number, ctx, invoker=ctx.author.id)
        await paginator.start()

    @commands.command(aliases=["portal"])
    async def guild_invite(self, ctx, server_id: int):
        """Generates an invite link for the specified guild by ID."""
        guild = self.bot.get_guild(server_id)
        if not guild:
            return await ctx.send(embed=discord.Embed(color=0x2b2d31, description=f"❌ Could not find guild with ID {server_id}."))

        try:
            invite = await guild.text_channels[0].create_invite(max_age=400, max_uses=10)  
            await ctx.send(embed=discord.Embed(color=0x2b2d31, description=f"✅ Invite created: {invite.url}"))
        except Exception as e:
            await ctx.send(embed=discord.Embed(color=0x2b2d31, description=f"❌ Failed to create invite: {e}"))

    @commands.command(aliases=["gleave"])
    async def guild_leave(self, ctx, server_id: int):
        """Forces the bot to leave a guild by ID."""
        guild = self.bot.get_guild(server_id)
        if not guild:
            return await ctx.send(embed=discord.Embed(color=0x2b2d31, description=f"❌ Could not find guild with ID {server_id}."))

        if await self.confirmation(ctx, f"Leave guild {guild.name}"):
            await guild.leave()
            await ctx.send(embed=discord.Embed(color=0x2b2d31, description=f"✅ Left guild: {guild.name}"))

async def setup(bot):
    await bot.add_cog(Owner(bot))
