import customtkinter as ctk
import discord
import asyncio
import time
import sys
import os

# Import Colors directly
from src.interface.styles.colors import Colors
from src.operation_file import Clone
from src.interface.utils.language_manager import LanguageManager

class GuildInput(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        # Get language manager
        self.lang = LanguageManager()
        
        # Main frame
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="x", padx=20)
        
        # Source Guild Frame
        self.source_label = ctk.CTkLabel(
            self.main_frame,
            text=self.lang.get_text("input.guild.source.title"),
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.source_label.pack(anchor="w", pady=(10, 5))
        
        self.source_entry = ctk.CTkEntry(
            self.main_frame,
            placeholder_text=self.lang.get_text("input.guild.source.placeholder"),
            height=40,
            text_color=Colors.get_color(Colors.TEXT),
            fg_color=Colors.get_color(Colors.INPUT_BG)
        )
        self.source_entry.pack(fill="x", pady=(0, 10))
        
        # Destination Guild Frame
        self.dest_label = ctk.CTkLabel(
            self.main_frame,
            text=self.lang.get_text("input.guild.destination.title"),
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.dest_label.pack(anchor="w", pady=(10, 5))
        
        self.dest_entry = ctk.CTkEntry(
            self.main_frame,
            placeholder_text=self.lang.get_text("input.guild.destination.placeholder"),
            height=40,
            text_color=Colors.get_color(Colors.TEXT),
            fg_color=Colors.get_color(Colors.INPUT_BG)
        )
        self.dest_entry.pack(fill="x", pady=(0, 20))
        
        # Progress bar
        self.progress = ctk.CTkProgressBar(self.main_frame)
        self.progress.set(0)
        
        # Clone Button
        self.clone_button = ctk.CTkButton(
            self.main_frame,
            text=self.lang.get_text("input.guild.clone_button"),
            command=self.start_clone,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=Colors.get_color(Colors.TEXT, ctk.get_appearance_mode().lower()),
            text_color=Colors.get_color(Colors.BACKGROUND, ctk.get_appearance_mode().lower()),
            hover_color=Colors.get_color(Colors.TEXT_MUTED, ctk.get_appearance_mode().lower())
        )
        self.clone_button.pack(pady=10)
        
        # Discord client
        self.client = None
        
        # Update colors when theme changes
        self._update_colors()
        self.bind('<Configure>', lambda e: self._update_colors())
        
        # Add observer for language changes
        self.lang.add_observer(self.update_texts)
        
    def _update_colors(self):
        mode = ctk.get_appearance_mode().lower()
        
        # Update button colors
        self.clone_button.configure(
            fg_color=Colors.get_color(Colors.TEXT, mode),
            text_color=Colors.get_color(Colors.BACKGROUND, mode),
            hover_color=Colors.get_color(Colors.TEXT_MUTED, mode)
        )
        
        # Update input colors
        for entry in [self.source_entry, self.dest_entry]:
            entry.configure(
                text_color=Colors.get_color(Colors.TEXT, mode),
                fg_color=Colors.get_color(Colors.INPUT_BG, mode)
            )

    def update_progress(self, value, show=True):
        """Update progress bar value and visibility"""
        if show and not self.progress.winfo_ismapped():
            self.progress.pack(fill="x", pady=(0, 10))
        elif not show and self.progress.winfo_ismapped():
            self.progress.pack_forget()
        self.progress.set(value)
        
    def start_clone(self):
        """Start the cloning process"""
        # Get token from token input
        main_window = self.winfo_toplevel()
        token = main_window.token_input.entry.get()
        source_id = self.source_entry.get()
        dest_id = self.dest_entry.get()
        
        # Validate inputs
        if not all([token, source_id, dest_id]):
            main_window.status_bar.update_status(
                self.lang.get_text("status.error"), 
                "red"
            )
            return
            
        # Disable clone button during process
        self.clone_button.configure(state="disabled")
        main_window.status_bar.update_status(
            self.lang.get_text("status.cloning"), 
            "blue"
        )
        
        # Start cloning process
        asyncio.run(self.clone_server(token, source_id, dest_id))
        
    async def clone_server(self, token, source_id, dest_id):
        """Execute server cloning process"""
        main_window = self.winfo_toplevel()
        try:
            intents = discord.Intents.all()
            self.client = discord.Client(intents=intents)
            
            @self.client.event
            async def on_ready():
                try:
                    self._debug_log(self.lang.get_text("logs.clone.connected").format(user=self.client.user))
                    
                    guild_from = self.client.get_guild(int(source_id))
                    guild_to = self.client.get_guild(int(dest_id))
                    
                    if not guild_from or not guild_to:
                        self._debug_log(self.lang.get_text("logs.clone.server_not_found"), "ERROR")
                        await self.client.close()
                        return
                    
                    cloner = Clone(self._debug_log)
                    success = await cloner.start_clone(guild_from, guild_to)
                    
                    if success:
                        self._debug_log(self.lang.get_text("logs.clone.completed"), "SUCCESS")
                    
                except Exception as e:
                    self._debug_log(
                        self.lang.get_text("logs.clone.error").format(error=str(e)), 
                        "ERROR"
                    )
                finally:
                    self.clone_button.configure(state="normal")
                    await self.client.close()
            
            await self.client.start(token, bot=False)
            
        except Exception as e:
            self._debug_log(
                self.lang.get_text("logs.clone.connection_error").format(error=str(e)), 
                "ERROR"
            )
            self.clone_button.configure(state="normal")

    def _debug_log(self, message, level="INFO"):
        """Send log to debug window if active"""
        main_window = self.winfo_toplevel()
        if hasattr(main_window, 'debug_mode') and main_window.debug_mode:
            if hasattr(main_window, 'debug_window'):
                main_window.debug_window.log(message, level)
        
        # Always update status bar
        color = "red" if level == "ERROR" else "blue" if level == "INFO" else "green"
        main_window.status_bar.update_status(message, color)

    def update_texts(self):
        """Update texts when language changes"""
        self.source_label.configure(text=self.lang.get_text("input.guild.source.title"))
        self.source_entry.configure(placeholder_text=self.lang.get_text("input.guild.source.placeholder"))
        self.dest_label.configure(text=self.lang.get_text("input.guild.destination.title"))
        self.dest_entry.configure(placeholder_text=self.lang.get_text("input.guild.destination.placeholder"))
        self.clone_button.configure(text=self.lang.get_text("input.guild.clone_button"))