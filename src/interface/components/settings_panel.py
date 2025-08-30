import customtkinter as ctk
from PIL import Image, ImageTk
import os
from src.interface.components.debug_window import DebugWindow
from src.interface.utils.language_manager import LanguageManager
from src.interface.utils.settings_manager import SettingsManager
from src.interface.styles.colors import Colors

class SettingsPanel(ctk.CTkFrame):
    def __init__(self, master, width=400, height=None):
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
        
        # Scrollable frame with smooth scroll effect
        self.scrollable_frame = ctk.CTkScrollableFrame(
            self,
            width=width-60,
            height=height-140 if height else master.winfo_height()-180,
            fg_color="transparent",
            scrollbar_button_hover_color=("gray75", "gray25"),
            scrollbar_button_color=("gray70", "gray30")
        )
        self.scrollable_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Container for settings
        self.settings_container = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        self.settings_container.pack(fill="both", expand=True)
        
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
        
        # Map of language codes to displayed names
        self.language_map = {
            "it-IT": self.lang.get_text("settings.language.languages.it-IT"),
            "en-US": self.lang.get_text("settings.language.languages.en-US"),
            "es-ES": self.lang.get_text("settings.language.languages.es-ES"),
            "fr-FR": self.lang.get_text("settings.language.languages.fr-FR"),
            "np-NP": self.lang.get_text("settings.language.languages.np-NP")
        }
        
        # Reverse the map to find the code from the name
        self.reverse_language_map = {v: k for k, v in self.language_map.items()}
        
        # Create the language menu with the current value selected
        current_language_name = self.language_map[self.lang.current_language]
        self.language_menu = self._create_option_menu(
            self.language_frame,
            values=list(self.language_map.values()),
            command=self.change_language,
            default_value=current_language_name
        )
        
        # Debug
        self.debug_frame = self._create_section(
            self.lang.get_text("settings.debug.title"),
            "🔧"
        )
        self._create_debug_section()
        
        # Info
        self.info_frame = self._create_section(
            self.lang.get_text("settings.info.title"),
            "ℹ️"
        )
        self._create_info_section()
        
    def _create_section(self, title, icon=""):
        frame = ctk.CTkFrame(
            self.settings_container,
            fg_color=Colors.get_color(Colors.BACKGROUND_LIGHT, ctk.get_appearance_mode().lower()),
            corner_radius=12
        )
        frame.pack(fill="x", pady=20, padx=10)
        
        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.pack(fill="x", padx=25, pady=20)
        
        if icon:
            icon_label = ctk.CTkLabel(
                header,
                text=icon,
                font=ctk.CTkFont(size=24),
                text_color=Colors.get_color(Colors.TEXT, ctk.get_appearance_mode().lower())
            )
            icon_label.pack(side="left", padx=(0, 15))
        
        label = ctk.CTkLabel(
            header,
            text=title,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=Colors.get_color(Colors.TEXT, ctk.get_appearance_mode().lower())
        )
        label.pack(side="left")
        
        content_frame = ctk.CTkFrame(frame, fg_color="transparent")
        content_frame.pack(fill="x", padx=25, pady=(0, 20))
        
        return content_frame
        
    def _create_option_menu(self, parent, values, command, default_value=None):
        menu = ctk.CTkOptionMenu(
            parent,
            values=values,
            command=command,
            width=300,
            height=40,
            dynamic_resizing=False,
            fg_color=("gray75", "gray25"),
            button_color=("gray65", "gray35"),
            button_hover_color=("gray60", "gray40"),
            dropdown_fg_color=("gray80", "gray20"),
            dropdown_hover_color=("gray70", "gray30"),
            font=ctk.CTkFont(size=14)
        )
        
        # Set the default value if specified
        if default_value:
            menu.set(default_value)
            
        menu.pack(pady=10)
        return menu
        
    def _create_debug_section(self):
        # Debug description
        self.debug_description = ctk.CTkTextbox(
            self.debug_frame,
            height=100,
            wrap="word",
            fg_color="transparent",
            activate_scrollbars=False,
            font=ctk.CTkFont(size=14)
        )
        self.debug_description.insert("1.0", self.lang.get_text("settings.debug.description"))
        self.debug_description.configure(state="disabled")
        self.debug_description.pack(pady=(0, 15), padx=10, fill="x")
        
        # Main debug switch
        self.debug_switch = ctk.CTkSwitch(
            self.debug_frame,
            text=self.lang.get_text("settings.debug.enable"),
            command=self.toggle_debug,
            font=ctk.CTkFont(size=14),
            height=30,
            progress_color=("gray70", "gray30")
        )
        self.debug_switch.pack(pady=10, padx=10, anchor="w")
        
        # Frame for debug options
        self.debug_options = ctk.CTkFrame(self.debug_frame, fg_color="transparent")
        
        # Additional debug options
        self.log_file_switch = ctk.CTkSwitch(
            self.debug_options,
            text=self.lang.get_text("settings.debug.save_logs"),
            command=self.toggle_log_file,
            font=ctk.CTkFont(size=14),
            height=30,
            progress_color=("gray70", "gray30")
        )
        self.log_file_switch.pack(pady=10, padx=10, anchor="w")
        
        self.timing_switch = ctk.CTkSwitch(
            self.debug_options,
            text=self.lang.get_text("settings.debug.show_timing"),
            command=self.toggle_timing,
            font=ctk.CTkFont(size=14),
            height=30,
            progress_color=("gray70", "gray30")
        )
        self.timing_switch.pack(pady=10, padx=10, anchor="w")
        
        self.api_switch = ctk.CTkSwitch(
            self.debug_options,
            text=self.lang.get_text("settings.debug.show_api"),
            command=self.toggle_api_details,
            font=ctk.CTkFont(size=14),
            height=30,
            progress_color=("gray70", "gray30")
        )
        self.api_switch.pack(pady=10, padx=10, anchor="w")

    def _create_info_section(self):
        # Version
        self.version_label = ctk.CTkLabel(
            self.info_frame,
            text=self.lang.get_text("settings.info.version", version="1.0.0"),
            font=ctk.CTkFont(size=14),
            text_color=("gray50", "gray70")
        )
        self.version_label.pack(pady=10)
        
        # Creator label
        self.creator_label = ctk.CTkLabel(
            self.info_frame,
            text="Created by seregonwar",
            font=ctk.CTkFont(size=14),
            text_color=("gray50", "gray70")
        )
        self.creator_label.pack(pady=(0, 10))
        
        # GitHub button
        self.github_button = ctk.CTkButton(
            self.info_frame,
            text="GitHub",
            command=self.open_github,
            fg_color="transparent",
            hover_color=("gray80", "gray30"),
            width=300,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.github_button.pack(pady=5)
        
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
        # Convert the language name into the code
        language_code = self.reverse_language_map.get(language_name)
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
            self.language_menu.configure(values=[
                lang.get_text("settings.language.languages.it-IT"),
                lang.get_text("settings.language.languages.en-US"),
                lang.get_text("settings.language.languages.es-ES"),
                lang.get_text("settings.language.languages.fr-FR"),
                lang.get_text("settings.language.languages.np-NP")
                
            ])
        
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
            self.version_label.configure(text=lang.get_text("settings.info.version", version="1.0.0"))
        
    def toggle_debug(self):
        is_debug = self.debug_switch.get()
        self.settings.set_setting("debug", "enabled", is_debug)
        
        if is_debug:
            self.debug_options.pack(pady=5, padx=10, fill="x")
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
        for switch in ['debug_switch', 'log_file_switch', 'timing_switch', 'api_switch']:
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