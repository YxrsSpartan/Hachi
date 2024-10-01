import discord
import time
from discord.ui import Button, View, Modal, TextInput

class VoiceMasterControlPanel(View):
    def __init__(self, cog):
        super().__init__(timeout=None)
        self.cog = cog
        self.last_interaction = {}

    async def user_owns_temp_channel(self, user):
        """Check if the user owns a temporary voice channel."""
        return user.id in self.cog.temp_channels

    async def send_error_message(self, interaction, message):
        await interaction.response.send_message(message, ephemeral=True)

    async def is_cooldown(self, user_id):
        current_time = time.time()
        last_time = self.last_interaction.get(user_id, 0)
        cooldown_period = 3
        if current_time - last_time < cooldown_period:
            return True
        self.last_interaction[user_id] = current_time
        return False

    async def get_user_channel(self, user):
        channel_id = self.cog.temp_channels.get(user.id)
        if channel_id:
            return self.cog.bot.get_channel(channel_id)
        return None

    @discord.ui.button(label="Lock", style=discord.ButtonStyle.secondary, custom_id="voicemaster:lock", emoji="<:emoji_10:1280161924167766067>")
    async def lock_channel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await self.is_cooldown(interaction.user.id):
            await self.send_error_message(interaction, "Please wait 3 seconds before using this button again.")
            return

        if not await self.user_owns_temp_channel(interaction.user):
            await self.send_error_message(interaction, "You do not own a temporary voice channel.")
            return

        channel = await self.get_user_channel(interaction.user)
        if channel:
            await channel.set_permissions(interaction.guild.default_role, connect=False)
            await interaction.response.send_message(f"Channel {channel.name} is locked.", ephemeral=True)

    @discord.ui.button(label="Unlock", style=discord.ButtonStyle.secondary, custom_id="voicemaster:unlock", emoji="<:emoji_10:1280162035426000989>")
    async def unlock_channel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await self.is_cooldown(interaction.user.id):
            await self.send_error_message(interaction, "Please wait 3 seconds before using this button again.")
            return

        if not await self.user_owns_temp_channel(interaction.user):
            await self.send_error_message(interaction, "You do not own a temporary voice channel.")
            return

        channel = await self.get_user_channel(interaction.user)
        if channel:
            await channel.set_permissions(interaction.guild.default_role, connect=True)
            await interaction.response.send_message(f"Channel {channel.name} is unlocked.", ephemeral=True)

    @discord.ui.button(label="Hide", style=discord.ButtonStyle.secondary, custom_id="voicemaster:hide", emoji="<:emoji_11:1280162196621361202>")
    async def hide_channel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await self.is_cooldown(interaction.user.id):
            await self.send_error_message(interaction, "Please wait 3 seconds before using this button again.")
            return

        if not await self.user_owns_temp_channel(interaction.user):
            await self.send_error_message(interaction, "You do not own a temporary voice channel.")
            return

        channel = await self.get_user_channel(interaction.user)
        if channel:
            await channel.set_permissions(interaction.guild.default_role, view_channel=False)
            await interaction.response.send_message(f"Channel {channel.name} is hidden.", ephemeral=True)

    @discord.ui.button(label="Unhide", style=discord.ButtonStyle.secondary, custom_id="voicemaster:unhide", emoji="<:emoji_12:1280162349931565066>")
    async def unhide_channel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await self.is_cooldown(interaction.user.id):
            await self.send_error_message(interaction, "Please wait 3 seconds before using this button again.")
            return

        if not await self.user_owns_temp_channel(interaction.user):
            await self.send_error_message(interaction, "You do not own a temporary voice channel.")
            return

        channel = await self.get_user_channel(interaction.user)
        if channel:
            await channel.set_permissions(interaction.guild.default_role, view_channel=True)
            await interaction.response.send_message(f"Channel {channel.name} is unhidden.", ephemeral=True)

    @discord.ui.button(label="Rename", style=discord.ButtonStyle.secondary, custom_id="voicemaster:rename", emoji="<:emoji_13:1280162454252294268>")
    async def rename_channel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await self.is_cooldown(interaction.user.id):
            await self.send_error_message(interaction, "Please wait 3 seconds before using this button again.")
            return

        if not await self.user_owns_temp_channel(interaction.user):
            await self.send_error_message(interaction, "You do not own a temporary voice channel.")
            return

        await interaction.response.send_modal(RenameChannelModal(self))

    @discord.ui.button(label="Set Limit", style=discord.ButtonStyle.secondary, custom_id="voicemaster:set_limit", emoji="<:emoji_19:1280163846648238202>")
    async def set_limit_channel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await self.is_cooldown(interaction.user.id):
            await self.send_error_message(interaction, "Please wait 3 seconds before using this button again.")
            return

        if not await self.user_owns_temp_channel(interaction.user):
            await self.send_error_message(interaction, "You do not own a temporary voice channel.")
            return

        await interaction.response.send_modal(SetLimitModal(self))

    @discord.ui.button(label="Set Bitrate", style=discord.ButtonStyle.secondary, custom_id="voicemaster:set_bitrate", emoji="<:discotoolsxyzicon:1280166960826679417>")
    async def set_bitrate_channel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await self.is_cooldown(interaction.user.id):
            await self.send_error_message(interaction, "Please wait 3 seconds before using this button again.")
            return

        if not await self.user_owns_temp_channel(interaction.user):
            await self.send_error_message(interaction, "You do not own a temporary voice channel.")
            return

        await interaction.response.send_modal(SetBitrateModal(self))

    @discord.ui.button(label="Transfer Ownership", style=discord.ButtonStyle.secondary, custom_id="voicemaster:transfer_ownership", emoji="<:transfer:1280164887716433960>")
    async def transfer_ownership(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await self.is_cooldown(interaction.user.id):
            await self.send_error_message(interaction, "Please wait 3 seconds before using this button again.")
            return

        if not await self.user_owns_temp_channel(interaction.user):
            await self.send_error_message(interaction, "You do not own a temporary voice channel.")
            return

        await interaction.response.send_modal(TransferOwnershipModal(self, interaction))

    @discord.ui.button(label="Kick", style=discord.ButtonStyle.secondary, custom_id="voicemaster:kick", emoji="<:tts_ban_white:1280472246426800218>")
    async def kick_user(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await self.is_cooldown(interaction.user.id):
            await self.send_error_message(interaction, "Please wait 3 seconds before using this button again.")
            return

        if not await self.user_owns_temp_channel(interaction.user):
            await self.send_error_message(interaction, "You do not own a temporary voice channel.")
            return

        await interaction.response.send_modal(KickUserModal(self))

class RenameChannelModal(Modal, title="Rename Channel"):
    new_name = TextInput(label="New Channel Name", required=True)

    def __init__(self, control_panel):
        super().__init__()
        self.control_panel = control_panel

    async def on_submit(self, interaction: discord.Interaction):
        channel = await self.control_panel.get_user_channel(interaction.user)
        if channel:
            await channel.edit(name=self.new_name.value)
            await interaction.response.send_message(f"Channel renamed to {self.new_name.value}.", ephemeral=True)

class SetLimitModal(Modal, title="Set User Limit"):
    limit = TextInput(label="User Limit (0 for unlimited)", required=True)

    def __init__(self, control_panel):
        super().__init__()
        self.control_panel = control_panel

    async def on_submit(self, interaction: discord.Interaction):
        channel = await self.control_panel.get_user_channel(interaction.user)
        if channel:
            await channel.edit(user_limit=int(self.limit.value))
            await interaction.response.send_message(f"User limit set to {self.limit.value}.", ephemeral=True)

class SetBitrateModal(Modal, title="Set Bitrate"):
    bitrate = TextInput(label="Bitrate (8, 64, 96kbps)", required=True)

    def __init__(self, control_panel):
        super().__init__()
        self.control_panel = control_panel

    async def on_submit(self, interaction: discord.Interaction):
        channel = await self.control_panel.get_user_channel(interaction.user)
        if channel:
            await channel.edit(bitrate=int(self.bitrate.value) * 1000)
            await interaction.response.send_message(f"Bitrate set to {self.bitrate.value}kbps.", ephemeral=True)

class TransferOwnershipModal(Modal, title="Transfer Ownership"):
    new_owner_id = TextInput(label="New Owner ID", required=True)

    def __init__(self, control_panel, interaction):
        super().__init__()
        self.control_panel = control_panel
        self.interaction = interaction

    async def on_submit(self, interaction: discord.Interaction):
        new_owner = interaction.guild.get_member(int(self.new_owner_id.value))
        current_channel = await self.control_panel.get_user_channel(interaction.user)

        if not new_owner:
            await interaction.response.send_message("User not found.", ephemeral=True)
            return

        if new_owner == interaction.user:
            await interaction.response.send_message("You cannot transfer ownership to yourself.", ephemeral=True)
            return

        if current_channel and new_owner not in current_channel.members:
            await interaction.response.send_message(f"{new_owner.display_name} is not in your voice channel.", ephemeral=True)
            return

        self.control_panel.cog.temp_channels[new_owner.id] = self.control_panel.cog.temp_channels.pop(interaction.user.id)
        await interaction.response.send_message(f"Ownership transferred to {new_owner.display_name}.", ephemeral=True)

class KickUserModal(Modal, title="Kick User"):
    user_id = TextInput(label="User ID to Kick", required=True)

    def __init__(self, control_panel):
        super().__init__()
        self.control_panel = control_panel

    async def on_submit(self, interaction: discord.Interaction):
        if int(self.user_id.value) == interaction.user.id:
            await interaction.response.send_message("You cannot kick yourself from the voice channel.", ephemeral=True)
            return
        
        channel = await self.control_panel.get_user_channel(interaction.user)
        if channel:
            user = interaction.guild.get_member(int(self.user_id.value))
            if user in channel.members:
                await channel.set_permissions(user, connect=False)
                await user.move_to(None)
                await interaction.response.send_message(f"User {user.display_name} has been kicked from the channel.", ephemeral=True)
            else:
                await interaction.response.send_message("User is not in your voice channel.", ephemeral=True)

