import customtkinter as ctk
import asyncio
import aiohttp
from typing import Callable, Dict, Any
import tkinter as tk
import threading
from concurrent.futures import ThreadPoolExecutor

from src.interface.styles.colors import Colors
from src.interface.styles.discord_colors import DiscordColors
from src.interface.components.message_viewer import MessageViewer


def open_advanced_explorer_threaded(parent: ctk.CTkBaseClass,
                                   lang,
                                   guild_obj: Dict[str, Any],
                                   is_source: bool,
                                   on_select: Callable[[str], None]) -> None:
    """
    Thread-safe wrapper for opening the Advanced Explorer.
    This function runs the UI creation in the main thread while handling
    heavy operations (like API calls) in background threads.
    """
    def run_in_main_thread():
        open_advanced_explorer(parent, lang, guild_obj, is_source, on_select)
    
    # Ensure UI creation happens in the main thread
    if threading.current_thread() is threading.main_thread():
        run_in_main_thread()
    else:
        parent.after(0, run_in_main_thread)


def open_advanced_explorer(parent: ctk.CTkBaseClass,
                           lang,
                           guild_obj: Dict[str, Any],
                           is_source: bool,
                           on_select: Callable[[str], None]) -> None:
    """
    Open the Advanced Explorer modal in a Discord-like layout.

    Args:
        parent: The parent tkinter widget (e.g., a frame inside the main window).
        lang: LanguageManager-like object with get_text(key) method.
        guild_obj: Dict with at least 'id' and 'name'.
        is_source: Whether the selection will be used as source or destination.
        on_select: Callback receiving the display string "Name (ID)" when the user confirms selection.
    """
    mode = ctk.get_appearance_mode().lower()
    top = ctk.CTkToplevel(parent)
    gname = guild_obj.get('name', 'Guild')
    gid = str(guild_obj.get('id'))
    title_text = None
    try:
        title_text = lang.get_text("input.guild.explorer_title").format(name=gname)
    except Exception:
        title_text = f"Discord - {gname}"
    top.title(title_text)
    top.geometry("1200x700")
    top.after(10, top.grab_set)   # wait a few ms until window is mapped

    top.configure(fg_color=DiscordColors.get_background_color(mode, "primary"))
    
    # Set minimum size to maintain Discord-like proportions
    top.minsize(800, 600)

    # Discord-style header with server info
    header = ctk.CTkFrame(top, height=48, fg_color=DiscordColors.get_background_color(mode, "secondary"))
    header.pack(fill="x", padx=0, pady=0)
    header.pack_propagate(False)
    
    # Server icon placeholder (Discord-style)
    server_icon_frame = ctk.CTkFrame(header, width=32, height=32, corner_radius=16, 
                                   fg_color=DiscordColors.BLURPLE)
    server_icon_frame.pack(side="left", padx=(16, 12), pady=8)
    server_icon_frame.pack_propagate(False)
    
    # Server icon text (first letter of server name)
    server_icon_text = ctk.CTkLabel(server_icon_frame, text=gname[0].upper() if gname else "S",
                                  font=ctk.CTkFont(size=16, weight="bold"),
                                  text_color="white")
    server_icon_text.pack(expand=True)
    
    # Server name and info
    server_info_frame = ctk.CTkFrame(header, fg_color="transparent")
    server_info_frame.pack(side="left", fill="both", expand=True, pady=8)
    
    server_name = ctk.CTkLabel(server_info_frame, text=gname, 
                             font=ctk.CTkFont(size=16, weight="bold"),
                             text_color=DiscordColors.get_text_color(mode, "normal"))
    server_name.pack(anchor="w")
    
    server_id = ctk.CTkLabel(server_info_frame, text=f"ID: {gid}",
                           font=ctk.CTkFont(size=11),
                           text_color=DiscordColors.get_text_color(mode, "muted"))
    server_id.pack(anchor="w")
    
    # Discord-style close button
    close_btn = ctk.CTkButton(header, text="✕", width=32, height=32, 
                            corner_radius=4, command=top.destroy,
                            fg_color="transparent",
                            text_color=DiscordColors.get_text_color(mode, "muted"),
                            hover_color=DiscordColors.RED,
                            font=ctk.CTkFont(size=14))
    close_btn.pack(side="right", padx=(0, 16), pady=8)

    # Body: Discord-style layout with sidebar and main content
    body = ctk.CTkFrame(top, fg_color="transparent")
    body.pack(fill="both", expand=True, padx=0, pady=0)
    
    # Left sidebar for channels (Discord-style)
    left = ctk.CTkScrollableFrame(body, width=240, fg_color=DiscordColors.get_background_color(mode, "secondary"))
    left.pack(side="left", fill="y")
    left.pack_propagate(False)
    
    # Left sidebar - Discord-style channels list
    sidebar_header = ctk.CTkFrame(left, height=48, fg_color="transparent")
    sidebar_header.pack(fill="x", padx=0, pady=0)
    sidebar_header.pack_propagate(False)
    
    try:
        channels_title_text = lang.get_text("input.guild.channels_list")
    except Exception:
        channels_title_text = "CHANNELS"
    
    channels_title = ctk.CTkLabel(sidebar_header, text=channels_title_text.upper(), 
                                font=ctk.CTkFont(size=12, weight="bold"),
                                text_color=DiscordColors.get_text_color(mode, "muted"))
    channels_title.pack(anchor="w", padx=16, pady=16)
    
    # Separator line (Discord-style)
    separator = ctk.CTkFrame(left, height=1, fg_color=DiscordColors.get_background_color(mode, "tertiary"))
    separator.pack(fill="x", padx=16, pady=(0, 8))
    separator.pack_propagate(False)
    
    # Center panel for channel details and actions
    center = ctk.CTkFrame(body, fg_color=DiscordColors.get_background_color(mode, "primary"))
    center.pack(side="left", fill="both", expand=True)
    
    # Members panel (right sidebar) - Discord-style
    members_frame = ctk.CTkScrollableFrame(body, width=240, fg_color=DiscordColors.get_background_color(mode, "secondary"))
    members_frame.pack(side="right", fill="y")
    members_frame.pack_propagate(False)
    
    # Members panel header
    members_header = ctk.CTkFrame(members_frame, height=48, fg_color="transparent")
    members_header.pack(fill="x", padx=0, pady=0)
    members_header.pack_propagate(False)
    
    try:
        members_title_text = lang.get_text("input.guild.members_list")
    except Exception:
        members_title_text = "MEMBERS"
    
    members_title = ctk.CTkLabel(members_header, text=members_title_text.upper(), 
                                font=ctk.CTkFont(size=12, weight="bold"),
                                text_color=DiscordColors.get_text_color(mode, "muted"))
    members_title.pack(anchor="w", padx=16, pady=16)
    
    # Members separator line
    members_separator = ctk.CTkFrame(members_frame, height=1, fg_color=DiscordColors.get_background_color(mode, "tertiary"))
    members_separator.pack(fill="x", padx=16, pady=(0, 8))
    members_separator.pack_propagate(False)
    
    # Members list container
    members_list_container = ctk.CTkScrollableFrame(members_frame, fg_color="transparent")
    members_list_container.pack(fill="both", expand=True, padx=8, pady=0)
    
    def render_members():
        """Render server members in Discord style"""
        # Clear existing members
        for widget in members_list_container.winfo_children():
            widget.destroy()
        
        if not guild_obj or not hasattr(guild_obj, 'members'):
            # Show placeholder when no members available
            no_members_label = ctk.CTkLabel(members_list_container, 
                                          text="No members available",
                                          font=ctk.CTkFont(size=12),
                                          text_color=DiscordColors.get_text_color(mode, "muted"))
            no_members_label.pack(pady=20)
            return
        
        # Group members by status (online, offline, etc.)
        online_members = []
        offline_members = []
        
        for member in guild_obj.members[:50]:  # Limit to first 50 members for performance
            if hasattr(member, 'status') and str(member.status) == 'online':
                online_members.append(member)
            else:
                offline_members.append(member)
        
        # Render online members section
        if online_members:
            online_header = ctk.CTkLabel(members_list_container, 
                                       text=f"ONLINE — {len(online_members)}",
                                       font=ctk.CTkFont(size=11, weight="bold"),
                                       text_color=DiscordColors.get_text_color(mode, "muted"))
            online_header.pack(anchor="w", padx=8, pady=(8, 4))
            
            for member in online_members:
                render_member_item(member, "online")
        
        # Render offline members section
        if offline_members:
            offline_header = ctk.CTkLabel(members_list_container, 
                                        text=f"OFFLINE — {len(offline_members)}",
                                        font=ctk.CTkFont(size=11, weight="bold"),
                                        text_color=DiscordColors.get_text_color(mode, "muted"))
            offline_header.pack(anchor="w", padx=8, pady=(16, 4))
            
            for member in offline_members[:20]:  # Limit offline members display
                render_member_item(member, "offline")
    
    def render_member_item(member, status):
        """Render individual member item in Discord style"""
        member_frame = ctk.CTkFrame(members_list_container, 
                                  fg_color="transparent",
                                  height=42)
        member_frame.pack(fill="x", padx=4, pady=1)
        member_frame.pack_propagate(False)
        
        # Member content container
        member_content = ctk.CTkFrame(member_frame, fg_color="transparent")
        member_content.pack(fill="both", expand=True, padx=8, pady=6)
        
        # Member avatar (placeholder)
        avatar_frame = ctk.CTkFrame(member_content, width=32, height=32, 
                                  corner_radius=16,
                                  fg_color=DiscordColors.BRAND_COLOR)
        avatar_frame.pack(side="left", padx=(0, 12))
        avatar_frame.pack_propagate(False)
        
        # Avatar text (first letter of username)
        username = str(member.name) if hasattr(member, 'name') else str(member)
        avatar_text = username[0].upper() if username else "?"
        avatar_label = ctk.CTkLabel(avatar_frame, text=avatar_text,
                                  font=ctk.CTkFont(size=14, weight="bold"),
                                  text_color="white")
        avatar_label.pack(expand=True)
        
        # Member info container
        info_container = ctk.CTkFrame(member_content, fg_color="transparent")
        info_container.pack(side="left", fill="both", expand=True)
        
        # Member name
        display_name = getattr(member, 'display_name', username)
        name_color = DiscordColors.get_text_color(mode, "normal") if status == "online" else DiscordColors.get_text_color(mode, "muted")
        
        member_name = ctk.CTkLabel(info_container, text=display_name,
                                 font=ctk.CTkFont(size=14, weight="bold"),
                                 text_color=name_color)
        member_name.pack(anchor="w")
        
        # Member status/activity (if available)
        if hasattr(member, 'activity') and member.activity:
            activity_text = str(member.activity)[:30] + "..." if len(str(member.activity)) > 30 else str(member.activity)
            activity_label = ctk.CTkLabel(info_container, text=activity_text,
                                        font=ctk.CTkFont(size=11),
                                        text_color=DiscordColors.get_text_color(mode, "muted"))
            activity_label.pack(anchor="w")
        
        # Status indicator
        status_colors = {
            "online": "#43b581",
            "idle": "#faa61a", 
            "dnd": "#f04747",
            "offline": "#747f8d"
        }
        
        status_indicator = ctk.CTkFrame(member_content, width=12, height=12,
                                      corner_radius=6,
                                      fg_color=status_colors.get(status, status_colors["offline"]))
        status_indicator.pack(side="right", padx=(8, 0))
        status_indicator.pack_propagate(False)
        
        # Hover effect
        def on_enter(event):
            member_frame.configure(fg_color=DiscordColors.get_interactive_color(mode, "hover"))
        
        def on_leave(event):
            member_frame.configure(fg_color="transparent")
        
        member_frame.bind("<Enter>", on_enter)
        member_frame.bind("<Leave>", on_leave)
    
    # Initial render of members
    render_members()
    
    # Right panel for messages (initially hidden)
    right = ctk.CTkFrame(body, width=400, fg_color=DiscordColors.get_background_color(mode, "primary"))
    # Initially not packed

    # Center panel - Discord-style channel details
    center_content = ctk.CTkFrame(center, fg_color="transparent")
    center_content.pack(fill="both", expand=True, padx=24, pady=24)
    
    # Welcome message area (Discord-style)
    welcome_frame = ctk.CTkFrame(center_content, fg_color=DiscordColors.get_background_color(mode, "secondary"),
                               corner_radius=8)
    welcome_frame.pack(fill="x", pady=(0, 20))
    
    welcome_icon = ctk.CTkLabel(welcome_frame, text="#", font=ctk.CTkFont(size=32, weight="bold"),
                              text_color=DiscordColors.get_text_color(mode, "muted"))
    welcome_icon.pack(pady=(20, 10))
    
    welcome_title = ctk.CTkLabel(welcome_frame, text="Welcome to the Server Explorer",
                               font=ctk.CTkFont(size=20, weight="bold"),
                               text_color=DiscordColors.get_text_color(mode, "normal"))
    welcome_title.pack(pady=(0, 5))
    
    welcome_desc = ctk.CTkLabel(welcome_frame, text="Select a channel from the sidebar to view its details",
                              font=ctk.CTkFont(size=14),
                              text_color=DiscordColors.get_text_color(mode, "muted"))
    welcome_desc.pack(pady=(0, 20))

    # Channel details textbox (Discord-style)
    try:
        details_title_text = lang.get_text("input.guild.channel_details")
    except Exception:
        details_title_text = "Channel Information"
    
    details_frame = ctk.CTkFrame(center_content, fg_color=DiscordColors.get_background_color(mode, "secondary"),
                               corner_radius=8)
    details_frame.pack(fill="x", pady=(0, 20))
    
    details_title = ctk.CTkLabel(details_frame, text=details_title_text,
                               font=ctk.CTkFont(size=16, weight="bold"),
                               text_color=DiscordColors.get_text_color(mode, "normal"))
    details_title.pack(pady=(16, 12), padx=16, anchor="w")
    
    details_box = ctk.CTkTextbox(details_frame, height=120, 
                               fg_color=DiscordColors.get_background_color(mode, "primary"),
                               text_color=DiscordColors.get_text_color(mode, "normal"),
                               corner_radius=6)
    details_box.pack(fill="x", padx=16, pady=(0, 16))
    details_box.configure(state="disabled")

    # Action buttons (Discord-style)
    action_frame = ctk.CTkFrame(center_content, fg_color="transparent")
    action_frame.pack(fill="x")

    view_messages_btn = ctk.CTkButton(action_frame, 
                                    text="📄 " + (lang.get_text("advanced.view_messages") if hasattr(lang, 'get_text') else "Visualizza messaggi"),
                                    command=toggle_messages_panel,
                                    height=40, corner_radius=6,
                                    fg_color=DiscordColors.BLURPLE,
                                    hover_color=DiscordColors.BLURPLE_DARK,
                                    font=ctk.CTkFont(size=14, weight="bold"),
                                    state="disabled")
    view_messages_btn.pack(fill="x", pady=(0, 12))
    
    select_btn = ctk.CTkButton(action_frame,
                             text="✅ " + (lang.get_text("advanced.select_guild") if hasattr(lang, 'get_text') else "Seleziona Server"),
                             command=finalize_selection,
                             height=40, corner_radius=6,
                             fg_color=DiscordColors.GREEN,
                             hover_color=DiscordColors.GREEN,
                             font=ctk.CTkFont(size=14, weight="bold"))
    select_btn.pack(fill="x")
    
    # Right panel already defined above as `right`; keep single instance

    try:
        loading_text = lang.get_text("status.loading")
    except Exception:
        loading_text = "Caricamento..."
    status_lbl = ctk.CTkLabel(center, text=loading_text, text_color=Colors.get_color(Colors.TEXT_MUTED, mode))
    status_lbl.pack(anchor="w", padx=10, pady=(0, 6))
    
    # Message viewer (initially None)
    message_viewer = None
    current_selected_channel = None
    messages_panel_visible = False

    def set_details(text: str):
        details_box.configure(state="normal")
        details_box.delete("1.0", "end")
        details_box.insert("1.0", text)
        details_box.configure(state="disabled")

    def finalize_selection():
        display = f"{gname} ({gid})"
        try:
            on_select(display)
        finally:
            top.destroy()
            
    def toggle_messages_panel():
        """Toggle the visibility of the messages panel with Discord-style animations"""
        nonlocal messages_panel_visible, message_viewer
        if not current_selected_channel:
            return
            
        if not messages_panel_visible:
            # Show messages panel with Discord-style layout
            right.pack(side="right", fill="both", expand=True)
            
            # Resize window to accommodate messages panel (Discord-like width)
            current_width = top.winfo_width()
            new_width = max(current_width, 1400)
            top.geometry(f"{new_width}x{top.winfo_height()}")
            
            # Create message viewer with Discord styling
            if message_viewer is None:
                # Clear any existing content in right panel
                for widget in right.winfo_children():
                    widget.destroy()
                
                # Create Discord-style message header
                msg_header = ctk.CTkFrame(right, height=48, fg_color=DiscordColors.get_background_color(mode, "secondary"))
                msg_header.pack(fill="x", padx=0, pady=0)
                msg_header.pack_propagate(False)
                
                channel_name = current_selected_channel.get('name', 'channel')
                
                # Channel icon and name
                header_content = ctk.CTkFrame(msg_header, fg_color="transparent")
                header_content.pack(fill="both", expand=True, padx=16, pady=12)
                
                channel_icon = ctk.CTkLabel(header_content, text="#", 
                                          font=ctk.CTkFont(size=20, weight="bold"),
                                          text_color=DiscordColors.get_text_color(mode, "muted"))
                channel_icon.pack(side="left", padx=(0, 8))
                
                channel_title = ctk.CTkLabel(header_content, text=channel_name,
                                            font=ctk.CTkFont(size=16, weight="bold"),
                                            text_color=DiscordColors.get_text_color(mode, "normal"))
                channel_title.pack(side="left")
                
                # Close messages button
                close_msg_btn = ctk.CTkButton(header_content, text="✕", width=32, height=32,
                                             corner_radius=4, command=toggle_messages_panel,
                                             fg_color="transparent",
                                             text_color=DiscordColors.get_text_color(mode, "muted"),
                                             hover_color=DiscordColors.get_interactive_color(mode, "hover"),
                                             font=ctk.CTkFont(size=14))
                close_msg_btn.pack(side="right")
                
                # Create message viewer
                main_window = parent.winfo_toplevel()
                token = getattr(main_window, 'verified_token', None) or getattr(getattr(main_window, 'token_input', None), 'entry', None).get()
                message_viewer = MessageViewer(right, lang, token, fg_color="transparent")
                message_viewer.pack(fill="both", expand=True, padx=5, pady=5)
            
            # Load messages for current channel
            asyncio.create_task(message_viewer.load_channel_messages(
                current_selected_channel['id'],
                current_selected_channel['name']
            ))
            
            messages_panel_visible = True
            
            # Update button text
            channel_name = current_selected_channel.get('name', 'channel')
            try:
                view_messages_btn.configure(text=f"📄 {lang.get_text('advanced.hide_messages')} da #{channel_name}")
            except Exception:
                view_messages_btn.configure(text=f"📄 Nascondi messaggi da #{channel_name}")
        else:
            # Hide messages panel
            right.pack_forget()
            
            # Resize window back to original size
            top.geometry("1200x700")
            
            messages_panel_visible = False
            
            # Update button text
            channel_name = current_selected_channel.get('name', 'channel')
            try:
                view_messages_btn.configure(text=f"📄 {lang.get_text('advanced.view_messages')} in #{channel_name}")
            except Exception:
                view_messages_btn.configure(text=f"📄 Visualizza messaggi in #{channel_name}")
            
    def select_channel(ch):
        nonlocal current_selected_channel
        current_selected_channel = ch
        
        # Hide welcome message when channel is selected
        welcome_frame.pack_forget()
        
        # Update details with Discord-style formatting
        ch_name = ch.get('name', 'unknown')
        ch_type = ch.get('type')
        ch_id = ch.get('id')
        topic = ch.get('topic', '')
        position = ch.get('position')
        parent_id = ch.get('parent_id')
        nsfw = ch.get('nsfw', False)
        
        type_names = {
            0: 'Canale di testo',
            2: 'Canale vocale', 
            5: 'Canale annunci',
            13: 'Canale stage',
            15: 'Forum'
        }
        
        details_text = f"📝 Canale: #{ch_name}\n🆔 ID: {ch_id}\n🏷️ Tipo: {type_names.get(ch_type, f'Tipo {ch_type}')}"
        if topic:
            details_text += f"\n📋 Descrizione: {topic}"
        if position is not None:
            details_text += f"\n📍 Posizione: {position}"
        if parent_id:
            details_text += f"\n📁 Categoria ID: {parent_id}"
        if nsfw:
            details_text += f"\n🔞 NSFW: Sì"
            
        set_details(details_text)
        
        # Enable view messages button for text channels with Discord styling
        if ch_type in [0, 5, 15]:  # Text channels, announcement channels, forums
            view_messages_btn.configure(state="normal",
                                      fg_color=DiscordColors.BLURPLE,
                                      hover_color=DiscordColors.BLURPLE_DARK,
                                      text=f"📄 Visualizza messaggi in #{ch_name}")
        else:
            view_messages_btn.configure(state="disabled",
                                      fg_color=DiscordColors.get_background_color(mode, "tertiary"),
                                      text="📄 Visualizza messaggi")
            if messages_panel_visible:
                toggle_messages_panel()  # Hide if currently visible
        
        # Update members panel when channel is selected
            try:
                # Use asyncio.run in thread to handle async operations
                async def async_fetch():
                    async with aiohttp.ClientSession(headers=headers) as session:
                        async with session.get(url) as resp:
                            if resp.status != 200:
                                return None, f"HTTP {resp.status}"
                            return await resp.json(), None
                
                channels, error = asyncio.run(async_fetch())
                
                # Update UI in main thread
                def update_ui():
                    if error:
                        status_lbl.configure(text=error)
                        render_channels([])
                    else:
                        render_channels(channels or [])
                
                top.after(0, update_ui)
                
            except Exception as e:
                # Update UI in main thread
                def update_error():
                    status_lbl.configure(text=str(e))
                    render_channels([])
                
                top.after(0, update_error)
        
        # Run fetch in background thread
        thread = threading.Thread(target=fetch_channels_sync, daemon=True)
        thread.start()
    
    async def fetch_channels():
        """Legacy async function for compatibility"""
        main_window = parent.winfo_toplevel()
        token = getattr(main_window, 'verified_token', None) or getattr(getattr(main_window, 'token_input', None), 'entry', None).get()
        headers = {"Authorization": token, "Content-Type": "application/json"}
        url = f"https://discord.com/api/v10/guilds/{gid}/channels"
        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        status_lbl.configure(text=f"HTTP {resp.status}")
                        return []
                    return await resp.json()
        except Exception as e:
            status_lbl.configure(text=str(e))
            return []

    def render_channels(channels):
        # Clear sidebar (preserve header and separator)
        for w in left.winfo_children():
            if w != sidebar_header and w != separator:
                w.destroy()
        
        # Build maps
        categories = {c['id']: c for c in channels if c.get('type') == 4}
        by_category = {cid: [] for cid in categories.keys()}
        uncategorized = []
        for ch in channels:
            t = ch.get('type')
            if t == 4:
                continue
            parent_id = ch.get('parent_id')
            (by_category[parent_id] if parent_id in by_category else uncategorized).append(ch)
        for lst in by_category.values():
            lst.sort(key=lambda x: (x.get('position', 0), x.get('id')))
        uncategorized.sort(key=lambda x: (x.get('position', 0), x.get('id')))

        def channel_button(parent_widget, ch):
            ch_name = ch.get('name', 'unknown')
            ch_type = ch.get('type')
            # Discord-style icons
            icon_map = {
                0: '#',      # Text channel
                2: '🔊',     # Voice channel  
                5: '📢',     # Announcement channel
                13: '🎤',    # Stage channel
                15: '🔒'     # Forum channel
            }
            icon = icon_map.get(ch_type, '•')
            
            # Discord-style button
            btn_frame = ctk.CTkFrame(parent_widget, fg_color="transparent", height=32)
            btn_frame.pack(fill="x", pady=1)
            btn_frame.pack_propagate(False)
            
            btn = ctk.CTkButton(btn_frame,
                                text=f"{icon} {ch_name}",
                                anchor="w",
                                height=32,
                                corner_radius=4,
                                fg_color="transparent",
                                text_color=DiscordColors.get_text_color(mode, "normal"),
                                hover_color=DiscordColors.get_interactive_color(mode, "hover"),
                                font=ctk.CTkFont(size=14),
                                command=lambda: select_channel(ch))
            btn.pack(fill="both", expand=True, padx=8)

        # Render categories with Discord-style layout
        for cat_id, cat in sorted(categories.items(), key=lambda kv: (kv[1].get('position', 0), kv[0])):
            # Category header
            cat_frame = ctk.CTkFrame(left, fg_color="transparent", height=28)
            cat_frame.pack(fill="x", pady=(12, 4))
            cat_frame.pack_propagate(False)
            
            cat_label = ctk.CTkLabel(cat_frame, 
                                   text=f"▼ {cat.get('name', 'CATEGORIA').upper()}", 
                                   font=ctk.CTkFont(size=11, weight="bold"),
                                   text_color=DiscordColors.get_text_color(mode, "muted"))
            cat_label.pack(anchor="w", padx=16, pady=4)
            
            # Category channels
            for ch in by_category.get(cat_id, []):
                channel_button(cat_frame, ch)

        # Render uncategorized channels
        if uncategorized:
            try:
                no_cat_text = lang.get_text("input.guild.channels_no_category")
            except Exception:
                no_cat_text = "CANALI DI TESTO"
            
            # Section header for uncategorized
            sep_frame = ctk.CTkFrame(left, fg_color="transparent", height=28)
            sep_frame.pack(fill="x", pady=(12, 4))
            sep_frame.pack_propagate(False)
            
            sep = ctk.CTkLabel(sep_frame, 
                             text=no_cat_text.upper(), 
                             font=ctk.CTkFont(size=11, weight="bold"),
                             text_color=DiscordColors.get_text_color(mode, "muted"))
            sep.pack(anchor="w", padx=16, pady=4)
            
            for ch in uncategorized:
                channel_button(left, ch)

        try:
            ready_text = lang.get_text("status.ready")
        except Exception:
            ready_text = "Pronto"
        status_lbl.configure(text=ready_text)

    # Run fetch in background thread to avoid blocking UI
    fetch_channels_threaded()


def create_advanced_explorer_frame(parent: ctk.CTkBaseClass,
                                   lang,
                                   guild_obj: Dict[str, Any],
                                   is_source: bool,
                                   on_select: Callable[[str], None],
                                   on_close: Callable[[], None]) -> ctk.CTkFrame:
    """Create an embeddable Advanced Explorer UI inside a CTkFrame.

    Args:
        parent: The container widget to place the explorer frame into.
        lang: Language manager with get_text(key) method (best effort).
        guild_obj: Dict with at least 'id' and 'name'.
        is_source: Whether the selection is for source or destination (affects label text).
        on_select: Callback invoked with display name "Name (ID)" after confirm.
        on_close: Callback invoked when user clicks the close/back button.

    Returns:
        The created CTkFrame containing the explorer UI. Caller should grid/pack it.
    """
    mode = ctk.get_appearance_mode().lower()
    gname = guild_obj.get('name', 'Guild')
    gid = str(guild_obj.get('id'))

    root = ctk.CTkFrame(parent, fg_color=DiscordColors.get_background_color(mode, "primary"))
    root.grid_propagate(True)

    # Header
    header = ctk.CTkFrame(root, height=48, fg_color=DiscordColors.get_background_color(mode, "secondary"))
    header.pack(fill="x", padx=0, pady=0)
    header.pack_propagate(False)

    # Server icon
    icon_frame = ctk.CTkFrame(header, width=32, height=32, corner_radius=16, fg_color=DiscordColors.BLURPLE)
    icon_frame.pack(side="left", padx=(16, 12), pady=8)
    icon_frame.pack_propagate(False)
    ctk.CTkLabel(icon_frame, text=gname[0].upper() if gname else "S",
                 font=ctk.CTkFont(size=16, weight="bold"), text_color="white").pack(expand=True)

    # Info
    info_frame = ctk.CTkFrame(header, fg_color="transparent")
    info_frame.pack(side="left", fill="both", expand=True, pady=8)
    ctk.CTkLabel(info_frame, text=gname,
                 font=ctk.CTkFont(size=16, weight="bold"),
                 text_color=DiscordColors.get_text_color(mode, "normal")).pack(anchor="w")
    ctk.CTkLabel(info_frame, text=f"ID: {gid}", font=ctk.CTkFont(size=11),
                 text_color=DiscordColors.get_text_color(mode, "muted")).pack(anchor="w")

    # Close/back button
    close_text = "✕"
    close_btn = ctk.CTkButton(header, text=close_text, width=32, height=32,
                              corner_radius=4, command=on_close,
                              fg_color="transparent",
                              text_color=DiscordColors.get_text_color(mode, "muted"),
                              hover_color=DiscordColors.RED,
                              font=ctk.CTkFont(size=14))
    close_btn.pack(side="right", padx=(0, 16), pady=8)

    # Body
    body = ctk.CTkFrame(root, fg_color="transparent")
    body.pack(fill="both", expand=True, padx=0, pady=0)

    # Left sidebar
    left = ctk.CTkScrollableFrame(body, width=240, fg_color=DiscordColors.get_background_color(mode, "secondary"))
    left.pack(side="left", fill="y")
    left.pack_propagate(False)

    sidebar_header = ctk.CTkFrame(left, height=48, fg_color="transparent")
    sidebar_header.pack(fill="x")
    sidebar_header.pack_propagate(False)
    try:
        channels_title_text = lang.get_text("input.guild.channels_list")
    except Exception:
        channels_title_text = "CHANNELS"
    ctk.CTkLabel(sidebar_header, text=channels_title_text.upper(),
                 font=ctk.CTkFont(size=12, weight="bold"),
                 text_color=DiscordColors.get_text_color(mode, "muted")).pack(anchor="w", padx=16, pady=16)
    separator = ctk.CTkFrame(left, height=1, fg_color=DiscordColors.get_background_color(mode, "tertiary"))
    separator.pack(fill="x", padx=16, pady=(0, 8))
    separator.pack_propagate(False)

    # Center and right
    center = ctk.CTkFrame(body, fg_color=DiscordColors.get_background_color(mode, "primary"))
    center.pack(side="left", fill="both", expand=True)
    right = ctk.CTkFrame(body, width=400, fg_color=DiscordColors.get_background_color(mode, "primary"))
    # not packed initially

    center_content = ctk.CTkFrame(center, fg_color="transparent")
    center_content.pack(fill="both", expand=True, padx=24, pady=24)

    welcome_frame = ctk.CTkFrame(center_content, fg_color=DiscordColors.get_background_color(mode, "secondary"), corner_radius=8)
    welcome_frame.pack(fill="x", pady=(0, 20))
    ctk.CTkLabel(welcome_frame, text="#", font=ctk.CTkFont(size=32, weight="bold"),
                 text_color=DiscordColors.get_text_color(mode, "muted")).pack(pady=(20, 10))
    ctk.CTkLabel(welcome_frame, text="Welcome to the Server Explorer",
                 font=ctk.CTkFont(size=20, weight="bold"),
                 text_color=DiscordColors.get_text_color(mode, "normal")).pack(pady=(0, 5))
    ctk.CTkLabel(welcome_frame, text="Select a channel from the sidebar to view its details",
                 font=ctk.CTkFont(size=14),
                 text_color=DiscordColors.get_text_color(mode, "muted")).pack(pady=(0, 20))

    try:
        details_title_text = lang.get_text("input.guild.channel_details")
    except Exception:
        details_title_text = "Channel Information"
    details_frame = ctk.CTkFrame(center_content, fg_color=DiscordColors.get_background_color(mode, "secondary"), corner_radius=8)
    details_frame.pack(fill="x", pady=(0, 20))
    ctk.CTkLabel(details_frame, text=details_title_text,
                 font=ctk.CTkFont(size=16, weight="bold"),
                 text_color=DiscordColors.get_text_color(mode, "normal")).pack(pady=(16, 12), padx=16, anchor="w")
    details_box = ctk.CTkTextbox(details_frame, height=120,
                                 fg_color=DiscordColors.get_background_color(mode, "primary"),
                                 text_color=DiscordColors.get_text_color(mode, "normal"),
                                 corner_radius=6)
    details_box.pack(fill="x", padx=16, pady=(0, 16))
    details_box.configure(state="disabled")

    action_frame = ctk.CTkFrame(center_content, fg_color="transparent")
    action_frame.pack(fill="x")
    try:
        view_label = lang.get_text("advanced.view_messages")
    except Exception:
        view_label = "Visualizza messaggi"
    view_messages_btn = ctk.CTkButton(action_frame, text=f"📄 {view_label}", height=40, corner_radius=6,
                                      fg_color=DiscordColors.BLURPLE, hover_color=DiscordColors.BLURPLE_DARK,
                                      font=ctk.CTkFont(size=14, weight="bold"), state="disabled")
    view_messages_btn.pack(fill="x", pady=(0, 12))

    try:
        sel_label = lang.get_text("advanced.select_guild")
    except Exception:
        sel_label = "Seleziona Server"
    select_btn = ctk.CTkButton(action_frame, text=f"✅ {sel_label}", height=40, corner_radius=6,
                               fg_color=DiscordColors.GREEN, hover_color=DiscordColors.GREEN,
                               font=ctk.CTkFont(size=14, weight="bold"))
    select_btn.pack(fill="x")

    try:
        loading_text = lang.get_text("status.loading")
    except Exception:
        loading_text = "Caricamento..."
    status_lbl = ctk.CTkLabel(center, text=loading_text, text_color=Colors.get_color(Colors.TEXT_MUTED, mode))
    status_lbl.pack(anchor="w", padx=10, pady=(0, 6))

    # Internal state
    message_viewer = None
    current_selected_channel = None
    messages_panel_visible = False
    channels_cache = []

    def set_details(text: str):
        details_box.configure(state="normal")
        details_box.delete("1.0", "end")
        details_box.insert("1.0", text)
        details_box.configure(state="disabled")

    def finalize_selection():
        display = f"{gname} ({gid})"
        try:
            on_select(display)
        finally:
            on_close()

    def toggle_messages_panel():
        nonlocal messages_panel_visible, message_viewer
        if not current_selected_channel:
            return
        if not messages_panel_visible:
            right.pack(side="right", fill="both", expand=True)
            if message_viewer is None:
                for w in right.winfo_children():
                    w.destroy()
                msg_header = ctk.CTkFrame(right, height=48, fg_color=DiscordColors.get_background_color(mode, "secondary"))
                msg_header.pack(fill="x")
                msg_header.pack_propagate(False)
                header_content = ctk.CTkFrame(msg_header, fg_color="transparent")
                header_content.pack(fill="both", expand=True, padx=16, pady=12)
                ctk.CTkLabel(header_content, text="#", font=ctk.CTkFont(size=20, weight="bold"),
                             text_color=DiscordColors.get_text_color(mode, "muted")).pack(side="left", padx=(0, 8))
                ctk.CTkLabel(header_content, text=current_selected_channel.get('name', 'channel'),
                             font=ctk.CTkFont(size=16, weight="bold"),
                             text_color=DiscordColors.get_text_color(mode, "normal")).pack(side="left")
                ctk.CTkButton(header_content, text="✕", width=32, height=32, corner_radius=4,
                              command=toggle_messages_panel, fg_color="transparent",
                              text_color=DiscordColors.get_text_color(mode, "muted"),
                              hover_color=DiscordColors.get_interactive_color(mode, "hover"),
                              font=ctk.CTkFont(size=14)).pack(side="right")
                main_window = root.winfo_toplevel()
                token = getattr(main_window, 'verified_token', None) or getattr(getattr(main_window, 'token_input', None), 'entry', None).get()
                message_viewer = MessageViewer(right, lang, token, fg_color="transparent")
                message_viewer.pack(fill="both", expand=True, padx=5, pady=5)
            asyncio.create_task(message_viewer.load_channel_messages(
                current_selected_channel['id'], current_selected_channel.get('name', 'channel')
            ))
            messages_panel_visible = True
            try:
                view_messages_btn.configure(text=f"📄 {lang.get_text('advanced.hide_messages')} da #{current_selected_channel.get('name','channel')}")
            except Exception:
                view_messages_btn.configure(text=f"📄 Nascondi messaggi da #{current_selected_channel.get('name','channel')}")
        else:
            right.pack_forget()
            messages_panel_visible = False
            try:
                view_messages_btn.configure(text=f"📄 {lang.get_text('advanced.view_messages')} in #{current_selected_channel.get('name','channel')}")
            except Exception:
                view_messages_btn.configure(text=f"📄 Visualizza messaggi in #{current_selected_channel.get('name','channel')}")

    def select_channel(ch):
        nonlocal current_selected_channel
        current_selected_channel = ch
        welcome_frame.pack_forget()
        ch_name = ch.get('name', 'unknown')
        ch_type = ch.get('type')
        ch_id = ch.get('id')
        topic = ch.get('topic', '')
        position = ch.get('position')
        parent_id = ch.get('parent_id')
        nsfw = ch.get('nsfw', False)
        type_names = {0: 'Canale di testo', 2: 'Canale vocale', 5: 'Canale annunci', 13: 'Canale stage', 15: 'Forum'}
        details_text = f"📝 Canale: #{ch_name}\n🆔 ID: {ch_id}\n🏷️ Tipo: {type_names.get(ch_type, f'Tipo {ch_type}')}"
        if topic:
            details_text += f"\n📋 Descrizione: {topic}"
        if position is not None:
            details_text += f"\n📍 Posizione: {position}"
        if parent_id:
            details_text += f"\n📁 Categoria ID: {parent_id}"
        if nsfw:
            details_text += f"\n🔞 NSFW: Sì"
        set_details(details_text)
        if ch_type in [0, 5, 15]:
            view_messages_btn.configure(state="normal",
                                        fg_color=DiscordColors.BLURPLE,
                                        hover_color=DiscordColors.BLURPLE_DARK,
                                        text=f"📄 Visualizza messaggi in #{ch_name}")
        else:
            view_messages_btn.configure(state="disabled",
                                        fg_color=DiscordColors.get_background_color(mode, "tertiary"),
                                        text="📄 Visualizza messaggi")
            if messages_panel_visible:
                toggle_messages_panel()

    def render_channels(channels):
        # Clear sidebar except header+separator
        for w in left.winfo_children():
            if w not in (sidebar_header, separator):
                w.destroy()
        categories = {c['id']: c for c in channels if c.get('type') == 4}
        by_category = {cid: [] for cid in categories.keys()}
        uncategorized = []
        for ch in channels:
            t = ch.get('type')
            if t == 4:
                continue
            parent_id = ch.get('parent_id')
            (by_category[parent_id] if parent_id in by_category else uncategorized).append(ch)
        for lst in by_category.values():
            lst.sort(key=lambda x: (x.get('position', 0), x.get('id')))
        uncategorized.sort(key=lambda x: (x.get('position', 0), x.get('id')))

        def channel_button(parent_widget, ch):
            ch_name = ch.get('name', 'unknown')
            ch_type = ch.get('type')
            icon_map = {0: '#', 2: '🔊', 5: '📢', 13: '🎤', 15: '🔒'}
            icon = icon_map.get(ch_type, '•')
            btn_frame = ctk.CTkFrame(parent_widget, fg_color="transparent", height=32)
            btn_frame.pack(fill="x", pady=1)
            btn_frame.pack_propagate(False)
            btn = ctk.CTkButton(btn_frame, text=f"{icon} {ch_name}", anchor="w", height=32, corner_radius=4,
                                fg_color="transparent",
                                text_color=DiscordColors.get_text_color(mode, "normal"),
                                hover_color=DiscordColors.get_interactive_color(mode, "hover"),
                                font=ctk.CTkFont(size=14), command=lambda: select_channel(ch))
            btn.pack(fill="both", expand=True, padx=8)

        for cat_id, cat in sorted(categories.items(), key=lambda kv: (kv[1].get('position', 0), kv[0])):
            cat_frame = ctk.CTkFrame(left, fg_color="transparent", height=28)
            cat_frame.pack(fill="x", pady=(12, 4))
            cat_frame.pack_propagate(False)
            ctk.CTkLabel(cat_frame, text=f"▼ {cat.get('name', 'CATEGORIA').upper()}",
                         font=ctk.CTkFont(size=11, weight="bold"),
                         text_color=DiscordColors.get_text_color(mode, "muted")).pack(anchor="w", padx=16, pady=4)
            for ch in by_category.get(cat_id, []):
                channel_button(cat_frame, ch)

        if uncategorized:
            try:
                no_cat_text = lang.get_text("input.guild.channels_no_category")
            except Exception:
                no_cat_text = "CANALI DI TESTO"
            sep_frame = ctk.CTkFrame(left, fg_color="transparent", height=28)
            sep_frame.pack(fill="x", pady=(12, 4))
            sep_frame.pack_propagate(False)
            ctk.CTkLabel(sep_frame, text=no_cat_text.upper(),
                         font=ctk.CTkFont(size=11, weight="bold"),
                         text_color=DiscordColors.get_text_color(mode, "muted")).pack(anchor="w", padx=16, pady=4)
            for ch in uncategorized:
                channel_button(left, ch)

        try:
            ready_text = lang.get_text("status.ready")
        except Exception:
            ready_text = "Pronto"
        status_lbl.configure(text=ready_text)

    def fetch_channels_thread():
        try:
            main_window = root.winfo_toplevel()
            token = getattr(main_window, 'verified_token', None) or getattr(getattr(main_window, 'token_input', None), 'entry', None).get()
            headers = {"Authorization": token, "Content-Type": "application/json"}
            url = f"https://discord.com/api/v10/guilds/{gid}/channels"
            async def async_fetch():
                async with aiohttp.ClientSession(headers=headers) as session:
                    async with session.get(url) as resp:
                        if resp.status != 200:
                            return None, f"HTTP {resp.status}"
                        return await resp.json(), None
            channels, error = asyncio.run(async_fetch())
            def update_ui():
                if error:
                    status_lbl.configure(text=error)
                    render_channels([])
                else:
                    nonlocal channels_cache
                    channels_cache = channels or []
                    render_channels(channels_cache)
            root.after(0, update_ui)
        except Exception as e:
            root.after(0, lambda: (status_lbl.configure(text=str(e)), render_channels([])))

    # Wire buttons
    view_messages_btn.configure(command=toggle_messages_panel)
    select_btn.configure(command=finalize_selection)

    # Fetch channels in background
    threading.Thread(target=fetch_channels_thread, daemon=True).start()

    return root
