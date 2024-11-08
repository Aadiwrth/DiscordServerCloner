import customtkinter as ctk
from PIL import Image
import os
from src.interface.components.header import Header
from src.interface.components.token_input import TokenInput
from src.interface.components.guild_input import GuildInput
from src.interface.components.status_bar import StatusBar
from src.interface.components.settings_panel import SettingsPanel
from src.interface.utils.language_manager import LanguageManager
from src.interface.utils.animations import AnimationManager
from src.interface.utils.settings_manager import SettingsManager

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Initialize the settings manager
        self.settings = SettingsManager()
        
        # Load and apply the saved theme
        saved_theme = self.settings.get_setting("appearance", "theme")
        if saved_theme:
            ctk.set_appearance_mode(saved_theme)
        else:
            ctk.set_appearance_mode("dark")  # default theme
            self.settings.set_setting("appearance", "theme", "dark")
        
        # Initialize the language manager
        self.lang = LanguageManager()
        
        # Load and apply the saved language
        saved_language = self.settings.get_setting("language", "current")
        if saved_language:
            self.lang.set_language(saved_language)
        else:
            self.lang.set_language("en-US")  # default language
            self.settings.set_setting("language", "current", "en-US")
        
        # Register the main window as an observer for language changes
        self.lang.add_observer(self.update_texts)
        
        # Theme configuration
        ctk.set_default_color_theme("blue")
        
        # Window configuration
        self.title(self.lang.get_text("app.title"))
        self.geometry("1000x800")
        self.minsize(900, 700)
        
        # Main grid configuration
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Main container
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(1, weight=1)
        
        # Header
        self.header = Header(self.main_container)
        self.header.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        # Central frame
        self.main_frame = ctk.CTkFrame(self.main_container)
        self.main_frame.grid(row=1, column=0, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Input container
        self.input_container = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.input_container.pack(fill="both", expand=True, padx=40, pady=30)
        
        # Input components
        self.token_input = TokenInput(self.input_container)
        self.token_input.pack(fill="x", pady=(0, 20))
        
        self.guild_input = GuildInput(self.input_container)
        self.guild_input.pack(fill="x")
        
        # Settings Button with icon
        try:
            # Correct path to the image
            settings_image = Image.open(os.path.join("src", "interface", "assets", "settings.png"))
            settings_image = settings_image.convert("RGBA")  # Convert to RGBA for transparency
            
            # Create light and dark versions of the icon
            dark_image = settings_image.copy()
            light_image = settings_image.copy()
            
            # Create the CTk icon
            self.settings_icon = ctk.CTkImage(
                light_image=light_image,
                dark_image=dark_image,
                size=(25, 25)
            )
            
            # Create the button with the icon
            self.settings_button = ctk.CTkButton(
                self,
                text="",
                image=self.settings_icon,
                width=35,
                height=35,
                command=self.toggle_settings,
                fg_color="transparent",
                hover_color=("gray80", "gray30"),
                corner_radius=8
            )
            self.settings_button.place(relx=0.97, rely=0.02, anchor="ne")
            
        except Exception as e:
            print(f"Error loading settings icon: {e}")
            # Fallback to text if the icon cannot be loaded
            self.settings_button = ctk.CTkButton(
                self,
                text="⚙️",
                width=35,
                command=self.toggle_settings
            )
            self.settings_button.place(relx=0.97, rely=0.02, anchor="ne")
        
        # Status bar
        self.status_bar = StatusBar(self)
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky="ew")
        
        # Settings Panel (initially hidden)
        self.settings_panel = SettingsPanel(
            self,
            width=400,
            height=self.winfo_height() - 40
        )
        self.settings_visible = False
        
        # Binding for window resizing
        self.bind("<Configure>", self._on_resize)
        
        # Startup animation
        self.after(100, self.startup_animation)
        
    def update_texts(self):
        """Update all interface texts when the language changes"""
        # Update the window title
        self.title(self.lang.get_text("app.title"))
        
        # Update the header
        self.header.title.configure(text=self.lang.get_text("app.title"))
        self.header.subtitle.configure(text=self.lang.get_text("app.subtitle"))
        
        # Update the token input
        self.token_input.label.configure(text=self.lang.get_text("input.token.title"))
        self.token_input.entry.configure(placeholder_text=self.lang.get_text("input.token.placeholder"))
        self.token_input.help_button.configure(text=self.lang.get_text("input.token.help"))
        
        # Update the guild input
        self.guild_input.source_label.configure(text=self.lang.get_text("input.guild.source.title"))
        self.guild_input.source_entry.configure(placeholder_text=self.lang.get_text("input.guild.source.placeholder"))
        self.guild_input.dest_label.configure(text=self.lang.get_text("input.guild.destination.title"))
        self.guild_input.dest_entry.configure(placeholder_text=self.lang.get_text("input.guild.destination.placeholder"))
        self.guild_input.clone_button.configure(text=self.lang.get_text("input.guild.clone_button"))
        
        # Update the status bar
        self.status_bar.status_label.configure(text=self.lang.get_text("status.ready"))
        
        # Update the settings panel if it exists
        if hasattr(self, 'settings_panel') and self.settings_panel:
            self.settings_panel.update_texts()
    
    def _on_resize(self, event):
        if hasattr(self, 'settings_panel'):
            self.settings_panel.configure(height=self.winfo_height() - 40)
            if self.settings_visible:
                self.settings_panel.grid(row=0, column=2, rowspan=2, sticky="nsew", padx=(0, 20), pady=20)
    
    def toggle_settings(self):
        if self.settings_visible:
            # Hide the panel
            self.settings_panel.grid_remove()
            self.settings_visible = False
            # Restore the main column weight
            self.grid_columnconfigure(1, weight=1)
            self.grid_columnconfigure(2, weight=0)
        else:
            # Show the panel
            self.settings_panel.grid(row=0, column=2, rowspan=2, sticky="nsew", padx=(0, 20), pady=20)
            self.settings_visible = True
            # Adjust the column weights
            self.grid_columnconfigure(1, weight=1)
            self.grid_columnconfigure(2, weight=0)
            
        # Force color update
        mode = ctk.get_appearance_mode().lower()
        self.settings_panel._update_colors(mode)
    
    def startup_animation(self):
        self.attributes('-alpha', 0.0)
        AnimationManager.smooth_fade(self, 0, 1, 500)