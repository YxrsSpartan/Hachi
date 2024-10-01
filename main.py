import discord
from discord.ext import commands
import aiohttp
import asyncio
import json

intents = discord.Intents.all()
intents.voice_states = True
intents.guilds = True

class MyBot(commands.AutoShardedBot):
    async def setup_hook(self):
        self.session = aiohttp.ClientSession()

    async def close(self):
        if self.session:
            await self.session.close()
        await super().close()


with open('owners.json', 'r') as f:
    owners_data = json.load(f)
owners = owners_data.get("owners", [])

bot = MyBot(command_prefix="", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    print(f'Connected to {len(bot.guilds)} servers')
    print(f'Running on {bot.shard_count} shards')

    bot.remove_command('help')


    for cog in ['voicemaster', 'utility', 'info', 'mention_listener', 'on_guild_join', 'command_logger', 
                'autoblacklist', 'osama', 'owner', 'server', 'add','shards', 'hachi', 'daru', 'gun', 
                'extrasmart', 'chatfilter', 'ttt', 'premium', 'np', 'role', 'moderation']:
        try:
            await bot.load_extension(f'cogs.{cog}')
            print(f"{cog.capitalize()} cog loaded successfully.")
        except Exception as e:
            print(f"Failed to load {cog.capitalize()} cog: {e}")


    try:
        await bot.load_extension('jishaku')
        print("Jishaku loaded successfully.")
    except Exception as e:
        print(f"Failed to load Jishaku: {e}")

    total_users = sum(guild.member_count for guild in bot.guilds)
    activity = discord.Activity(type=discord.ActivityType.watching, name=f"?help | @Hachi")
    await bot.change_presence(activity=activity, status=discord.Status.online)
    print(f'Bot status set to idle and activity set to watching ?help | @Hachi')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    else:
        print(f"Error: {error}")


def is_owner(ctx):
    return ctx.author.id in owners

@bot.check
async def check_jsk_access(ctx):
    if ctx.command and ctx.command.cog_name == "Jishaku":
        return is_owner(ctx)
    return True


@bot.command()
async def reload_owners(ctx):
    global owners
    with open('owners.json', 'r') as f:
        owners_data = json.load(f)
    owners = owners_data.get("owners", [])
    await ctx.send(f"Owners list reloaded. Current owners: {owners}")

async def main():
    async with bot:
        await bot.start('')  

if __name__ == "__main__":
    asyncio.run(main()) 