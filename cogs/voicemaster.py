import discord
from discord.ext import commands
import aiosqlite
import asyncio
from .interface import VoiceMasterControlPanel  

db_file = 'voicemaster.db'

async def init_db():
    """Initialize the SQLite database asynchronously."""
    async with aiosqlite.connect(db_file) as conn:
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS guilds (
                guild_id INTEGER PRIMARY KEY,
                setup BOOLEAN,
                category_id INTEGER,
                join_to_create_id INTEGER,
                duo_voice_channel_id INTEGER,
                trio_voice_channel_id INTEGER,
                text_channel_id INTEGER
            )
        ''')
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS temp_channels (
                user_id INTEGER PRIMARY KEY,
                channel_id INTEGER
            )
        ''')
        await conn.commit()

class VoiceMaster(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.temp_channels = {}
        self.control_panel = VoiceMasterControlPanel(self)
        self.bot.add_view(self.control_panel)
        self.bot.loop.create_task(self.load_data())  

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setup(self, ctx):
        guild_id = ctx.guild.id

        async with aiosqlite.connect(db_file) as conn:
            async with conn.execute('SELECT * FROM guilds WHERE guild_id = ?', (guild_id,)) as cursor:
                guild_data = await cursor.fetchone()

        if guild_data:
            setup_embed = discord.Embed(
                description="<:eei_anime_CuteHug1:1285229214756507759> **VoiceMaster is already enabled in this server. "
                            "Use the button below to reset the setup.**",
                color=discord.Color.blue()
            )

            reset_button = discord.ui.Button(label="Reset Setup", style=discord.ButtonStyle.danger)

            async def reset_callback(interaction: discord.Interaction):
                await interaction.message.delete()
                await self.reset_setup(ctx.guild)
                await interaction.response.send_message("VoiceMaster setup has been reset.", ephemeral=True)

            reset_button.callback = reset_callback

            view = discord.ui.View()
            view.add_item(reset_button)

            await ctx.send(embed=setup_embed, view=view)
            return

        guild = ctx.guild

        setup_embed = discord.Embed(
            description="**Setting up VoiceMaster. Please wait...**",
            color=discord.Color.blue()
        )
        setup_message = await ctx.send(embed=setup_embed)

        setup_embed.description = "**Creating voice category...**"
        await setup_message.edit(embed=setup_embed)
        voice_category = await guild.create_category(name="Hachi")
        setup_embed.description = "**Voice category created.**"
        await setup_message.edit(embed=setup_embed)
        await asyncio.sleep(1)  

        setup_embed.description = "**Creating join-to-create voice channel...**"
        await setup_message.edit(embed=setup_embed)
        join_to_create = await voice_category.create_voice_channel(name="➕ Create Your VC", user_limit=1)
        setup_embed.description = "**Join-to-create voice channel created.**"
        await setup_message.edit(embed=setup_embed)
        await asyncio.sleep(1)

        setup_embed.description = "**Creating duo voice channel...**"
        await setup_message.edit(embed=setup_embed)
        duo_voice_channel = await voice_category.create_voice_channel(name="➕ Create Duo VC", user_limit=2)
        setup_embed.description = "**Duo voice channel created.**"
        await setup_message.edit(embed=setup_embed)
        await asyncio.sleep(1)

        setup_embed.description = "**Creating trio voice channel...**"
        await setup_message.edit(embed=setup_embed)
        trio_voice_channel = await voice_category.create_voice_channel(name="➕ Create Trio VC", user_limit=3)
        setup_embed.description = "**Trio voice channel created.**"
        await setup_message.edit(embed=setup_embed)
        await asyncio.sleep(1)

        setup_embed.description = "**Creating control text channel...**"
        await setup_message.edit(embed=setup_embed)
        text_channel = await voice_category.create_text_channel(name="Control")
        setup_embed.description = "**Control text channel created.**"
        await setup_message.edit(embed=setup_embed)
        await asyncio.sleep(1)

        setup_embed.description = "✅ **VoiceMaster setup complete.**"
        await setup_message.edit(embed=setup_embed)

        control_embed = discord.Embed(
            description="**Use the buttons below to manage your temporary voice channels.**",
            color=discord.Color.blue()
        )
        await text_channel.send(embed=control_embed, view=self.control_panel)

        async with aiosqlite.connect(db_file) as conn:
            await conn.execute('''
                INSERT OR REPLACE INTO guilds (guild_id, setup, category_id, join_to_create_id, duo_voice_channel_id, trio_voice_channel_id, text_channel_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                guild.id,
                True,
                voice_category.id,
                join_to_create.id,
                duo_voice_channel.id,
                trio_voice_channel.id,
                text_channel.id
            ))
            await conn.commit()

    @setup.error
    async def setup_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            no_perm_embed = discord.Embed(
                description="**You do not have the required permissions to use this command. You need the Administrator permission to run the setup command.**",
                color=discord.Color.blue()
            )
            await ctx.send(embed=no_perm_embed)

    async def reset_setup(self, guild):
        guild_id = guild.id

        async with aiosqlite.connect(db_file) as conn:
            async with conn.execute('SELECT * FROM guilds WHERE guild_id = ?', (guild_id,)) as cursor:
                guild_data = await cursor.fetchone()

        if not guild_data:
            return

        category_id = guild_data[2]
        text_channel_id = guild_data[6]

        system_channel = guild.system_channel
        if not system_channel:
            system_channel = guild.text_channels[0]

        status_embed = discord.Embed(
            description="**Starting the reset process. Please wait...**",
            color=discord.Color.blue()
        )
        status_message = await system_channel.send(embed=status_embed)

        category = discord.utils.get(guild.categories, id=category_id)
        if category:
            status_embed.description = "**Deleting channels in the category...**"
            await status_message.edit(embed=status_embed)
            for channel in category.channels:
                try:
                    await channel.delete()
                except discord.HTTPException as e:
                    await status_message.edit(
                        description=f"**Failed to delete channel {channel.name}: {e}**"
                    )
            status_embed.description = "**Category deleted.**"
            await status_message.edit(embed=status_embed)
            await asyncio.sleep(1)
            try:
                await category.delete()
            except discord.HTTPException as e:
                await status_message.edit(
                    description=f"**Failed to delete category: {e}**"
                )

        text_channel = guild.get_channel(text_channel_id)
        if text_channel:
            status_embed.description = "**Deleting control text channel...**"
            await status_message.edit(embed=status_embed)
            try:
                await text_channel.delete()
            except discord.HTTPException as e:
                await status_message.edit(
                    description=f"**Failed to delete text channel: {e}**"
                )

        async with aiosqlite.connect(db_file) as conn:
            await conn.execute('DELETE FROM guilds WHERE guild_id = ?', (guild_id,))
            await conn.execute('DELETE FROM temp_channels WHERE user_id IN (SELECT user_id FROM temp_channels)')
            await conn.commit()

        self.temp_channels = {}

        status_embed.description = "✅ **VoiceMaster setup has been reset.**"
        await status_message.edit(embed=status_embed)

    async def load_data(self):
        """Load existing temp channels from the database asynchronously."""
        await self.bot.wait_until_ready()  
        async with aiosqlite.connect(db_file) as conn:
            async with conn.execute('SELECT * FROM temp_channels') as cursor:
                rows = await cursor.fetchall()
                self.temp_channels = {user_id: channel_id for user_id, channel_id in rows}

    async def handle_join_to_create_channel(self, member, join_to_create_channel):
        """Handles the creation of a new temporary channel when a user joins the 'Create Your VC' channel."""
        temp_channel_id = self.temp_channels.get(member.id)
        if temp_channel_id:
            temp_channel = member.guild.get_channel(temp_channel_id)
            if temp_channel:
                try:
                    await temp_channel.delete()
                except discord.HTTPException:
                    pass
            async with aiosqlite.connect(db_file) as conn:
                await conn.execute('DELETE FROM temp_channels WHERE user_id = ?', (member.id,))
                await conn.commit()
            del self.temp_channels[member.id]

        temp_channel = await join_to_create_channel.category.create_voice_channel(
            name=f"VC {member.display_name}"
        )
        await member.move_to(temp_channel)
        self.temp_channels[member.id] = temp_channel.id

        async with aiosqlite.connect(db_file) as conn:
            await conn.execute('INSERT INTO temp_channels (user_id, channel_id) VALUES (?, ?)', (member.id, temp_channel.id))
            await conn.commit()

    async def handle_duo_create_channel(self, member, duo_voice_channel):
        """Handles the creation of a new temporary duo channel when a user joins the 'Create Duo VC' channel."""
        temp_channel_id = self.temp_channels.get(member.id)
        if temp_channel_id:
            temp_channel = member.guild.get_channel(temp_channel_id)
            if temp_channel:
                try:
                    await temp_channel.delete()
                except discord.HTTPException:
                    pass
            async with aiosqlite.connect(db_file) as conn:
                await conn.execute('DELETE FROM temp_channels WHERE user_id = ?', (member.id,))
                await conn.commit()
            del self.temp_channels[member.id]

        temp_channel = await duo_voice_channel.category.create_voice_channel(
            name=f"Duo VC {member.display_name}",
            user_limit=2
        )
        await member.move_to(temp_channel)
        self.temp_channels[member.id] = temp_channel.id

        async with aiosqlite.connect(db_file) as conn:
            await conn.execute('INSERT INTO temp_channels (user_id, channel_id) VALUES (?, ?)', (member.id, temp_channel.id))
            await conn.commit()

    async def handle_trio_create_channel(self, member, trio_voice_channel):
        """Handles the creation of a new temporary trio channel when a user joins the 'Create Trio VC' channel."""
        temp_channel_id = self.temp_channels.get(member.id)
        if temp_channel_id:
            temp_channel = member.guild.get_channel(temp_channel_id)
            if temp_channel:
                try:
                    await temp_channel.delete()
                except discord.HTTPException:
                    pass
            async with aiosqlite.connect(db_file) as conn:
                await conn.execute('DELETE FROM temp_channels WHERE user_id = ?', (member.id,))
                await conn.commit()
            del self.temp_channels[member.id]

        temp_channel = await trio_voice_channel.category.create_voice_channel(
            name=f"Trio VC {member.display_name}",
            user_limit=3
        )
        await member.move_to(temp_channel)
        self.temp_channels[member.id] = temp_channel.id

        async with aiosqlite.connect(db_file) as conn:
            await conn.execute('INSERT INTO temp_channels (user_id, channel_id) VALUES (?, ?)', (member.id, temp_channel.id))
            await conn.commit()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        guild = member.guild
        guild_id = guild.id

        async with aiosqlite.connect(db_file) as conn:
            async with conn.execute('SELECT * FROM guilds WHERE guild_id = ?', (guild_id,)) as cursor:
                guild_data = await cursor.fetchone()

        if not guild_data:
            return

        join_to_create_id = guild_data[3]
        duo_voice_channel_id = guild_data[4]
        trio_voice_channel_id = guild_data[5]

        if after.channel and after.channel.id == join_to_create_id:
            await self.handle_join_to_create_channel(member, after.channel)

        elif after.channel and after.channel.id == duo_voice_channel_id:
            await self.handle_duo_create_channel(member, after.channel)

        elif after.channel and after.channel.id == trio_voice_channel_id:
            await self.handle_trio_create_channel(member, after.channel)

        if before.channel:
            temp_channel_id = self.temp_channels.get(member.id)
            if temp_channel_id and before.channel.id == temp_channel_id:
                temp_channel = guild.get_channel(temp_channel_id)
                if temp_channel:
                    if len(temp_channel.members) == 0 or (len(temp_channel.members) == 1 and temp_channel.members[0].bot):
                        try:
                            await temp_channel.delete()
                        except discord.HTTPException:
                            pass

                        async with aiosqlite.connect(db_file) as conn:
                            await conn.execute('DELETE FROM temp_channels WHERE user_id = ?', (member.id,))
                            await conn.commit()

                        del self.temp_channels[member.id]

    async def cog_unload(self):
        """Ensure that the control panel is properly removed when the cog is unloaded."""
        self.bot.remove_view(self.control_panel)

async def setup(bot):
    await init_db() 
    await bot.add_cog(VoiceMaster(bot))
