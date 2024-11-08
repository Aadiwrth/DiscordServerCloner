import customtkinter as ctk
from src.interface.utils.validators import is_token_valid
from src.interface.utils.language_manager import LanguageManager
from src.interface.styles.colors import Colors

class TokenInput(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        # Get the language manager
        self.lang = LanguageManager()
        
        # Main frame
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="x", padx=20)
        
        # Label
        self.label = ctk.CTkLabel(
            self.main_frame,
            text=self.lang.get_text("input.token.title"),
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.label.pack(anchor="w", pady=(10, 5))
        
        # Input frame
        self.input_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.input_frame.pack(fill="x")
        
        # Entry
        self.entry = ctk.CTkEntry(
            self.input_frame,
            show="•",
            placeholder_text=self.lang.get_text("input.token.placeholder"),
            height=40
        )
        self.entry.pack(side="left", fill="x", expand=True)
        
        # Show/Hide button
        self.show_button = ctk.CTkButton(
            self.input_frame,
            text="👁",
            width=40,
            command=self.toggle_show_hide,
            fg_color=Colors.get_color(Colors.TEXT, ctk.get_appearance_mode().lower()),
            text_color=Colors.get_color(Colors.BACKGROUND, ctk.get_appearance_mode().lower()),
            hover_color=Colors.get_color(Colors.TEXT_MUTED, ctk.get_appearance_mode().lower())
        )
        self.show_button.pack(side="left", padx=(10, 0))
        
        # Help text with tooltip
        self.help_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.help_frame.pack(fill="x", pady=(5, 10))
        
        self.help_label = ctk.CTkLabel(
            self.help_frame,
            text=self.lang.get_text("input.token.help"),
            text_color=Colors.get_color(Colors.LINK),
            cursor="hand2"
        )
        self.help_label.pack(anchor="w")
        
        # Tooltip frame (initially hidden)
        self.tooltip = None
        self.tooltip_timer = None
        
        # Bind mouse events
        self.help_label.bind("<Enter>", self.schedule_tooltip)
        self.help_label.bind("<Leave>", self.hide_tooltip)
        
        # Add observer for language changes
        self.lang.add_observer(self.update_texts)
        
    def update_texts(self):
        """Update texts when the language changes"""
        self.label.configure(text=self.lang.get_text("input.token.title"))
        self.entry.configure(placeholder_text=self.lang.get_text("input.token.placeholder"))
        self.help_label.configure(text=self.lang.get_text("input.token.help"))
        
        # If the tooltip is visible, update it
        if self.tooltip:
            for child in self.tooltip.winfo_children():
                if isinstance(child, ctk.CTkLabel):
                    child.configure(text=self.lang.get_text("input.token.help_text"))
        
    def schedule_tooltip(self, event):
        """Schedule the appearance of the tooltip after a delay"""
        if self.tooltip_timer:
            self.help_frame.after_cancel(self.tooltip_timer)
        self.tooltip_timer = self.help_frame.after(500, self.show_tooltip)  # 500ms delay
        
    def show_tooltip(self):
        """Show the tooltip"""
        if self.tooltip:
            return
            
        # Create the tooltip as a toplevel window
        self.tooltip = ctk.CTkToplevel()
        self.tooltip.overrideredirect(True)  # Remove window decoration
        
        # Configure the tooltip style
        self.tooltip.configure(fg_color=Colors.get_color(Colors.BACKGROUND_LIGHT))
        
        # Create the tooltip content
        help_text = ctk.CTkLabel(
            self.tooltip,
            text=self.lang.get_text("input.token.help_text"),
            justify="left",
            wraplength=400,
            padx=20,
            pady=20,
            text_color=Colors.get_color(Colors.TEXT)
        )
        help_text.pack()
        
        # Calculate the tooltip position
        x = self.help_label.winfo_rootx()
        y = self.help_label.winfo_rooty() + self.help_label.winfo_height() + 5
        
        # Update the tooltip geometry
        self.tooltip.geometry(f"+{x}+{y}")
        
        # Keep the tooltip above the main window
        self.tooltip.lift()
        self.tooltip.attributes('-topmost', True)
        
    def hide_tooltip(self, event=None):
        """Hide the tooltip"""
        if self.tooltip_timer:
            self.help_frame.after_cancel(self.tooltip_timer)
            self.tooltip_timer = None
            
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None
            
    def toggle_show_hide(self):
        if self.entry.cget("show") == "•":
            self.entry.configure(show="")
            self.show_button.configure(text="🔒")
        else:
            self.entry.configure(show="•")
            self.show_button.configure(text="👁")
            
    def _update_colors(self):
        mode = ctk.get_appearance_mode().lower()
        self.show_button.configure(
            fg_color=Colors.get_color(Colors.TEXT, mode),
            text_color=Colors.get_color(Colors.BACKGROUND, mode),
            hover_color=Colors.get_color(Colors.TEXT_MUTED, mode)
        )
        
        if self.tooltip:
            self.tooltip.configure(fg_color=Colors.get_color(Colors.BACKGROUND_LIGHT, mode))
            for child in self.tooltip.winfo_children():
                if isinstance(child, ctk.CTkLabel):
                    child.configure(text_color=Colors.get_color(Colors.TEXT, mode))