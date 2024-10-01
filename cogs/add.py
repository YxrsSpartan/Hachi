import discord
from discord.ext import commands
from discord.ui import Button, View

class AddCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        owner = guild.owner

        support_button = Button(label="Support Server", url="https://discord.gg/mizubee")
        premium_button = Button(label="Get Premium", url="https://discord.gg/mizubee")

        view = View()
        view.add_item(support_button)
        view.add_item(premium_button)

        embed = discord.Embed(
            title="**<:happy_anime:1285165828777447555> Thank you for choosing Hachi!**",
            description=(
                "<:f_daisy:1285167699319848962> `Hachi` has been successfully added to your server.\n\n"
                "<:f_daisy:1285167699319848962> You can report any issues at my **[Support Server](https://discord.gg/mizubee)** following the needed steps. "
                "<:f_daisy:1285167699319848962> You can also reach out to my **Developers** if you want to know more about me."
            ),
            color=0x2b2d31  
        )
        
        try:
            await owner.send(embed=embed, view=view)
        except discord.Forbidden:
            print(f"Could not send message to {owner} in guild {guild.name}.")
        except Exception as e:
            print(f"An error occurred: {e}")

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} cog is ready!")

async def setup(bot):
    await bot.add_cog(AddCog(bot))
