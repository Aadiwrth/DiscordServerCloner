import customtkinter as ctk
import asyncio
import aiohttp
import tkinter as tk
from tkinter import messagebox
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
import webbrowser
import os
import tempfile
from PIL import Image, ImageTk
import io
import requests

from src.interface.styles.colors import Colors


class MessageViewer(ctk.CTkScrollableFrame):
    """Advanced message viewer with media support for Discord channels."""
    
    def __init__(self, parent, lang, token: str, **kwargs):
        super().__init__(parent, **kwargs)
        self.lang = lang
        self.token = token
        self.mode = ctk.get_appearance_mode().lower()
        self.messages = []
        self.current_channel = None
        self.media_cache = {}
        
        # Configure colors
        self.configure(fg_color=Colors.get_color(Colors.BACKGROUND, self.mode))
        
        # Create header
        self.create_header()
        
        # Message container
        self.message_container = ctk.CTkFrame(self, fg_color="transparent")
        self.message_container.pack(fill="both", expand=True, padx=10, pady=5)
        
    def create_header(self):
        """Create the header with channel info and controls."""
        self.header = ctk.CTkFrame(self, height=60, fg_color=Colors.get_color(Colors.SETTINGS_BG, self.mode))
        self.header.pack(fill="x", padx=10, pady=(10, 5))
        self.header.pack_propagate(False)
        
        # Channel info
        self.channel_label = ctk.CTkLabel(
            self.header, 
            text=self.lang.get_text("advanced.select_channel") if hasattr(self.lang, 'get_text') else "Seleziona un canale",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.channel_label.pack(side="left", padx=15, pady=15)
        
        # Controls
        controls_frame = ctk.CTkFrame(self.header, fg_color="transparent")
        controls_frame.pack(side="right", padx=15, pady=10)
        
        self.refresh_btn = ctk.CTkButton(
            controls_frame,
            text="🔄",
            width=40,
            height=30,
            command=self.refresh_messages,
            fg_color=Colors.get_color(Colors.BACKGROUND_LIGHT, self.mode),
            hover_color=Colors.get_color(Colors.SETTINGS_ITEM_BG, self.mode)
        )
        self.refresh_btn.pack(side="right", padx=5)
        
        self.load_more_btn = ctk.CTkButton(
            controls_frame,
            text=self.lang.get_text("advanced.load_more") if hasattr(self.lang, 'get_text') else "Carica altri",
            height=30,
            command=self.load_more_messages,
            fg_color=Colors.get_color(Colors.TEXT, self.mode),
            text_color=Colors.get_color(Colors.BACKGROUND, self.mode)
        )
        self.load_more_btn.pack(side="right", padx=5)
        
    async def load_channel_messages(self, channel_id: str, channel_name: str, limit: int = 50):
        """Load messages from a Discord channel."""
        self.current_channel = {"id": channel_id, "name": channel_name}
        self.channel_label.configure(text=f"# {channel_name}")
        
        # Clear existing messages
        for widget in self.message_container.winfo_children():
            widget.destroy()
        
        # Show loading
        loading_label = ctk.CTkLabel(
            self.message_container,
            text=self.lang.get_text("status.loading") if hasattr(self.lang, 'get_text') else "Caricamento messaggi...",
            text_color=Colors.get_color(Colors.TEXT_MUTED, self.mode)
        )
        loading_label.pack(pady=20)
        
        try:
            messages = await self.fetch_messages(channel_id, limit)
            loading_label.destroy()
            self.display_messages(messages)
        except Exception as e:
            loading_label.configure(text=f"Errore: {str(e)}")
            
    async def fetch_messages(self, channel_id: str, limit: int = 50, before: str = None) -> List[Dict[str, Any]]:
        """Fetch messages from Discord API."""
        headers = {
            "Authorization": self.token,
            "Content-Type": "application/json"
        }
        
        url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
        params = {"limit": limit}
        if before:
            params["before"] = before
            
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url, params=params) as resp:
                if resp.status != 200:
                    raise Exception(f"HTTP {resp.status}: {await resp.text()}")
                return await resp.json()
                
    def display_messages(self, messages: List[Dict[str, Any]]):
        """Display messages in the viewer."""
        self.messages.extend(messages)
        
        for message in reversed(messages):  # Display in chronological order
            self.create_message_widget(message)
            
    def create_message_widget(self, message: Dict[str, Any]):
        """Create a widget for a single message."""
        # Message frame
        msg_frame = ctk.CTkFrame(
            self.message_container,
            fg_color=Colors.get_color(Colors.BACKGROUND_LIGHT, self.mode),
            corner_radius=8
        )
        msg_frame.pack(fill="x", padx=5, pady=3)
        
        # Author and timestamp header
        header_frame = ctk.CTkFrame(msg_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=(8, 4))
        
        author = message.get("author", {})
        author_name = author.get("username", "Unknown")
        timestamp = message.get("timestamp", "")
        
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                formatted_time = dt.strftime("%d/%m/%Y %H:%M")
            except:
                formatted_time = timestamp[:16]
        else:
            formatted_time = ""
            
        author_label = ctk.CTkLabel(
            header_frame,
            text=author_name,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=Colors.get_color(Colors.TEXT, self.mode)
        )
        author_label.pack(side="left")
        
        time_label = ctk.CTkLabel(
            header_frame,
            text=formatted_time,
            font=ctk.CTkFont(size=11),
            text_color=Colors.get_color(Colors.TEXT_MUTED, self.mode)
        )
        time_label.pack(side="left", padx=(10, 0))
        
        # Message content
        content = message.get("content", "")
        if content:
            content_label = ctk.CTkLabel(
                msg_frame,
                text=content,
                font=ctk.CTkFont(size=12),
                text_color=Colors.get_color(Colors.TEXT, self.mode),
                wraplength=700,
                justify="left"
            )
            content_label.pack(anchor="w", padx=10, pady=(0, 5))
            
        # Attachments
        attachments = message.get("attachments", [])
        if attachments:
            self.create_attachments_section(msg_frame, attachments)
            
        # Embeds
        embeds = message.get("embeds", [])
        if embeds:
            self.create_embeds_section(msg_frame, embeds)
            
    def create_attachments_section(self, parent, attachments: List[Dict[str, Any]]):
        """Create section for message attachments."""
        attachments_frame = ctk.CTkFrame(parent, fg_color="transparent")
        attachments_frame.pack(fill="x", padx=10, pady=5)
        
        for attachment in attachments:
            self.create_attachment_widget(attachments_frame, attachment)
            
    def create_attachment_widget(self, parent, attachment: Dict[str, Any]):
        """Create widget for a single attachment."""
        filename = attachment.get("filename", "unknown")
        url = attachment.get("url", "")
        content_type = attachment.get("content_type", "")
        size = attachment.get("size", 0)
        
        attachment_frame = ctk.CTkFrame(
            parent,
            fg_color=Colors.get_color(Colors.SETTINGS_ITEM_BG, self.mode),
            corner_radius=6
        )
        attachment_frame.pack(fill="x", pady=2)
        
        # Check if it's an image
        if content_type.startswith("image/"):
            self.create_image_preview(attachment_frame, url, filename)
        elif content_type.startswith("audio/"):
            self.create_audio_widget(attachment_frame, url, filename)
        elif content_type.startswith("video/"):
            self.create_video_widget(attachment_frame, url, filename)
        else:
            self.create_file_widget(attachment_frame, url, filename, size)
            
    def create_image_preview(self, parent, url: str, filename: str):
        """Create image preview widget."""
        img_frame = ctk.CTkFrame(parent, fg_color="transparent")
        img_frame.pack(fill="x", padx=8, pady=8)
        
        # Image label with click to open
        img_label = ctk.CTkLabel(
            img_frame,
            text=f"🖼️ {filename}",
            font=ctk.CTkFont(size=12),
            text_color=Colors.get_color(Colors.TEXT, self.mode),
            cursor="hand2"
        )
        img_label.pack(anchor="w")
        img_label.bind("<Button-1>", lambda e: self.open_media(url))
        
        # Download button
        download_btn = ctk.CTkButton(
            img_frame,
            text="📥",
            width=30,
            height=25,
            command=lambda: self.download_file(url, filename),
            fg_color=Colors.get_color(Colors.BACKGROUND_LIGHT, self.mode)
        )
        download_btn.pack(side="right", padx=5)
        
    def create_audio_widget(self, parent, url: str, filename: str):
        """Create audio widget."""
        audio_frame = ctk.CTkFrame(parent, fg_color="transparent")
        audio_frame.pack(fill="x", padx=8, pady=8)
        
        audio_label = ctk.CTkLabel(
            audio_frame,
            text=f"🎵 {filename}",
            font=ctk.CTkFont(size=12),
            text_color=Colors.get_color(Colors.TEXT, self.mode)
        )
        audio_label.pack(side="left")
        
        # Play button
        play_btn = ctk.CTkButton(
            audio_frame,
            text="▶️",
            width=40,
            height=25,
            command=lambda: self.open_media(url),
            fg_color=Colors.get_color(Colors.TEXT, self.mode),
            text_color=Colors.get_color(Colors.BACKGROUND, self.mode)
        )
        play_btn.pack(side="right", padx=5)
        
        # Download button
        download_btn = ctk.CTkButton(
            audio_frame,
            text="📥",
            width=30,
            height=25,
            command=lambda: self.download_file(url, filename),
            fg_color=Colors.get_color(Colors.BACKGROUND_LIGHT, self.mode)
        )
        download_btn.pack(side="right", padx=5)
        
    def create_video_widget(self, parent, url: str, filename: str):
        """Create video widget."""
        video_frame = ctk.CTkFrame(parent, fg_color="transparent")
        video_frame.pack(fill="x", padx=8, pady=8)
        
        video_label = ctk.CTkLabel(
            video_frame,
            text=f"🎬 {filename}",
            font=ctk.CTkFont(size=12),
            text_color=Colors.get_color(Colors.TEXT, self.mode)
        )
        video_label.pack(side="left")
        
        # Play button
        play_btn = ctk.CTkButton(
            video_frame,
            text="▶️",
            width=40,
            height=25,
            command=lambda: self.open_media(url),
            fg_color=Colors.get_color(Colors.TEXT, self.mode),
            text_color=Colors.get_color(Colors.BACKGROUND, self.mode)
        )
        play_btn.pack(side="right", padx=5)
        
        # Download button
        download_btn = ctk.CTkButton(
            video_frame,
            text="📥",
            width=30,
            height=25,
            command=lambda: self.download_file(url, filename),
            fg_color=Colors.get_color(Colors.BACKGROUND_LIGHT, self.mode)
        )
        download_btn.pack(side="right", padx=5)
        
    def create_file_widget(self, parent, url: str, filename: str, size: int):
        """Create generic file widget."""
        file_frame = ctk.CTkFrame(parent, fg_color="transparent")
        file_frame.pack(fill="x", padx=8, pady=8)
        
        size_text = self.format_file_size(size)
        file_label = ctk.CTkLabel(
            file_frame,
            text=f"📄 {filename} ({size_text})",
            font=ctk.CTkFont(size=12),
            text_color=Colors.get_color(Colors.TEXT, self.mode)
        )
        file_label.pack(side="left")
        
        # Download button
        download_btn = ctk.CTkButton(
            file_frame,
            text="📥",
            width=40,
            height=25,
            command=lambda: self.download_file(url, filename),
            fg_color=Colors.get_color(Colors.TEXT, self.mode),
            text_color=Colors.get_color(Colors.BACKGROUND, self.mode)
        )
        download_btn.pack(side="right", padx=5)
        
    def create_embeds_section(self, parent, embeds: List[Dict[str, Any]]):
        """Create section for message embeds."""
        for embed in embeds:
            embed_frame = ctk.CTkFrame(
                parent,
                fg_color=Colors.get_color(Colors.SETTINGS_ITEM_BG, self.mode),
                corner_radius=6
            )
            embed_frame.pack(fill="x", padx=10, pady=5)
            
            title = embed.get("title", "")
            description = embed.get("description", "")
            url = embed.get("url", "")
            
            if title:
                title_label = ctk.CTkLabel(
                    embed_frame,
                    text=title,
                    font=ctk.CTkFont(size=13, weight="bold"),
                    text_color=Colors.get_color(Colors.TEXT, self.mode)
                )
                title_label.pack(anchor="w", padx=8, pady=(8, 4))
                
            if description:
                desc_label = ctk.CTkLabel(
                    embed_frame,
                    text=description[:200] + ("..." if len(description) > 200 else ""),
                    font=ctk.CTkFont(size=11),
                    text_color=Colors.get_color(Colors.TEXT_MUTED, self.mode),
                    wraplength=600,
                    justify="left"
                )
                desc_label.pack(anchor="w", padx=8, pady=(0, 8))
                
    def format_file_size(self, size: int) -> str:
        """Format file size in human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
        
    def open_media(self, url: str):
        """Open media file in default application."""
        try:
            webbrowser.open(url)
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile aprire il file: {str(e)}")
            
    def download_file(self, url: str, filename: str):
        """Download file to user's system."""
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            # Ask user where to save
            from tkinter import filedialog
            save_path = filedialog.asksaveasfilename(
                defaultextension=os.path.splitext(filename)[1],
                initialvalue=filename,
                title="Salva file"
            )
            
            if save_path:
                with open(save_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                messagebox.showinfo("Successo", f"File salvato: {save_path}")
                
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile scaricare il file: {str(e)}")
            
    def refresh_messages(self):
        """Refresh current channel messages."""
        if self.current_channel:
            asyncio.create_task(self.load_channel_messages(
                self.current_channel["id"],
                self.current_channel["name"]
            ))
            
    def load_more_messages(self):
        """Load more messages from current channel."""
        if self.current_channel and self.messages:
            oldest_message_id = self.messages[-1].get("id")
            asyncio.create_task(self.load_more_messages_async(oldest_message_id))
            
    async def load_more_messages_async(self, before_id: str):
        """Load more messages asynchronously."""
        try:
            more_messages = await self.fetch_messages(
                self.current_channel["id"],
                limit=25,
                before=before_id
            )
            if more_messages:
                self.display_messages(more_messages)
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile caricare altri messaggi: {str(e)}")