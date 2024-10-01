import discord
from discord.ext import commands

class ShardsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def shards(self, ctx):
        embed = discord.Embed(
            title=f"**<:3667af09b61803af507b5cd49edb95a9:1285481370495352923> {self.bot.user.name}'s Shards**",
            color=0x2b2d31
        )

        for shard_id, shard in self.bot.shards.items():
            latency = round(shard.latency * 1000, 2)
            guild_count = sum(1 for g in self.bot.guilds if g.shard_id == shard_id)
            member_count = sum(g.member_count for g in self.bot.guilds if g.shard_id == shard_id)

            embed.add_field(
                name=f"Shard {shard_id}",
                value=(
                    f"<:latency:1285480777894592605> {latency}ms\n"
                    f"<:white_Icon_Home_LOV:1285480973131321355> {guild_count} guilds\n"
                    f"<:white_members:1285481077489668117> {member_count} members"
                ),
                inline=True
            )

        shard_info = f"You are on shard {ctx.guild.shard_id}"
        embed.set_footer(text=f"{shard_info} • {discord.utils.format_dt(discord.utils.utcnow(), 'f')}")

        avatar_url = ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url
        embed.set_author(name=ctx.author.name, icon_url=avatar_url)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ShardsCog(bot))
