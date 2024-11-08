import customtkinter as ctk
from src.interface.utils.language_manager import LanguageManager

class StatusBar(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, height=30)
        
        # Get the language manager
        self.lang = LanguageManager()
        
        self.status_label = ctk.CTkLabel(
            self,
            text=self.lang.get_text("status.ready"),
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(side="left", padx=10)
        
    def update_status(self, message, color=None):
        self.status_label.configure(text=message)
        if color:
            self.status_label.configure(text_color=color)

