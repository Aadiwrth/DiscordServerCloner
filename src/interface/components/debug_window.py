import customtkinter as ctk
import time
from datetime import datetime
import os
from src.interface.styles.colors import Colors
from src.interface.utils.language_manager import LanguageManager

class DebugWindow(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        
        # Get the language manager
        self.lang = LanguageManager()
        
        self.title(self.lang.get_text("debug_window.title"))
        self.geometry("800x600")
        
        # Logging configuration
        self.file_logging_enabled = False
        self.show_timing = False
        self.show_api_details = False
        self.log_file = None
        self.start_time = time.time()
        
        # Toolbar
        self.toolbar = ctk.CTkFrame(
            self,
            fg_color=Colors.get_color(Colors.SETTINGS_BG, ctk.get_appearance_mode().lower())
        )
        self.toolbar.pack(fill="x", padx=10, pady=5)
        
        # Clear button
        self.clear_button = ctk.CTkButton(
            self.toolbar,
            text=self.lang.get_text("debug_window.buttons.clear"),
            command=self.clear_log,
            width=100,
            fg_color=Colors.get_color(Colors.TEXT, ctk.get_appearance_mode().lower()),
            text_color=Colors.get_color(Colors.BACKGROUND, ctk.get_appearance_mode().lower()),
            hover_color=Colors.get_color(Colors.TEXT_MUTED, ctk.get_appearance_mode().lower())
        )
        self.clear_button.pack(side="left", padx=5)
        
        # Save button
        self.save_button = ctk.CTkButton(
            self.toolbar,
            text=self.lang.get_text("debug_window.buttons.save"),
            command=self.save_log,
            width=100,
            fg_color=Colors.get_color(Colors.TEXT, ctk.get_appearance_mode().lower()),
            text_color=Colors.get_color(Colors.BACKGROUND, ctk.get_appearance_mode().lower()),
            hover_color=Colors.get_color(Colors.TEXT_MUTED, ctk.get_appearance_mode().lower())
        )
        self.save_button.pack(side="left", padx=5)
        
        # Log area
        self.log_text = ctk.CTkTextbox(
            self,
            fg_color=Colors.get_color(Colors.BACKGROUND_LIGHT, ctk.get_appearance_mode().lower()),
            text_color=Colors.get_color(Colors.TEXT, ctk.get_appearance_mode().lower())
        )
        self.log_text.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Statistics
        self.stats_frame = ctk.CTkFrame(
            self,
            fg_color=Colors.get_color(Colors.SETTINGS_BG, ctk.get_appearance_mode().lower())
        )
        self.stats_frame.pack(fill="x", padx=10, pady=5)
        
        # Labels for statistics
        self.stats_labels = {
            "start_time": ctk.CTkLabel(
                self.stats_frame,
                text=f"{self.lang.get_text('debug_window.stats.start_time')}: -",
                text_color=Colors.get_color(Colors.TEXT, ctk.get_appearance_mode().lower())
            ),
            "elapsed_time": ctk.CTkLabel(
                self.stats_frame,
                text=f"{self.lang.get_text('debug_window.stats.elapsed_time')}: -",
                text_color=Colors.get_color(Colors.TEXT, ctk.get_appearance_mode().lower())
            ),
            "roles_count": ctk.CTkLabel(
                self.stats_frame,
                text=f"{self.lang.get_text('debug_window.stats.roles')}: 0/0",
                text_color=Colors.get_color(Colors.TEXT, ctk.get_appearance_mode().lower())
            ),
            "channels_count": ctk.CTkLabel(
                self.stats_frame,
                text=f"{self.lang.get_text('debug_window.stats.channels')}: 0/0",
                text_color=Colors.get_color(Colors.TEXT, ctk.get_appearance_mode().lower())
            ),
            "errors_count": ctk.CTkLabel(
                self.stats_frame,
                text=f"{self.lang.get_text('debug_window.stats.errors')}: 0",
                text_color=Colors.get_color(Colors.TEXT, ctk.get_appearance_mode().lower())
            )
        }
        
        for label in self.stats_labels.values():
            label.pack(side="left", padx=10)
            
        # Add observer for language changes
        self.lang.add_observer(self.update_texts)
        
        # Binding for theme change
        self.bind('<Configure>', lambda e: self._update_colors())
        
    def _update_colors(self):
        """Update colors based on the current theme"""
        mode = ctk.get_appearance_mode().lower()
        
        # Update frame colors
        self.toolbar.configure(fg_color=Colors.get_color(Colors.SETTINGS_BG, mode))
        self.stats_frame.configure(fg_color=Colors.get_color(Colors.SETTINGS_BG, mode))
        
        # Update button colors
        for button in [self.clear_button, self.save_button]:
            button.configure(
                fg_color=Colors.get_color(Colors.TEXT, mode),
                text_color=Colors.get_color(Colors.BACKGROUND, mode),
                hover_color=Colors.get_color(Colors.TEXT_MUTED, mode)
            )
        
        # Update log colors
        self.log_text.configure(
            fg_color=Colors.get_color(Colors.BACKGROUND_LIGHT, mode),
            text_color=Colors.get_color(Colors.TEXT, mode)
        )
        
        # Update statistics colors
        for label in self.stats_labels.values():
            label.configure(text_color=Colors.get_color(Colors.TEXT, mode))
            
    def update_texts(self):
        """Update texts when the language changes"""
        self.title(self.lang.get_text("debug_window.title"))
        self.clear_button.configure(text=self.lang.get_text("debug_window.buttons.clear"))
        self.save_button.configure(text=self.lang.get_text("debug_window.buttons.save"))
        
        # Update statistics labels
        stats_texts = {
            "start_time": "start_time",
            "elapsed_time": "elapsed_time",
            "roles_count": "roles",
            "channels_count": "channels",
            "errors_count": "errors"
        }
        
        for key, text_key in stats_texts.items():
            current_value = self.stats_labels[key].cget("text").split(": ")[1]
            self.stats_labels[key].configure(
                text=f"{self.lang.get_text(f'debug_window.stats.{text_key}')}: {current_value}"
            )

    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] [{level}] {message}\n"
        
        # Add to textbox
        self.log_text.insert("end", formatted_message)
        self.log_text.see("end")
        
        # If file logging is enabled, write to the file as well
        if self.file_logging_enabled and self.log_file:
            self.log_file.write(formatted_message)
            self.log_file.flush()
        
    def update_stats(self, **kwargs):
        for key, value in kwargs.items():
            if key in self.stats_labels:
                self.stats_labels[key].configure(text=f"{key.replace('_', ' ').title()}: {value}")
                
    def clear_log(self):
        self.log_text.delete("1.0", "end")
        
    def save_log(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"debug_log_{timestamp}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(self.log_text.get("1.0", "end"))
            
    def enable_file_logging(self):
        """Enable file logging"""
        if not self.file_logging_enabled:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"debug_log_{timestamp}.txt"
            
            # Create logs folder if it doesn't exist
            os.makedirs("logs", exist_ok=True)
            
            self.log_file = open(os.path.join("logs", filename), "w", encoding="utf-8")
            self.file_logging_enabled = True
            self.log("File logging enabled", "INFO")
            
    def disable_file_logging(self):
        """Disable file logging"""
        if self.file_logging_enabled and self.log_file:
            self.log("File logging disabled", "INFO")
            self.log_file.close()
            self.log_file = None
            self.file_logging_enabled = False
            
    def on_closing(self):
        """Handle window closing"""
        if self.file_logging_enabled and self.log_file:
            self.log_file.close()
        self.destroy()