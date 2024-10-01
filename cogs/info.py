import discord
from discord.ext import commands
import asyncio

class InfoCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["h"])
    async def help(self, ctx):
        await self.send_help_embed(ctx)

    async def send_help_embed(self, ctx):
        embed = discord.Embed(
            title="<:greetings:1285086779380076625> **Hachi Help**",
            description="**How to use**\nUse the dropdown menu below to see commands.",
            color=0x2b2d31  
        )
        
        embed.add_field(
            name="**Need support?**", 
            value="Join the **[support server](https://discord.gg/mizubee)** if you're stuck.", 
            inline=False
        )
        embed.add_field(
            name="**Additional info**",
            value="Anything in <> is required, [] is optional\n**[TOS](https://github.com/zeralysss/hachi/blob/main/Hachi%20Terms%20and%20Conditions) • [Privacy](https://github.com/zeralysss/hachi/blob/main/Hachi%20Privacy)**",
            inline=False
        )
        
        avatar_url = ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url
        embed.set_thumbnail(url=avatar_url)

        view = HelpDropdownView(ctx.author)
        message = await ctx.send(embed=embed, view=view)
        view.message = message

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user or message.author.bot:
            return

        if self.bot.user.mentioned_in(message) and "help" in message.content.lower():
            ctx = await self.bot.get_context(message)
            if ctx:
                await self.send_help_embed(ctx)

class HelpDropdownView(discord.ui.View):
    def __init__(self, user):
        super().__init__(timeout=60) 
        self.user = user
        self.message = None 
        self.add_item(HelpDropdown())

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user == self.user

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)

class HelpDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="General", value="general", description="General commands", emoji="<:B_9star_1blue:1285477060382556182>"),
            discord.SelectOption(label="Voicemaster", value="voicemaster", description="Voicemaster commands", emoji="<:B_9star_1blue:1285477060382556182>"),
            discord.SelectOption(label="Server", value="server", description="Server related commands", emoji="<:B_9star_1blue:1285477060382556182>"),
            discord.SelectOption(label="Extra", value="extra", description="Extra commands", emoji="<:B_9star_1blue:1285477060382556182>") 
        ]
        super().__init__(placeholder="Select a category", options=options)

    async def callback(self, interaction: discord.Interaction):
        category = self.values[0]
        commands_list = ""
        
        if category == "general":
            commands_list = (
                "**`Ping`**, **`Uptime`**, **`Banner`**, **`Avatar`**, **`Report`**, "
                "**`Stats`**, **`Invite`**, **`About`**, **`Vote`**, **`Profile`**, "
                "**`Rolelist`**, **`Shards`**"
            )
        elif category == "voicemaster":
            commands_list = (
                "**`Setup`**"
            )
        elif category == "server":
            commands_list = (
                "**`Server`**, **`Autoroles`**, **`Pingonjoin`**, **`Picperms`**, **`Bots`**, **`Botlink`**, **`Chatfilter`**, **`Ttt`**, "
                "**`Roleall`**, **`Role`**, **`Role Status`**, **`Role Cancel`**, **`Vc Ban`**, **`Vc Unban`**, **`Deafen`**, **`Undeafen`**"
            )
        elif category == "extra":  
            commands_list = (
                "**`Gay`**, **`Lesbo`**, **`Cute`**"
            )

        embed = discord.Embed(
            title=f"{category.capitalize()} Commands",
            description=commands_list,
            color=0x2b2d31  
        )
        
        avatar_url = interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url
        embed.set_footer(text=f"Requested by {interaction.user}", icon_url=avatar_url)
        
        await interaction.response.edit_message(embed=embed)

async def setup(bot):
    await bot.add_cog(InfoCog(bot))
