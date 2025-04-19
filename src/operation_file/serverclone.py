import discord
from src.operation_file.logger import Logger
from typing import Optional, Callable
import asyncio
import time
import io
import aiohttp
from concurrent.futures import ThreadPoolExecutor
import json
import re
from datetime import datetime

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
        self.progress_callback = None  # Callback per l'aggiornamento della barra di progresso
        self.stats = {
            "roles_created": 0,
            "categories_created": 0,
            "text_channels_created": 0,
            "voice_channels_created": 0,
            "messages_cloned": 0,
            "errors": 0,
            "start_time": None,
            "elapsed_time": 0
        }
        self.total_operations = 0
        self.completed_operations = 0
        self.roles_map = {}
        self.categories_map = {}
        self.channels_map = {}

    def set_progress_callback(self, callback: Callable[[float], None]):
        """Imposta una callback per aggiornare l'UI con il progresso
        La callback riceve un valore da 0.0 a 1.0 che rappresenta la percentuale di completamento
        """
        self.progress_callback = callback

    def _update_progress(self, progress: float):
        """Aggiorna il progresso chiamando la callback se disponibile"""
        if self.progress_callback:
            # Assicuriamoci che il valore sia tra 0 e 1
            progress = max(0.0, min(1.0, progress))
            self.progress_callback(progress)

    async def start_clone(self, guild_from, guild_to, session, options=None) -> bool:
        """Start the cloning process with options using REST API
        
        Args:
            guild_from: JSON data of source guild
            guild_to: JSON data of destination guild
            session: aiohttp ClientSession with appropriate headers
            options: Dictionary of options to customize the cloning process:
                - clone_roles: Whether to clone roles
                - clone_categories: Whether to clone categories
                - clone_text_channels: Whether to clone text channels
                - clone_voice_channels: Whether to clone voice channels
                - clone_messages: Whether to clone messages
                - messages_limit: Maximum number of messages to clone per channel
        """
        try:
            self.start_time = time.time()
            
            # Reset statistics
            self.stats = {
                "roles_created": 0,
                "categories_created": 0,
                "text_channels_created": 0,
                "voice_channels_created": 0,
                "messages_cloned": 0,
                "errors": 0,
                "start_time": time.time(),
                "elapsed_time": 0
            }
            
            # Reset entity maps
            self.roles_map = {}
            self.categories_map = {}
            self.channels_map = {}
            
            # Default options if none provided
            if options is None:
                options = {
                    "clone_roles": True,
                    "clone_categories": True,
                    "clone_text_channels": True,
                    "clone_voice_channels": True,
                    "clone_messages": False,
                    "messages_limit": 0
                }
            
            # Calculate total operations for progress tracking
            self.total_operations = 0
            self.completed_operations = 0
            
            source_id = guild_from.get("id")
            dest_id = guild_to.get("id")
            
            self._safe_log(f"Starting cloning process from {guild_from.get('name')} to {guild_to.get('name')}")
            
            # Fetch all data from the source server
            
            # Roles
            roles_url = f"https://discord.com/api/v10/guilds/{source_id}/roles"
            roles_data = []
            
            if options.get("clone_roles", True):
                async with session.get(roles_url) as roles_response:
                    if roles_response.status == 200:
                        roles_data = await roles_response.json()
                        # Filtriamo il ruolo everyone che non possiamo clonare
                        roles_data = [r for r in roles_data if r.get("name") != "@everyone"]
                        self.total_roles = len(roles_data)
                        self._safe_log(f"Found {self.total_roles} roles to clone")
                    else:
                        self._safe_log(f"Error fetching roles: {roles_response.status}", "ERROR")
                        self.errors += 1
            
            # Canali
            channels_url = f"https://discord.com/api/v10/guilds/{source_id}/channels"
            categories_data = []
            text_channels_data = []
            voice_channels_data = []
            
            async with session.get(channels_url) as channels_response:
                if channels_response.status == 200:
                    all_channels = await channels_response.json()
                    
                    # Dividiamo i canali per tipo
                    categories_data = [c for c in all_channels if c.get("type") == 4]
                    text_channels_data = [c for c in all_channels if c.get("type") == 0]
                    voice_channels_data = [c for c in all_channels if c.get("type") == 2]
                    
                    total_channels = 0
                    if options.get("clone_categories", True):
                        total_channels += len(categories_data)
                    if options.get("clone_text_channels", True):
                        total_channels += len(text_channels_data)
                    if options.get("clone_voice_channels", True):
                        total_channels += len(voice_channels_data)
                    
                    self.total_channels = total_channels
                    self._safe_log(f"Found {self.total_channels} channels to clone")
                else:
                    self._safe_log(f"Error fetching channels: {channels_response.status}", "ERROR")
                    self.errors += 1
            
            # Inizializziamo il progresso
            self._update_progress(0.0)
            
            # Customize progress percentages based on selected options
            progress_steps = []
            current_progress = 0.0
            
            # Basic server settings always come first
            progress_steps.append(("edit_guild", 0.05))
            current_progress += 0.05
            
            # Calculate progress percentages for each step
            # We allocate percentages based on whether an option is enabled
            
            if options.get("clone_roles", True):
                progress_steps.append(("delete_roles", current_progress + 0.10))
                current_progress += 0.10
                progress_steps.append(("create_roles", current_progress + 0.15))
                current_progress += 0.15
            
            if options.get("clone_categories", True) or options.get("clone_text_channels", True) or options.get("clone_voice_channels", True):
                progress_steps.append(("delete_channels", current_progress + 0.10))
                current_progress += 0.10
            
            if options.get("clone_categories", True):
                progress_steps.append(("create_categories", current_progress + 0.10))
                current_progress += 0.10
            
            channel_progress = 0.0
            if options.get("clone_text_channels", True) or options.get("clone_voice_channels", True):
                channel_progress = 0.20
                progress_steps.append(("create_channels", current_progress + channel_progress))
                current_progress += channel_progress
            
            if options.get("clone_messages", True):
                progress_steps.append(("copy_messages", 1.0))  # Messages always go to 100%
            else:
                # If we don't clone messages, we need to ensure we reach 100%
                self._update_progress(1.0)
            
            # Store progress steps for reference
            self.progress_steps = dict(progress_steps)

            # Cloning sequence with options
            # Basic server settings (name, icon)
            await self._edit_guild_rest(guild_to, guild_from, session)
            self._update_progress(self.progress_steps.get("edit_guild", 0.05))
            
            # Roles
            if options.get("clone_roles", True) and roles_data:
                await self._delete_existing_roles_rest(guild_to, session)
                self._update_progress(self.progress_steps.get("delete_roles", 0.15))
                
                await self._create_roles_rest(guild_to, roles_data, session)
                self._update_progress(self.progress_steps.get("create_roles", 0.30))
            
            # Channels
            channel_types_to_clone = []
            if options.get("clone_categories", True):
                channel_types_to_clone.append("categories")
            if options.get("clone_text_channels", True):
                channel_types_to_clone.append("text")
            if options.get("clone_voice_channels", True):
                channel_types_to_clone.append("voice")
            
            if channel_types_to_clone:
                await self._delete_existing_channels_rest(guild_to, session)
                self._update_progress(self.progress_steps.get("delete_channels", 0.40))
            
            # Categories first
            if options.get("clone_categories", True) and categories_data:
                await self._create_categories_rest(guild_to, categories_data, session)
                self._update_progress(self.progress_steps.get("create_categories", 0.50))
            
            # Text & Voice Channels
            if (options.get("clone_text_channels", True) and text_channels_data) or (options.get("clone_voice_channels", True) and voice_channels_data):
                await self._create_channels_rest(
                    guild_to, 
                    text_channels_data if options.get("clone_text_channels", True) else [],
                    voice_channels_data if options.get("clone_voice_channels", True) else [],
                    session
                )
                self._update_progress(self.progress_steps.get("create_channels", 0.70))
            
            # We skip messages for now as they would need a completely different approach with the REST API
            # You would need to fetch messages from each channel and then post them to the destination
            # This can be added as a separate feature later

            elapsed = time.time() - self.start_time
            self.logger.add(f"Cloning completed in {elapsed:.2f} seconds")
            return True

        except Exception as e:
            self.logger.error(f"Critical error during cloning: {str(e)}")
            return False

    async def _edit_guild_rest(self, guild_to, guild_from, session):
        """Edit basic server settings using REST API"""
        self._safe_log("Starting server modification...")
        try:
            await session.put(f"https://discord.com/api/v10/guilds/{guild_to.get('id')}", json={
                "name": guild_from.get('name')
            })
            
            # Utilizziamo una sessione separata per il download dell'icona
            if guild_from.get('icon'):
                try:
                    # Creiamo una sessione aiohttp temporanea con force_close=True
                    async with session.get(guild_from.get('icon')) as response:
                        if response.status == 200:
                            icon_data = await response.read()
                            await session.put(f"https://discord.com/api/v10/guilds/{guild_to.get('id')}/icons/{guild_to.get('icon')}", data=icon_data)
                            self._safe_log("Server icon updated")
                except Exception as icon_error:
                    self.errors += 1
                    self._safe_log(f"Error downloading server icon: {str(icon_error)}", "ERROR")
        except Exception as e:
            self.errors += 1
            self._safe_log(f"Error modifying server: {str(e)}", "ERROR")

    async def _delete_existing_roles_rest(self, guild_to, session):
        """Delete all existing roles using REST API"""
        self._safe_log("Deleting existing roles...")
        roles_url = f"https://discord.com/api/v10/guilds/{guild_to.get('id')}/roles"
        await session.delete(roles_url)

    async def _delete_existing_channels_rest(self, guild_to, session):
        """Delete all existing channels using REST API"""
        self._safe_log("Deleting existing channels...")
        channels_url = f"https://discord.com/api/v10/guilds/{guild_to.get('id')}/channels"
        await session.delete(channels_url)

    def _safe_log(self, message: str, level: str = "INFO"):
        """Thread-safe logging wrapper"""
        try:
            if level == "ERROR":
                self.logger.error(message)
            else:
                self.logger.add(message)
        except Exception:
            pass

    async def _create_roles_rest(self, guild_to, roles_data, session):
        """Create new roles using REST API (POST, aggiorna mappa ID)"""
        self._safe_log("Creating new roles...")
        for role in roles_data:
            try:
                payload = {
                    "name": role.get('name'),
                    "permissions": role.get('permissions'),
                    "color": role.get('colour'),
                    "hoist": role.get('hoist'),
                    "mentionable": role.get('mentionable')
                }
                async with session.post(f"https://discord.com/api/v10/guilds/{guild_to.get('id')}/roles", json=payload) as resp:
                    if resp.status == 200 or resp.status == 201:
                        created = await resp.json()
                        self.roles_map[role.get('id')] = created.get('id')
                        self.roles_created += 1
                        self._safe_log(f"Role created ({self.roles_created}/{self.total_roles}): {role.get('name')}")
                    elif resp.status == 429:  # Rate limit
                        # Estraiamo le informazioni sul rate limit
                        rate_limit_data = await resp.json()
                        retry_after = rate_limit_data.get('retry_after', 5)  # Default 5 secondi
                        self._safe_log(f"Rate limit hit when creating role {role.get('name')}. Waiting {retry_after} seconds...", "ERROR")
                        await asyncio.sleep(retry_after)
                        # Riprova la creazione del ruolo (decrementiamo l'indice del loop)
                        continue
                    else:
                        self.errors += 1
                        self._safe_log(f"Error creating role {role.get('name')}: {resp.status}", "ERROR")
                
                # Aggiungiamo un piccolo delay per evitare rate limits
                await asyncio.sleep(0.5)
            except Exception as e:
                self.errors += 1
                self._safe_log(f"Error creating role {role.get('name')}: {str(e)}", "ERROR")
                # In caso di errore, aspettiamo un po' di più
                await asyncio.sleep(1.0)

    async def _create_categories_rest(self, guild_to, categories_data, session):
        """Create categories using REST API"""
        for category in categories_data:
            try:
                overwrites_to = {}
                for key, value in category.get('overwrites', {}).items():
                    role = discord.utils.get(guild_to.get('roles'), name=key.get('name'))
                    if role:
                        overwrites_to[role] = value
                
                async with session.put(f"https://discord.com/api/v10/guilds/{guild_to.get('id')}/channels/{category.get('id')}", json={
                    "name": category.get('name'),
                    "overwrites": overwrites_to
                }) as response:
                    if response.status == 200 or response.status == 201:
                        self.channel_map[category.get('id')] = category.get('id')
                        self._safe_log(f"Category created: {category.get('name')}")
                    elif response.status == 429:  # Rate limit
                        # Estraiamo le informazioni sul rate limit
                        rate_limit_data = await response.json()
                        retry_after = rate_limit_data.get('retry_after', 5)  # Default 5 secondi
                        self._safe_log(f"Rate limit hit when creating category {category.get('name')}. Waiting {retry_after} seconds...", "ERROR")
                        await asyncio.sleep(retry_after)
                        # Riprova la creazione della categoria
                        continue
                    else:
                        self.errors += 1
                        self._safe_log(f"Error creating category {category.get('name')}: {response.status}", "ERROR")
                
                # Aggiungi un ritardo più lungo per evitare i rate limit
                await asyncio.sleep(2.0) 
            except Exception as e:
                self.errors += 1
                self._safe_log(f"Error creating category {category.get('name')}: {str(e)}", "ERROR")
                # Aumentiamo il ritardo in caso di errore
                await asyncio.sleep(4.0)

    async def _create_channels_rest(self, guild_to, text_channels_data, voice_channels_data, session):
        """Create channels using REST API"""
        # Create text channels
        for channel in text_channels_data:
            try:
                category = None
                if channel.get('category_id') and channel.get('category_id') in self.channel_map:
                    category = guild_to.get('channels', []).get(str(self.channel_map[channel.get('category_id')]), {}).get('name')

                overwrites_to = {}
                for key, value in channel.get('overwrites', {}).items():
                    role = discord.utils.get(guild_to.get('roles', []), name=key.get('name'))
                    if role:
                        overwrites_to[role] = value

                async with session.put(f"https://discord.com/api/v10/guilds/{guild_to.get('id')}/channels/{channel.get('id')}", json={
                    "name": channel.get('name'),
                    "overwrites": overwrites_to,
                    "position": channel.get('position'),
                    "topic": channel.get('topic'),
                    "slowmode_delay": channel.get('slowmode_delay'),
                    "nsfw": channel.get('nsfw'),
                    "category_id": category
                }) as response:
                    if response.status == 200 or response.status == 201:
                        self.channels_created += 1
                        self._safe_log(f"Text channel created ({self.channels_created}/{self.total_channels}): {channel.get('name')}")
                    elif response.status == 429:  # Rate limit
                        # Estraiamo le informazioni sul rate limit
                        rate_limit_data = await response.json()
                        retry_after = rate_limit_data.get('retry_after', 5)  # Default 5 secondi
                        self._safe_log(f"Rate limit hit when creating channel {channel.get('name')}. Waiting {retry_after} seconds...", "ERROR")
                        await asyncio.sleep(retry_after)
                        # Riprova la creazione del canale
                        continue
                    else:
                        self.errors += 1
                        self._safe_log(f"Error creating text channel {channel.get('name')}: {response.status}", "ERROR")
                
                # Aggiungi un ritardo più lungo per evitare i rate limit
                await asyncio.sleep(2.5)
            except Exception as e:
                self.errors += 1
                self._safe_log(f"Error creating text channel {channel.get('name')}: {str(e)}", "ERROR")
                # Aumentiamo il ritardo in caso di errore
                await asyncio.sleep(5.0)

        # Create voice channels
        for channel in voice_channels_data:
            try:
                category = None
                if channel.get('category_id') and channel.get('category_id') in self.channel_map:
                    category = guild_to.get('channels', []).get(str(self.channel_map[channel.get('category_id')]), {}).get('name')

                overwrites_to = {}
                for key, value in channel.get('overwrites', {}).items():
                    role = discord.utils.get(guild_to.get('roles', []), name=key.get('name'))
                    if role:
                        overwrites_to[role] = value

                async with session.put(f"https://discord.com/api/v10/guilds/{guild_to.get('id')}/channels/{channel.get('id')}", json={
                    "name": channel.get('name'),
                    "overwrites": overwrites_to,
                    "position": channel.get('position'),
                    "user_limit": channel.get('user_limit'),
                    "bitrate": channel.get('bitrate'),
                    "category_id": category
                }) as response:
                    if response.status == 200 or response.status == 201:
                        self.channels_created += 1
                        self._safe_log(f"Voice channel created ({self.channels_created}/{self.total_channels}): {channel.get('name')}")
                    elif response.status == 429:  # Rate limit
                        # Estraiamo le informazioni sul rate limit
                        rate_limit_data = await response.json()
                        retry_after = rate_limit_data.get('retry_after', 5)  # Default 5 secondi
                        self._safe_log(f"Rate limit hit when creating channel {channel.get('name')}. Waiting {retry_after} seconds...", "ERROR")
                        await asyncio.sleep(retry_after)
                        # Riprova la creazione del canale
                        continue
                    else:
                        self.errors += 1
                        self._safe_log(f"Error creating voice channel {channel.get('name')}: {response.status}", "ERROR")
                
                # Aggiungi un ritardo più lungo per evitare i rate limit
                await asyncio.sleep(2.5)
            except Exception as e:
                self.errors += 1
                self._safe_log(f"Error creating voice channel {channel.get('name')}: {str(e)}", "ERROR")
                # Aumentiamo il ritardo in caso di errore
                await asyncio.sleep(5.0)

    async def _copy_messages(self, guild_from: discord.Guild, guild_to: discord.Guild, message_limit=100):
        """Copy messages from source server channels with a limit"""
        self._safe_log("Starting message copy...")
        
        # Conteggio totale dei messaggi da copiare (approssimativo)
        # Per ogni canale di testo, utilizziamo il limite specificato
        self.total_messages = len(guild_from.text_channels) * message_limit
        
        copy_tasks = []
        for channel_from in guild_from.text_channels:
            channel_to = discord.utils.get(guild_to.text_channels, name=channel_from.name)
            if channel_to:
                copy_tasks.append(self._copy_channel_messages(channel_from, channel_to, message_limit))
        
        # Execute message copying concurrently in batches, using smaller batches
        batch_size = 2  # Ridotto da 3 a 2 per evitare rate limit
        for i in range(0, len(copy_tasks), batch_size):
            batch = copy_tasks[i:i + batch_size]
            await asyncio.gather(*batch, return_exceptions=True)
            
            # Aspettiamo un po' tra i batch per evitare rate limit
            await asyncio.sleep(1.0)

    async def _copy_channel_messages(self, channel_from, channel_to, message_limit=100):
        """Helper method for copying messages from one channel with a limit"""
        try:
            # Iniziamo con un piccolo delay tra i messaggi per evitare rate limit
            rate_limit_delay = 0.7
            consecutive_errors = 0
            message_count = 0
            
            # Recuperiamo i messaggi in ordine cronologico inverso (dal più recente)
            messages = []
            async for message in channel_from.history(limit=message_limit):
                messages.append(message)
            
            # Invertiamo per inviarli in ordine cronologico (dal più vecchio)
            messages.reverse()
            
            for message in messages:
                # Se abbiamo troppi errori consecutivi, aumentiamo molto il delay
                if consecutive_errors >= 3:
                    rate_limit_delay = min(5.0, rate_limit_delay * 1.5)
                    consecutive_errors = 0
                
                try:
                    # Prepariamo il contenuto del messaggio
                    author_name = message.author.display_name
                    timestamp = message.created_at.strftime("%d/%m/%Y %H:%M")
                    
                    # Gestione degli embed e del contenuto
                    content = f"**{author_name}** *{timestamp}*"
                    if message.content:
                        content += f"\n{message.content}"
                    
                    # Formattiamo il contenuto
                    if len(content) > 2000:
                        # Se il messaggio è troppo lungo, lo tronchiamo
                        content = content[:1997] + "..."
                    
                    # Inviamo il messaggio
                    if content and content != f"**{author_name}**:":
                        await channel_to.send(content=content)
                        self.messages_copied += 1
                        message_count += 1
                        
                    # Gestione degli allegati
                    if message.attachments:
                        files = []
                        
                        # Utilizziamo una sessione sicura per scaricare gli allegati
                        connector = aiohttp.TCPConnector(force_close=True)
                        async with aiohttp.ClientSession(connector=connector) as session:
                            for attachment in message.attachments:
                                try:
                                    # Scarichiamo direttamente dall'URL dell'allegato
                                    async with session.get(attachment.url) as response:
                                        if response.status == 200:
                                            file_data = await response.read()
                                            files.append(discord.File(io.BytesIO(file_data), filename=attachment.filename))
                                except Exception:
                                    continue
                        
                        # Se abbiamo scaricato file, li inviamo
                        if files:
                            # Inviamo il messaggio con gli allegati, includendo il nome dell'autore se non già inviato
                            if not content or content == f"**{author_name}**:":
                                await channel_to.send(content=f"**{author_name}** *{timestamp}*", files=files)
                            else:
                                await channel_to.send(files=files)
                            
                            self.messages_copied += 1
                            message_count += 1
                    
                    # Aspettiamo tra un messaggio e l'altro per evitare rate limit
                    await asyncio.sleep(rate_limit_delay)
                    
                    # Se tutto va bene, riduciamo gradualmente il delay
                    rate_limit_delay = max(0.5, rate_limit_delay * 0.95)
                    # Reset del contatore errori in caso di successo
                    consecutive_errors = 0
                except discord.errors.HTTPException as e:
                    if e.status == 429:  # Rate limit
                        consecutive_errors += 1
                        self._safe_log(f"Rate limit reached, waiting longer ({round(rate_limit_delay, 1)}s)")
                        await asyncio.sleep(rate_limit_delay)
                    else:
                        consecutive_errors += 1
                        self._safe_log(f"HTTP error while sending message: {e}")
                        await asyncio.sleep(rate_limit_delay)
                except Exception as e:
                    consecutive_errors += 1
                    self._safe_log(f"Error copying message: {str(e)}")
                    await asyncio.sleep(rate_limit_delay)
            
            self._safe_log(f"Copied {message_count} messages to {channel_to.name}")
            return message_count
        except Exception as e:
            self._safe_log(f"Error during message copying: {str(e)}")
            return 0

    def get_stats(self) -> dict:
        """Return cloning statistics"""
        # Update elapsed time if started
        if self.stats["start_time"]:
            self.stats["elapsed_time"] = time.time() - self.stats["start_time"]
        return self.stats