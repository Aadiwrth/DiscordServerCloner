import discord
from src.operation_file.logger import Logger
from typing import Optional
import asyncio
import time
import io
from concurrent.futures import ThreadPoolExecutor

class Clone:
    def __init__(self, debug_callback=None):
        self.logger = Logger(debug_callback)
        self.total_roles = 0
        self.total_channels = 0
        self.total_messages = 0
        self.roles_created = 0
        self.channels_created = 0
        self.messages_copied = 0
        self.errors = 0
        self.start_time = None
        self.channel_map = {}  # Map to track old->new channels
        self.executor = ThreadPoolExecutor(max_workers=3)  # For async file operations

    async def start_clone(self, guild_from: discord.Guild, guild_to: discord.Guild) -> bool:
        """Start the cloning process"""
        try:
            self.start_time = time.time()
            self.total_roles = len([r for r in guild_from.roles if r.name != "@everyone"])
            self.total_channels = len(guild_from.channels)

            # Cloning sequence
            await self._edit_guild(guild_to, guild_from)
            await self._delete_existing_roles(guild_to)
            await self._delete_existing_channels(guild_to)
            await self._create_roles(guild_to, guild_from)
            await self._create_categories(guild_to, guild_from)
            await self._create_channels(guild_to, guild_from)
            await self._copy_messages(guild_from, guild_to)

            elapsed = time.time() - self.start_time
            self.logger.add(f"Cloning completed in {elapsed:.2f} seconds")
            return True

        except Exception as e:
            self.logger.error(f"Critical error during cloning: {str(e)}")
            return False

    async def _edit_guild(self, guild_to: discord.Guild, guild_from: discord.Guild):
        """Edit basic server settings"""
        self._safe_log("Starting server modification...")
        try:
            await guild_to.edit(name=guild_from.name)
            if guild_from.icon:
                icon_image = await guild_from.icon_url.read()
                await guild_to.edit(icon=icon_image)
                self._safe_log("Server icon updated")
        except Exception as e:
            self.errors += 1
            self._safe_log(f"Error modifying server: {str(e)}", "ERROR")

    async def _delete_existing_roles(self, guild: discord.Guild):
        """Delete all existing roles"""
        self._safe_log("Deleting existing roles...")
        for role in guild.roles:
            try:
                if role.name != "@everyone":
                    await role.delete()
                    self._safe_log(f"Role deleted: {role.name}")
                    await asyncio.sleep(0.5)
            except Exception as e:
                self.errors += 1
                self._safe_log(f"Error deleting role {role.name}: {str(e)}", "ERROR")

    async def _delete_existing_channels(self, guild: discord.Guild):
        """Delete all existing channels"""
        self._safe_log("Deleting existing channels...")
        for channel in guild.channels:
            try:
                await channel.delete()
                self._safe_log(f"Channel deleted: {channel.name}")
                await asyncio.sleep(0.5)
            except Exception as e:
                self.errors += 1
                self._safe_log(f"Error deleting channel {channel.name}: {str(e)}", "ERROR")

    async def _create_roles(self, guild_to: discord.Guild, guild_from: discord.Guild):
        """Create new roles"""
        self._safe_log("Creating new roles...")
        roles = [role for role in guild_from.roles if role.name != "@everyone"]
        roles.reverse()
        
        for role in roles:
            try:
                await guild_to.create_role(
                    name=role.name,
                    permissions=role.permissions,
                    colour=role.colour,
                    hoist=role.hoist,
                    mentionable=role.mentionable
                )
                self.roles_created += 1
                self._safe_log(f"Role created ({self.roles_created}/{self.total_roles}): {role.name}")
                await asyncio.sleep(0.5)
            except Exception as e:
                self.errors += 1
                self._safe_log(f"Error creating role {role.name}: {str(e)}", "ERROR")

    async def _create_categories(self, guild_to: discord.Guild, guild_from: discord.Guild):
        """Create categories"""
        for category in guild_from.categories:
            try:
                overwrites_to = {}
                for key, value in category.overwrites.items():
                    role = discord.utils.get(guild_to.roles, name=key.name)
                    if role:
                        overwrites_to[role] = value
                
                new_category = await guild_to.create_category(
                    name=category.name,
                    overwrites=overwrites_to
                )
                self.channel_map[category.id] = new_category.id
                self._safe_log(f"Category created: {category.name}")
                await asyncio.sleep(0.5)
            except Exception as e:
                self.errors += 1
                self._safe_log(f"Error creating category {category.name}: {str(e)}", "ERROR")

    async def _create_channels(self, guild_to: discord.Guild, guild_from: discord.Guild):
        """Create channels"""
        # Create text channels
        for channel in guild_from.text_channels:
            try:
                category = None
                if channel.category_id and channel.category_id in self.channel_map:
                    category = guild_to.get_channel(self.channel_map[channel.category_id])

                overwrites_to = {}
                for key, value in channel.overwrites.items():
                    role = discord.utils.get(guild_to.roles, name=key.name)
                    if role:
                        overwrites_to[role] = value

                new_channel = await guild_to.create_text_channel(
                    name=channel.name,
                    overwrites=overwrites_to,
                    position=channel.position,
                    topic=channel.topic,
                    slowmode_delay=channel.slowmode_delay,
                    nsfw=channel.nsfw,
                    category=category
                )
                self.channels_created += 1
                self._safe_log(f"Text channel created ({self.channels_created}/{self.total_channels}): {channel.name}")
                await asyncio.sleep(0.5)
            except Exception as e:
                self.errors += 1
                self._safe_log(f"Error creating text channel {channel.name}: {str(e)}", "ERROR")

        # Create voice channels
        for channel in guild_from.voice_channels:
            try:
                category = None
                if channel.category_id and channel.category_id in self.channel_map:
                    category = guild_to.get_channel(self.channel_map[channel.category_id])

                overwrites_to = {}
                for key, value in channel.overwrites.items():
                    role = discord.utils.get(guild_to.roles, name=key.name)
                    if role:
                        overwrites_to[role] = value

                new_channel = await guild_to.create_voice_channel(
                    name=channel.name,
                    overwrites=overwrites_to,
                    position=channel.position,
                    user_limit=channel.user_limit,
                    bitrate=channel.bitrate,
                    category=category
                )
                self.channels_created += 1
                self._safe_log(f"Voice channel created ({self.channels_created}/{self.total_channels}): {channel.name}")
                await asyncio.sleep(0.5)
            except Exception as e:
                self.errors += 1
                self._safe_log(f"Error creating voice channel {channel.name}: {str(e)}", "ERROR")

    def _safe_log(self, message: str, level: str = "INFO"):
        """Thread-safe logging wrapper"""
        try:
            if level == "ERROR":
                self.logger.error(message)
            else:
                self.logger.add(message)
        except Exception:
            pass

    async def _copy_messages(self, guild_from: discord.Guild, guild_to: discord.Guild):
        """Copy messages from source server channels"""
        self._safe_log("Starting message copy...")
        
        copy_tasks = []
        for channel_from in guild_from.text_channels:
            channel_to = discord.utils.get(guild_to.text_channels, name=channel_from.name)
            if channel_to:
                copy_tasks.append(self._copy_channel_messages(channel_from, channel_to))
        
        # Execute message copying concurrently in batches
        batch_size = 3  # Smaller batch size for message copying to prevent rate limits
        for i in range(0, len(copy_tasks), batch_size):
            batch = copy_tasks[i:i + batch_size]
            await asyncio.gather(*batch, return_exceptions=True)

    async def _copy_channel_messages(self, channel_from, channel_to):
        """Helper method for copying messages from one channel"""
        try:
            self._safe_log(f"Copying messages from channel: {channel_from.name}")
            async for message in channel_from.history(limit=50, oldest_first=True):  # Reduced limit for stability
                try:
                    content = message.content
                    if message.embeds:
                        embed_texts = []
                        for embed in message.embeds:
                            if embed.title:
                                embed_texts.append(f"**{embed.title}**")
                            if embed.description:
                                embed_texts.append(embed.description)
                        if embed_texts:
                            content = content + "\n\n" + "\n".join(embed_texts) if content else "\n".join(embed_texts)

                    # Send message without waiting for files if there's content
                    if content:
                        await channel_to.send(content=content)
                        self.messages_copied += 1
                        
                    # Handle attachments separately
                    if message.attachments:
                        files = []
                        for attachment in message.attachments:
                            try:
                                file_data = await attachment.read()
                                files.append(discord.File(io.BytesIO(file_data), filename=attachment.filename))
                            except Exception:
                                continue
                        if files:
                            await channel_to.send(files=files)
                    
                    await asyncio.sleep(0.5)  # Reduced delay between messages
                    
                except Exception as e:
                    self.errors += 1
                    self._safe_log(f"Error copying message: {str(e)}", "ERROR")
                    continue
                    
        except Exception as e:
            self.errors += 1
            self._safe_log(f"Error accessing channel {channel_from.name}: {str(e)}", "ERROR")

    def get_stats(self) -> dict:
        """Return cloning statistics"""
        return {
            "roles_created": self.roles_created,
            "total_roles": self.total_roles,
            "channels_created": self.channels_created,
            "total_channels": self.total_channels,
            "messages_copied": self.messages_copied,
            "total_messages": self.total_messages,
            "errors": self.errors,
            "elapsed_time": time.time() - self.start_time if self.start_time else 0
        }