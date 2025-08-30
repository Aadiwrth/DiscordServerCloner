import customtkinter as ctk
from PIL import Image, ImageTk
import os
from src.interface.components.debug_window import DebugWindow
from src.interface.utils.language_manager import LanguageManager
from src.interface.utils.settings_manager import SettingsManager
from src.interface.styles.colors import Colors
from src.interface.utils.version import CURRENT_VERSION, get_latest_version_sync, is_newer
import threading
from tkinter import messagebox
import requests
import io
import json

class SettingsPanel(ctk.CTkFrame):
    def __init__(self, master, width=400, height=None, on_feature_toggle=None):
        super().__init__(
            master, 
            width=width, 
            height=height,
            fg_color=Colors.get_color(Colors.SETTINGS_BG, ctk.get_appearance_mode().lower()),
            border_width=1,
            border_color=Colors.get_color(Colors.TEXT_MUTED, ctk.get_appearance_mode().lower())
        )
        
        # Get the managers
        self.lang = LanguageManager()
        self.settings = SettingsManager()
        self.on_feature_toggle = on_feature_toggle
        
        # Force the specified dimensions
        self.pack_propagate(False)
        
        # Panel header with close button
        self.header = ctk.CTkFrame(self, fg_color="transparent", height=60)
        self.header.pack(fill="x", padx=20, pady=(20, 0))
        
        # Title with icon
        self.title_frame = ctk.CTkFrame(self.header, fg_color="transparent")
        self.title_frame.pack(side="left", padx=10)
        
        try:
            settings_icon = "⚙️"
            self.icon_label = ctk.CTkLabel(
                self.title_frame,
                text=settings_icon,
                font=ctk.CTkFont(size=28)
            )
            self.icon_label.pack(side="left", padx=(0, 15))
        except:
            pass
        
        self.title = ctk.CTkLabel(
            self.title_frame,
            text=self.lang.get_text("settings.title"),
            font=ctk.CTkFont(size=28, weight="bold")
        )
        self.title.pack(side="left")
        
        # Close button with dynamic colors
        self.close_button = ctk.CTkButton(
            self.header,
            text="✕",
            width=45,
            height=45,
            command=lambda: master.toggle_settings(),
            fg_color="transparent",
            text_color=Colors.get_color(Colors.TEXT),
            hover_color=Colors.get_color(Colors.BACKGROUND_LIGHT),
            corner_radius=10
        )
        self.close_button.pack(side="right", padx=10)
        
        # Separator with gradient
        self.separator = ctk.CTkFrame(self, height=2, fg_color=("gray70", "gray30"))
        self.separator.pack(fill="x", padx=20, pady=20)
        
        # Main content frame (no scrolling) with reduced padding
        self.main_content = ctk.CTkFrame(self, fg_color="transparent")
        self.main_content.pack(fill="both", expand=True, padx=10, pady=2)
        
        # Container for settings with grid layout - minimal padding
        self.settings_container = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.settings_container.pack(fill="both", expand=True, padx=2, pady=2)
        self.settings_container.grid_columnconfigure(0, weight=1)
        
        # Sections with hover animations
        self._create_sections()
        
        # Update menu colors
        self._update_colors()
        
        # Add observer for theme change
        self._appearance_mode_changed()  # Initial call
        
    def _create_sections(self):
        # Theme
        self.appearance_frame = self._create_section(
            self.lang.get_text("settings.appearance.title"),
            "🎨"
        )
        
        # Load the saved theme
        saved_theme = self.settings.get_setting("appearance", "theme")
        theme_values = [
            self.lang.get_text("settings.appearance.themes.dark"),
            self.lang.get_text("settings.appearance.themes.light"),
            self.lang.get_text("settings.appearance.themes.system")
        ]
        
        self.appearance_mode_menu = self._create_option_menu(
            self.appearance_frame,
            values=theme_values,
            command=self.change_appearance_mode,
            default_value=self._get_translated_theme(saved_theme)
        )
        
        # Language
        self.language_frame = self._create_section(
            self.lang.get_text("settings.language.title"),
            "🌍"
        )
        # Build language list dynamically from LanguageManager
        self.language_map = self.lang.get_available_languages()  # code -> display name
        current_language_name = self.language_map.get(self.lang.current_language, self.lang.current_language)
        self.language_menu = self._create_option_menu(
            self.language_frame,
            values=list(self.language_map.values()),
            command=self.change_language,
            default_value=current_language_name
        )
        
        # Features
        self.features_frame = self._create_section(
            self.lang.get_text("settings.features.title"),
            "🧩"
        )
        self.advanced_explorer_switch = ctk.CTkSwitch(
            self.features_frame,
            text=self.lang.get_text("settings.features.advanced_explorer"),
            command=self.toggle_advanced_explorer,
            font=ctk.CTkFont(size=12),
            height=24,
            progress_color=("gray70", "gray30")
        )
        # Load saved value
        saved_adv = self.settings.get_setting("features", "advanced_explorer")
        if isinstance(saved_adv, bool):
            self.advanced_explorer_switch.select() if saved_adv else self.advanced_explorer_switch.deselect()
        else:
            self.advanced_explorer_switch.deselect()
        self.advanced_explorer_switch.pack(pady=3, padx=3, anchor="w")
        
        # Debug
        self.debug_frame = self._create_section(
            self.lang.get_text("settings.debug.title"),
            "🔧"
        )
        self._create_debug_section()
        
        # Info (moved to bottom)
        self.info_frame = self._create_section(
            self.lang.get_text("settings.info.title"),
            "ℹ️"
        )
        self._create_info_section()

        # Contributors (below Info)
        self.contributors_frame = self._create_section(
            "Contributors",
            "👥"
        )
        self._create_contributors_section()
        
    def _create_section(self, title, icon=""):
        frame = ctk.CTkFrame(
            self.settings_container,
            fg_color=Colors.get_color(Colors.BACKGROUND_LIGHT, ctk.get_appearance_mode().lower()),
            corner_radius=8
        )
        frame.pack(fill="x", pady=3, padx=3)
        
        header = ctk.CTkFrame(frame, fg_color="transparent", height=28)
        header.pack(fill="x", padx=10, pady=4)
        header.pack_propagate(False)
        
        if icon:
            icon_label = ctk.CTkLabel(
                header,
                text=icon,
                font=ctk.CTkFont(size=16),
                text_color=Colors.get_color(Colors.TEXT, ctk.get_appearance_mode().lower())
            )
            icon_label.pack(side="left", padx=(0, 6))
        
        label = ctk.CTkLabel(
            header,
            text=title,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=Colors.get_color(Colors.TEXT, ctk.get_appearance_mode().lower())
        )
        label.pack(side="left")
        
        content_frame = ctk.CTkFrame(frame, fg_color="transparent")
        content_frame.pack(fill="x", padx=10, pady=(0, 4))
        
        return content_frame
        
    def _create_option_menu(self, parent, values, command, default_value=None):
        menu = ctk.CTkOptionMenu(
            parent,
            values=values,
            command=command,
            width=260,
            height=28,
            dynamic_resizing=False,
            fg_color=("gray75", "gray25"),
            button_color=("gray65", "gray35"),
            button_hover_color=("gray60", "gray40"),
            dropdown_fg_color=("gray80", "gray20"),
            dropdown_hover_color=("gray70", "gray30"),
            font=ctk.CTkFont(size=12)
        )
        
        # Set the default value if specified
        if default_value:
            menu.set(default_value)
            
        menu.pack(pady=3)
        return menu
        
    def _create_debug_section(self):
        # Debug description (expanded for better readability)
        self.debug_description = ctk.CTkTextbox(
            self.debug_frame,
            height=80,
            wrap="word",
            fg_color="transparent",
            activate_scrollbars=False,
            font=ctk.CTkFont(size=12)
        )
        self.debug_description.insert("1.0", self.lang.get_text("settings.debug.description"))
        self.debug_description.configure(state="disabled")
        self.debug_description.pack(pady=(0, 6), padx=5, fill="x")
        
        # Main debug switch
        self.debug_switch = ctk.CTkSwitch(
            self.debug_frame,
            text=self.lang.get_text("settings.debug.enable"),
            command=self.toggle_debug,
            font=ctk.CTkFont(size=13),
            height=26,
            progress_color=("gray70", "gray30")
        )
        self.debug_switch.pack(pady=4, padx=5, anchor="w")
        
        # Frame for debug options
        self.debug_options = ctk.CTkFrame(self.debug_frame, fg_color="transparent")
        
        # Additional debug options (expanded for better readability)
        self.log_file_switch = ctk.CTkSwitch(
            self.debug_options,
            text=self.lang.get_text("settings.debug.save_logs"),
            command=self.toggle_log_file,
            font=ctk.CTkFont(size=12),
            height=24,
            progress_color=("gray70", "gray30")
        )
        self.log_file_switch.pack(pady=3, padx=5, anchor="w")
        
        self.timing_switch = ctk.CTkSwitch(
            self.debug_options,
            text=self.lang.get_text("settings.debug.show_timing"),
            command=self.toggle_timing,
            font=ctk.CTkFont(size=12),
            height=24,
            progress_color=("gray70", "gray30")
        )
        self.timing_switch.pack(pady=3, padx=5, anchor="w")
        
        self.api_switch = ctk.CTkSwitch(
            self.debug_options,
            text=self.lang.get_text("settings.debug.show_api"),
            command=self.toggle_api_details,
            font=ctk.CTkFont(size=12),
            height=24,
            progress_color=("gray70", "gray30")
        )
        self.api_switch.pack(pady=3, padx=5, anchor="w")

    def _create_info_section(self):
        # Credits container with improved styling
        credits_container = ctk.CTkFrame(
            self.info_frame,
            fg_color=("gray90", "gray20"),
            corner_radius=10
        )
        credits_container.pack(fill="x", pady=8, padx=8)
        
        # Title for credits section
        credits_title = ctk.CTkLabel(
            credits_container,
            text="Credits & Support",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("gray20", "gray90")
        )
        credits_title.pack(pady=(10, 5))
        
        # Version
        self.version_label = ctk.CTkLabel(
            credits_container,
            text=self.lang.get_text("settings.info.version", version=CURRENT_VERSION),
            font=ctk.CTkFont(size=12),
            text_color=("gray40", "gray80")
        )
        self.version_label.pack(pady=2)
        
        # Creator label
        self.creator_label = ctk.CTkLabel(
            credits_container,
            text="Created by seregonwar",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("gray30", "gray90")
        )
        self.creator_label.pack(pady=2)
        
        # Buttons container
        buttons_frame = ctk.CTkFrame(credits_container, fg_color="transparent")
        buttons_frame.pack(pady=(8, 4), fill="x")
        
        # GitHub button with improved styling
        self.github_button = ctk.CTkButton(
            buttons_frame,
            text="⚡ GitHub",
            command=self.open_github,
            fg_color=("#24292e", "#f6f8fa"),
            hover_color=("#1c2128", "#e1e4e8"),
            text_color=("white", "black"),
            width=120,
            height=32,
            font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=8
        )
        self.github_button.pack(side="left", padx=(20, 5))
        
        # Check updates button
        self.check_updates_button = ctk.CTkButton(
            buttons_frame,
            text="🔄 Check updates",
            command=self.check_updates,
            fg_color=("#2b6cb0", "#63b3ed"),
            hover_color=("#2c5282", "#4299e1"),
            text_color=("white", "black"),
            width=140,
            height=32,
            font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=8
        )
        self.check_updates_button.pack(side="left", padx=5)
        
        # Ko-fi support button placed below the row of buttons
        self.kofi_button = ctk.CTkButton(
            credits_container,
            text="💖 Ko-fi",
            command=self.open_kofi,
            fg_color=("#ff5f5f", "#ff3030"),
            hover_color=("#ff4040", "#ff1010"),
            text_color="white",
            width=140,
            height=32,
            font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=8
        )
        self.kofi_button.pack(pady=(6, 10), anchor="center")
        
    def _create_contributors_section(self):
        # Brief description and button to open modal
        desc = ctk.CTkLabel(
            self.contributors_frame,
            text="View project contributors",
            font=ctk.CTkFont(size=12)
        )
        desc.pack(anchor="w", padx=6, pady=(2, 4))
        self.contributors_button = ctk.CTkButton(
            self.contributors_frame,
            text="👥 View contributors",
            command=self.open_contributors,
            width=180,
            height=30,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.contributors_button.pack(anchor="w", padx=6, pady=(0, 8))
        
    def change_appearance_mode(self, new_appearance_mode: str):
        """Convert the translated theme name into the actual value and apply it"""
        # Map to convert translated names into actual values
        theme_map = {
            self.lang.get_text("settings.appearance.themes.dark"): "dark",
            self.lang.get_text("settings.appearance.themes.light"): "light",
            self.lang.get_text("settings.appearance.themes.system"): "system"
        }
        
        # Get the actual theme value
        actual_theme = theme_map.get(new_appearance_mode, "dark")
        ctk.set_appearance_mode(actual_theme)
        
        # Update colors immediately
        self._update_colors(actual_theme.lower())
        
        # Save the setting
        self.settings.set_setting("appearance", "theme", actual_theme)
        
    def change_language(self, language_name: str):
        """Handle language change using the correct language codes"""
        # Convert the language name into the code dynamically
        available = self.lang.get_available_languages()
        reverse_map = {v: k for k, v in available.items()}
        language_code = reverse_map.get(language_name)
        if language_code and self.lang.set_language(language_code):
            # Save the setting
            self.settings.set_setting("language", "current", language_code)
            # Update all texts in the interface
            self.update_texts()
        
    def update_texts(self):
        """Update all texts in the interface when the language changes"""
        lang = self.master.lang
        
        # Update the texts of the settings panel
        self.title.configure(text=lang.get_text("settings.title"))
        
        # Update the sections
        for section, (title_key, icon) in {
            "appearance": ("settings.appearance.title", "🎨"),
            "language": ("settings.language.title", "🌍"),
            "debug": ("settings.debug.title", "🔧"),
            "info": ("settings.info.title", "ℹ️")
        }.items():
            frame = getattr(self, f"{section}_frame", None)
            if frame:
                for widget in frame.winfo_children():
                    if isinstance(widget, ctk.CTkLabel) and not widget.cget("text") == icon:
                        widget.configure(text=lang.get_text(title_key))
        
        # Update the dropdown menus
        if hasattr(self, 'appearance_mode_menu'):
            current_theme = ctk.get_appearance_mode().lower()
            theme_values = [
                lang.get_text("settings.appearance.themes.dark"),
                lang.get_text("settings.appearance.themes.light"),
                lang.get_text("settings.appearance.themes.system")
            ]
            self.appearance_mode_menu.configure(values=theme_values)
            
            # Maintain the current theme after language update
            theme_map = {
                "dark": lang.get_text("settings.appearance.themes.dark"),
                "light": lang.get_text("settings.appearance.themes.light"),
                "system": lang.get_text("settings.appearance.themes.system")
            }
            self.appearance_mode_menu.set(theme_map.get(current_theme, theme_values[0]))
        
        if hasattr(self, 'language_menu'):
            # Refresh language values dynamically
            self.language_map = self.lang.get_available_languages()
            self.language_menu.configure(values=list(self.language_map.values()))
            # Maintain current selection
            current_language_name = self.language_map.get(self.lang.current_language, self.lang.current_language)
            self.language_menu.set(current_language_name)
        
        # Update the debug description text
        if hasattr(self, 'debug_description'):
            self.debug_description.configure(state="normal")
            self.debug_description.delete("1.0", "end")
            self.debug_description.insert("1.0", lang.get_text("settings.debug.description"))
            self.debug_description.configure(state="disabled")
        
        # Update the switches
        if hasattr(self, 'debug_switch'):
            self.debug_switch.configure(text=lang.get_text("settings.debug.enable"))
        if hasattr(self, 'log_file_switch'):
            self.log_file_switch.configure(text=lang.get_text("settings.debug.save_logs"))
        if hasattr(self, 'timing_switch'):
            self.timing_switch.configure(text=lang.get_text("settings.debug.show_timing"))
        if hasattr(self, 'api_switch'):
            self.api_switch.configure(text=lang.get_text("settings.debug.show_api"))
        
        # Update the version
        if hasattr(self, 'version_label'):
            self.version_label.configure(text=lang.get_text("settings.info.version", version=CURRENT_VERSION))
        
    def toggle_debug(self):
        is_debug = self.debug_switch.get()
        self.settings.set_setting("debug", "enabled", is_debug)
        
        if is_debug:
            self.debug_options.pack(pady=3, padx=6, fill="x")
            self.master.debug_mode = True
            self.create_debug_window()
        else:
            self.debug_options.pack_forget()
            self.master.debug_mode = False
            if hasattr(self.master, 'debug_window'):
                self.master.debug_window.destroy()
                
    def create_debug_window(self):
        if not hasattr(self.master, 'debug_window'):
            self.master.debug_window = DebugWindow(self.master)
            
    def toggle_log_file(self):
        if hasattr(self, 'log_file_switch'):
            is_enabled = self.log_file_switch.get()
            self.settings.set_setting("debug", "save_logs", is_enabled)
            if is_enabled and hasattr(self.master, 'debug_window'):
                self.master.debug_window.enable_file_logging()
            else:
                self.master.debug_window.disable_file_logging()
        
    def toggle_timing(self):
        if hasattr(self, 'timing_switch'):
            is_enabled = self.timing_switch.get()
            self.settings.set_setting("debug", "show_timing", is_enabled)
            
    def toggle_api_details(self):
        if hasattr(self, 'api_switch'):
            is_enabled = self.api_switch.get()
            self.settings.set_setting("debug", "show_api", is_enabled)
            
    def open_github(self):
        import webbrowser
        webbrowser.open("https://github.com/seregonwar/DiscordServerCloner")
        
    def open_kofi(self):
        import webbrowser
        webbrowser.open("https://ko-fi.com/seregon")
    
    def open_contributors(self):
        # Create modal window
        top = ctk.CTkToplevel(self)
        top.title("Contributors")
        top.geometry("520x600")
        top.grab_set()
        mode = ctk.get_appearance_mode().lower()
        top.configure(fg_color=Colors.get_color(Colors.SETTINGS_BG, mode))

        header = ctk.CTkFrame(top, fg_color="transparent")
        header.pack(fill="x", padx=12, pady=(12, 6))
        title_lbl = ctk.CTkLabel(header, text="Contributors", font=ctk.CTkFont(size=16, weight="bold"))
        title_lbl.pack(side="left")
        close_btn = ctk.CTkButton(header, text="✖", width=36, height=32, command=top.destroy,
                                  fg_color=Colors.get_color(Colors.BACKGROUND_LIGHT, mode),
                                  text_color=Colors.get_color(Colors.TEXT, mode),
                                  hover_color=Colors.get_color(Colors.SETTINGS_ITEM_BG, mode))
        close_btn.pack(side="right")

        body = ctk.CTkFrame(top, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=12, pady=6)
        loading_lbl = ctk.CTkLabel(body, text="Loading contributors…")
        loading_lbl.pack(pady=10)

        # Keep refs
        self._contributors_modal = top
        self._contributors_container = body
        self._contributors_photo_refs = []

        # Try to load cached contributors and render immediately
        cached = self._load_cached_contributors()
        if cached:
            try:
                # Clear loading label and render cached
                for child in list(self._contributors_container.winfo_children()):
                    child.destroy()
                self._render_contributors_list(cached)
                # Show a subtle note
                note = ctk.CTkLabel(self._contributors_container, text="Refreshing list…", text_color=Colors.get_color(Colors.TEXT_MUTED, mode))
                note.pack(pady=(6, 0))
            except Exception:
                pass

        # Start background fetch (will refresh UI and cache if newer)
        threading.Thread(target=self._load_contributors_thread, daemon=True).start()

    def _load_contributors_thread(self):
        url = "https://api.github.com/repos/seregonwar/DiscordServerCloner/contributors?per_page=100&anon=false"
        contributors = []
        error = None
        try:
            resp = requests.get(url, timeout=8)
            if resp.status_code == 200:
                data = resp.json()
                # Filter and sort by contributions desc
                contributors = [
                    {
                        "login": c.get("login"),
                        "html_url": c.get("html_url"),
                        "avatar_url": c.get("avatar_url"),
                        "contributions": int(c.get("contributions", 0))
                    }
                    for c in data if c.get("type") == "User"
                ]
                contributors.sort(key=lambda x: x["contributions"], reverse=True)
            else:
                error = f"GitHub API returned {resp.status_code}"
        except Exception as e:
            error = str(e)

        def finish():
            # Modal might have been closed
            if not hasattr(self, "_contributors_modal") or not self._contributors_modal.winfo_exists():
                return
            if error:
                # If there was an error but cache was shown, keep the cache; else show error
                if not self._contributors_container.winfo_children():
                    ctk.CTkLabel(self._contributors_container, text=f"Unable to load contributors: {error}").pack(pady=10)
                return

            # Save new list to cache and render
            try:
                self._save_cached_contributors(contributors)
            except Exception:
                pass

            # Clear then render updated list
            for child in list(self._contributors_container.winfo_children()):
                child.destroy()
            self._render_contributors_list(contributors)

        self.after(0, finish)

    def _render_contributors_list(self, contributors):
        mode = ctk.get_appearance_mode().lower()
        list_frame = ctk.CTkScrollableFrame(self._contributors_container, fg_color=Colors.get_color(Colors.BACKGROUND_LIGHT, mode))
        list_frame.pack(fill="both", expand=True)
        for c in contributors:
            row = ctk.CTkFrame(list_frame, fg_color="transparent")
            row.pack(fill="x", padx=6, pady=4)

            # Avatar
            photo = None
            try:
                if c.get("avatar_url"):
                    img_resp = requests.get(c["avatar_url"], timeout=6)
                    if img_resp.status_code == 200:
                        image = Image.open(io.BytesIO(img_resp.content)).convert("RGBA")
                        # Use CTkImage for proper HighDPI scaling
                        photo = ctk.CTkImage(light_image=image, dark_image=image, size=(32, 32))
                        self._contributors_photo_refs.append(photo)
            except Exception:
                photo = None

            if photo:
                ctk.CTkLabel(row, image=photo, text="").pack(side="left", padx=(4, 8))
            else:
                placeholder = ctk.CTkLabel(row, text="", width=32, height=32, fg_color=("#ddd", "#333"))
                placeholder.pack(side="left", padx=(4, 8))

            name = c.get("login") or "unknown"
            contribs = c.get("contributions", 0)
            btn = ctk.CTkButton(
                row,
                text=f"{name}  ({contribs})",
                command=lambda url=c.get("html_url"): __import__("webbrowser").open(url),
                height=30,
                width=320,
                fg_color=Colors.get_color(Colors.BUTTON_BG, mode),
                hover_color=Colors.get_color(Colors.BUTTON_HOVER, mode),
                text_color=Colors.get_color(Colors.TEXT, mode)
            )
            btn.pack(side="left", padx=4)

    def _cache_file_path(self):
        # Place cache under project logs directory
        # settings_panel.py is src/interface/components/, go up 4 to project root
        root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../"))
        logs_dir = os.path.join(root, "logs")
        try:
            os.makedirs(logs_dir, exist_ok=True)
        except Exception:
            pass
        return os.path.join(logs_dir, "contributors_cache.json")

    def _load_cached_contributors(self):
        try:
            path = self._cache_file_path()
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, list):
                    # basic validation
                    return [
                        {
                            "login": str(d.get("login")),
                            "html_url": d.get("html_url"),
                            "avatar_url": d.get("avatar_url"),
                            "contributions": int(d.get("contributions", 0))
                        }
                        for d in data
                    ]
        except Exception:
            return None
        return None

    def _save_cached_contributors(self, contributors):
        try:
            path = self._cache_file_path()
            with open(path, "w", encoding="utf-8") as f:
                json.dump(contributors, f)
        except Exception:
            pass
        
    def check_updates(self):
        """Start background check for new releases."""
        if hasattr(self, 'check_updates_button'):
            try:
                self.check_updates_button.configure(state="disabled", text="Checking…")
            except Exception:
                pass
        threading.Thread(target=self._check_updates_thread, daemon=True).start()

    def _check_updates_thread(self):
        """Worker to check the latest GitHub release without blocking UI."""
        try:
            latest = get_latest_version_sync(timeout=6.0)
        except Exception:
            latest = None

        def finish():
            # Restore button
            if hasattr(self, 'check_updates_button'):
                try:
                    self.check_updates_button.configure(state="normal", text="🔄 Check updates")
                except Exception:
                    pass

            if not latest:
                messagebox.showinfo("Updates", "Could not check for updates right now. Please try again later.")
                return

            if is_newer(latest, CURRENT_VERSION):
                res = messagebox.askyesno(
                    "Update available",
                    f"A new version {latest} is available. You are on {CURRENT_VERSION}.\n\nOpen releases page?"
                )
                if res:
                    import webbrowser
                    webbrowser.open("https://github.com/seregonwar/DiscordServerCloner/releases")
            else:
                messagebox.showinfo("Up to date", f"You are on the latest version ({CURRENT_VERSION}).")

        # Switch back to UI thread
        self.after(0, finish)
        
    def toggle_advanced_explorer(self):
        """Toggle advanced explorer feature"""
        state = self.advanced_explorer_switch.get()
        self.settings.set_setting("features", "advanced_explorer", state)
        
        # Notify main window about the change
        try:
            if self.on_feature_toggle:
                self.on_feature_toggle("advanced_explorer", state)
        except Exception:
            pass
        
    def _get_translated_theme(self, theme: str) -> str:
        """Convert the theme name into the translated text"""
        theme_keys = {
            "dark": "settings.appearance.themes.dark",
            "light": "settings.appearance.themes.light",
            "system": "settings.appearance.themes.system"
        }
        return self.lang.get_text(theme_keys.get(theme, "settings.appearance.themes.dark"))
        
    def _appearance_mode_changed(self, *args):
        """Handle theme change"""
        mode = ctk.get_appearance_mode().lower()
        self._update_colors(mode)
        
    def _update_colors(self, mode="dark"):
        """Update colors based on the current theme"""
        # Update the main frame colors
        self.configure(
            fg_color=Colors.get_color(Colors.SETTINGS_BG, mode),
            border_color=Colors.get_color(Colors.TEXT_MUTED, mode)
        )
        
        # Update the section colors
        for section in ["appearance_frame", "language_frame", "debug_frame", "info_frame"]:
            if hasattr(self, section):
                frame = getattr(self, section)
                frame.configure(fg_color=Colors.get_color(Colors.SETTINGS_ITEM_BG, mode))
                
                # Update the text colors in the sections
                for widget in frame.winfo_children():
                    if isinstance(widget, ctk.CTkLabel):
                        widget.configure(text_color=Colors.get_color(Colors.TEXT, mode))
        # Features frame colors
        if hasattr(self, 'features_frame'):
            self.features_frame.configure(fg_color=Colors.get_color(Colors.SETTINGS_ITEM_BG, mode))
            for widget in self.features_frame.winfo_children():
                if isinstance(widget, ctk.CTkLabel):
                    widget.configure(text_color=Colors.get_color(Colors.TEXT, mode))
        
        # Update the menu colors
        for menu in ['appearance_mode_menu', 'language_menu']:
            if hasattr(self, menu):
                getattr(self, menu).configure(
                    text_color=Colors.get_color(Colors.TEXT, mode),
                    fg_color=Colors.get_color(Colors.SETTINGS_ITEM_BG, mode),
                    button_color=Colors.get_color(Colors.BUTTON_BG, mode),
                    button_hover_color=Colors.get_color(Colors.BUTTON_HOVER, mode),
                    dropdown_fg_color=Colors.get_color(Colors.SETTINGS_ITEM_BG, mode),
                    dropdown_hover_color=Colors.get_color(Colors.SETTINGS_BG, mode),
                    dropdown_text_color=Colors.get_color(Colors.TEXT, mode)
                )
        
        # Update the switch colors
        for switch in ['debug_switch', 'log_file_switch', 'timing_switch', 'api_switch', 'advanced_explorer_switch']:
            if hasattr(self, switch):
                getattr(self, switch).configure(
                    text_color=Colors.get_color(Colors.TEXT, mode),
                    button_color=Colors.get_color(Colors.BUTTON_BG, mode),
                    button_hover_color=Colors.get_color(Colors.BUTTON_HOVER, mode),
                    progress_color=Colors.get_color(Colors.TEXT_MUTED, mode)
                )
                
        # Update the debug description text color
        if hasattr(self, 'debug_description'):
            self.debug_description.configure(
                text_color=Colors.get_color(Colors.TEXT, mode)
            )
        # Notify main window about the change
        try:
            if self.on_feature_toggle:
                self.on_feature_toggle("advanced_explorer", state)
        except Exception:
            pass