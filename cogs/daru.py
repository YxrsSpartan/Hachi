import discord
from discord.ext import commands
from discord.ui import Button, View
import asyncio

class BotListPaginator(View):
    def __init__(self, bots, ctx, bot):
        super().__init__()
        self.bots = bots
        self.ctx = ctx
        self.bot = bot  
        self.page = 0
        self.per_page = 10
        self.original_user = ctx.author
        self.disable_after = 60  

        self.bot.loop.create_task(self.disable_buttons_after_delay())

    def get_embed(self):
        start = self.page * self.per_page
        end = start + self.per_page
        bots_to_show = self.bots[start:end]
        
        description = '\n'.join(f'{i + 1}. {bot.mention}' for i, bot in enumerate(bots_to_show, start=start))
        total_pages = (len(self.bots) + self.per_page - 1) // self.per_page
        
        embed = discord.Embed(
            title=f'Bots in {self.ctx.guild.name}',
            description=description,
            color=0x2b2d31
        )
        embed.set_footer(text=f"Page {self.page + 1} of {total_pages} | Total bots: {len(self.bots)}")
        return embed

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.secondary, disabled=True)
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.original_user:
            await interaction.response.send_message("You are not allowed to use this button.", ephemeral=True)
            return
        
        if self.page > 0:
            self.page -= 1
            await self.update_buttons()
            await interaction.response.edit_message(embed=self.get_embed(), view=self)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.secondary)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.original_user:
            await interaction.response.send_message("You are not allowed to use this button.", ephemeral=True)
            return
        
        if (self.page + 1) * self.per_page < len(self.bots):
            self.page += 1
            await self.update_buttons()
            await interaction.response.edit_message(embed=self.get_embed(), view=self)

    async def update_buttons(self):
        self.previous.disabled = self.page == 0
        self.next.disabled = (self.page + 1) * self.per_page >= len(self.bots)
        await self.message.edit(view=self)

    async def disable_buttons_after_delay(self):
        await asyncio.sleep(self.disable_after)
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)

class BotList(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(manage_guild=True)  
    async def bots(self, ctx):
        bots = [member for member in ctx.guild.members if member.bot]
        paginator = BotListPaginator(bots, ctx, self.bot)  
        embed = paginator.get_embed()
        message = await ctx.send(embed=embed, view=paginator)
        paginator.message = message

    @bots.error
    async def bots_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                description=f"<:wickk:1281994107115278336> {ctx.author.mention}: You need the **Manage Server** permission to use this command.",
                color=0x2b2d31
            )
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(BotList(bot))
