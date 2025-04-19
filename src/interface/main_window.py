import customtkinter as ctk
from PIL import Image
import os
from src.interface.components.header import Header
from src.interface.components.token_input import TokenInput
from src.interface.components.guild_input import GuildInput
from src.interface.components.status_bar import StatusBar
from src.interface.components.settings_panel import SettingsPanel
from src.interface.utils.language_manager import LanguageManager
from src.interface.utils.settings_manager import SettingsManager
from src.interface.styles.colors import Colors

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Initialize the settings manager
        self.settings = SettingsManager()
        
        # Token verificato e server trovati
        self.verified_token = None
        self.debug_mode = False
        
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
        self.geometry("1100x800")
        self.minsize(900, 700)
        
        # Icona dell'applicazione
        icon_path = os.path.join("src", "interface", "assets", "discord_logo.png")
        if os.path.exists(icon_path):
            # Non possiamo usare iconbitmap con immagini PNG 
            # quindi non impostiamo l'icona se non è in formato .ico
            pass
        
        # Colori personalizzati
        self.bg_color = Colors.get_color(Colors.BACKGROUND)
        self.accent_color = Colors.PRIMARY
        self.configure(fg_color=self.bg_color)
        
        # Main grid configuration
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Sidebar
        self.sidebar = ctk.CTkFrame(self, fg_color=Colors.get_color(Colors.BACKGROUND_LIGHT), width=250, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)  # Mantiene la larghezza fissa
        
        # Logo container
        self.logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent", height=120)
        self.logo_frame.pack(fill="x", padx=20, pady=20)
        
        # Logo image
        try:
            logo_path = os.path.join("src", "interface", "assets", "logo.png")
            if os.path.exists(logo_path):
                logo_image = Image.open(logo_path)
                logo_photo = ctk.CTkImage(light_image=logo_image, dark_image=logo_image, size=(210, 70))
                self.logo_label = ctk.CTkLabel(self.logo_frame, image=logo_photo, text="")
                self.logo_label.pack(pady=10)
            else:
                # Fallback to text if image doesn't exist
                self.logo_label = ctk.CTkLabel(
                    self.logo_frame, 
                    text=self.lang.get_text("app.title"),
                    font=ctk.CTkFont(size=22, weight="bold")
                )
                self.logo_label.pack(pady=20)
                
                self.subtitle_label = ctk.CTkLabel(
                    self.logo_frame, 
                    text=self.lang.get_text("app.subtitle"),
                    font=ctk.CTkFont(size=12),
                    text_color=Colors.get_color(Colors.TEXT_MUTED)
                )
                self.subtitle_label.pack(pady=(0, 10))
        except Exception as e:
            print(f"Error loading logo: {e}")
            # Fallback to text
            self.logo_label = ctk.CTkLabel(
                self.logo_frame, 
                text=self.lang.get_text("app.title"),
                font=ctk.CTkFont(size=22, weight="bold")
            )
            self.logo_label.pack(pady=20)
            
        # Main container
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(1, weight=1)
        
        # Header
        self.header = Header(self.main_container)
        self.header.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        # Central frame with improved styling
        self.main_frame = ctk.CTkFrame(
            self.main_container,
            fg_color=Colors.get_color(Colors.BACKGROUND_LIGHT),
            corner_radius=10,
            border_width=1,
            border_color=Colors.get_color(Colors.BORDER)
        )
        self.main_frame.grid(row=1, column=0, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Scroll container per supportare contenuti più lunghi
        self.scroll_frame = ctk.CTkScrollableFrame(
            self.main_frame, 
            fg_color="transparent",
            scrollbar_fg_color=Colors.get_color(Colors.BACKGROUND),
            scrollbar_button_color=Colors.PRIMARY,
            scrollbar_button_hover_color=Colors.PRIMARY_DARK
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)
        self.scroll_frame.columnconfigure(0, weight=1)
        
        # Input container
        self.input_container = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        self.input_container.pack(fill="both", expand=True)
        
        # Input components with improved spacing
        self.token_input = TokenInput(self.input_container)
        self.token_input.pack(fill="x", pady=(0, 25))
        
        self.guild_input = GuildInput(self.input_container)
        self.guild_input.pack(fill="x")
        
        # Settings Panel (initially hidden)
        self.settings_panel = SettingsPanel(
            self,
            width=350,
            height=self.winfo_height() - 40
        )
        self.settings_visible = False
        
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
            
            # Create the button with the icon - moved to sidebar
            self.settings_button = ctk.CTkButton(
                self.sidebar,
                text=self.lang.get_text("settings.title"),
                image=self.settings_icon,
                height=40,
                command=self.toggle_settings,
                fg_color="transparent",
                text_color=Colors.get_color(Colors.TEXT),
                hover_color=Colors.get_color(Colors.BACKGROUND),
                anchor="w"
            )
            self.settings_button.pack(fill="x", padx=10, pady=(10, 5), side="bottom")
            
        except Exception as e:
            print(f"Error loading settings icon: {e}")
            # Fallback to text if the icon cannot be loaded
            self.settings_button = ctk.CTkButton(
                self.sidebar,
                text="⚙️ " + self.lang.get_text("settings.title"),
                height=40,
                command=self.toggle_settings,
                fg_color="transparent",
                text_color=Colors.get_color(Colors.TEXT),
                hover_color=Colors.get_color(Colors.BACKGROUND),
                anchor="w"
            )
            self.settings_button.pack(fill="x", padx=10, pady=(10, 5), side="bottom")
        
        # About button in sidebar
        self.about_button = ctk.CTkButton(
            self.sidebar,
            text=self.lang.get_text("settings.info.title"),
            height=40,
            command=self.show_about,
            fg_color="transparent",
            text_color=Colors.get_color(Colors.TEXT),
            hover_color=Colors.get_color(Colors.BACKGROUND),
            anchor="w"
        )
        self.about_button.pack(fill="x", padx=10, pady=5, side="bottom")
        
        # Status bar
        self.status_bar = StatusBar(self)
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky="ew")
        
        # Binding for window resizing
        self.bind("<Configure>", self._on_resize)
        
        # Startup animation
        self.after(100, self.startup_animation)
        
    def show_about(self):
        """Mostra la finestra di about"""
        about_window = ctk.CTkToplevel(self)
        about_window.title(self.lang.get_text("settings.info.title"))
        about_window.geometry("400x300")
        about_window.resizable(False, False)
        about_window.grab_set()  # Modal dialog
        
        # Try to set icon
        try:
            icon_path = os.path.join("src", "interface", "assets", "discord_logo.png")
            # Non possiamo usare iconbitmap con immagini PNG, quindi non impostiamo l'icona
            pass
        except:
            pass
        
        # Center the window
        about_window.update_idletasks()
        width = about_window.winfo_width()
        height = about_window.winfo_height()
        x = (about_window.winfo_screenwidth() // 2) - (width // 2)
        y = (about_window.winfo_screenheight() // 2) - (height // 2)
        about_window.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
        # Content frame
        about_frame = ctk.CTkFrame(about_window, fg_color="transparent")
        about_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # App logo/name
        about_logo_label = ctk.CTkLabel(
            about_frame, 
            text=self.lang.get_text("app.title"),
            font=ctk.CTkFont(size=24, weight="bold")
        )
        about_logo_label.pack(pady=(0, 5))
        
        # Version
        version = "1.0.0"  # Cambia in base alla versione corrente
        version_label = ctk.CTkLabel(
            about_frame, 
            text=self.lang.get_text("settings.info.version").format(version=version),
            font=ctk.CTkFont(size=12),
            text_color=Colors.get_color(Colors.TEXT_MUTED)
        )
        version_label.pack(pady=(0, 20))
        
        # Description
        description = ctk.CTkLabel(
            about_frame,
            text=self.lang.get_text("app.about_description"),
            font=ctk.CTkFont(size=12),
            justify="center",
            wraplength=350
        )
        description.pack(pady=10)
        
        # Credits
        credits = ctk.CTkLabel(
            about_frame,
            text="© 2023",
            font=ctk.CTkFont(size=12),
            text_color=Colors.get_color(Colors.TEXT_MUTED)
        )
        credits.pack(pady=(20, 0))
        
        # Close button
        close_button = ctk.CTkButton(
            about_frame,
            text="OK",
            command=about_window.destroy,
            width=100
        )
        close_button.pack(pady=20)
    
    def update_texts(self):
        """Update all interface texts when the language changes"""
        # Update the window title
        self.title(self.lang.get_text("app.title"))
        
        # Update sidebar
        if hasattr(self, 'logo_label') and not isinstance(self.logo_label, ctk.CTkImage):
            self.logo_label.configure(text=self.lang.get_text("app.title"))
        if hasattr(self, 'subtitle_label'):
            self.subtitle_label.configure(text=self.lang.get_text("app.subtitle"))
        
        # Update buttons
        if hasattr(self, 'settings_button'):
            if hasattr(self.settings_button, 'cget'):
                current_text = self.settings_button.cget("text")
                if current_text:  # Only if it has text (not just icon)
                    self.settings_button.configure(text=self.lang.get_text("settings.title"))
        
        if hasattr(self, 'about_button'):
            self.about_button.configure(text=self.lang.get_text("settings.info.title"))
            
        # Update the header
        self.header.title.configure(text=self.lang.get_text("app.title"))
        self.header.subtitle.configure(text=self.lang.get_text("app.subtitle"))
        
        # Update the token input
        self.token_input.label.configure(text=self.lang.get_text("input.token.title"))
        self.token_input.entry.configure(placeholder_text=self.lang.get_text("input.token.placeholder"))
        self.token_input.help_label.configure(text=self.lang.get_text("input.token.help"))
        self.token_input.verify_button.configure(text=self.lang.get_text("input.token.verify_button"))
        
        # Update the guild input (modificato per i dropdown)
        self.guild_input.source_label.configure(text=self.lang.get_text("input.guild.source.title"))
        
        # Aggiorniamo in base al tipo di input attivo
        if hasattr(self.guild_input, 'source_manual_input') and self.guild_input.source_manual_input:
            self.guild_input.source_entry.configure(placeholder_text=self.lang.get_text("input.guild.source.placeholder"))
        else:
            placeholder = self.lang.get_text("input.guild.dropdown_placeholder")
            if self.guild_input.source_dropdown.get() == "":
                self.guild_input.source_dropdown.set(placeholder)
        
        self.guild_input.dest_label.configure(text=self.lang.get_text("input.guild.destination.title"))
        
        # Aggiorniamo in base al tipo di input attivo
        if hasattr(self.guild_input, 'dest_manual_input') and self.guild_input.dest_manual_input:
            self.guild_input.dest_entry.configure(placeholder_text=self.lang.get_text("input.guild.destination.placeholder"))
        else:
            placeholder = self.lang.get_text("input.guild.dropdown_placeholder")
            if self.guild_input.dest_dropdown.get() == "":
                self.guild_input.dest_dropdown.set(placeholder)
        
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
    
    def startup_animation(self):
        # Nessuna animazione, mostra semplicemente la finestra
        self.attributes('-alpha', 1.0)  # Assicurati che la finestra sia completamente visibile
    
    def toggle_settings(self):
        if self.settings_visible:
            # Nascondi il pannello immediatamente
            self.settings_panel.grid_remove()
            self.settings_visible = False
            # Restore the main column weight
            self.grid_columnconfigure(1, weight=1)
            self.grid_columnconfigure(2, weight=0)
        else:
            # Mostra il pannello immediatamente
            self.settings_panel.grid(row=0, column=2, rowspan=2, sticky="nsew", padx=(0, 20), pady=20)
            self.settings_visible = True
            # Adjust the column weights
            self.grid_columnconfigure(1, weight=1)
            self.grid_columnconfigure(2, weight=0)
            
        # Force color update
        mode = ctk.get_appearance_mode().lower()
        self.settings_panel._update_colors(mode)