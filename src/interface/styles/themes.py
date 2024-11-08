import tkinter as tk
from tkinter import ttk
from src.interface.styles.colors import Colors

class ModernTheme:
    @staticmethod
    def configure_styles():
        # General style configuration
        style = ttk.Style()
        style.theme_use('clam')  # Use 'clam' as the base
        
        # Button configuration
        style.configure(
            'Custom.TButton',
            background=Colors.PRIMARY,
            foreground=Colors.TEXT,
            padding=(20, 10),
            font=('Helvetica', 10, 'bold'),
            borderwidth=0,
            relief='flat'
        )
        style.map('Custom.TButton',
            background=[('active', Colors.PRIMARY_DARK), ('disabled', Colors.DISABLED)],
            foreground=[('disabled', Colors.SECONDARY)]
        )
        
        # Entry configuration
        style.configure(
            'Custom.TEntry',
            fieldbackground=Colors.INPUT_BG,
            foreground=Colors.TEXT,
            padding=10,
            borderwidth=0
        )
        
        # Frame configuration
        style.configure(
            'Custom.TFrame',
            background=Colors.BACKGROUND
        )
        
        # LabelFrame configuration
        style.configure(
            'Custom.TLabelframe',
            background=Colors.BACKGROUND_LIGHT,
            foreground=Colors.TEXT,
            padding=10
        )
        style.configure(
            'Custom.TLabelframe.Label',
            background=Colors.BACKGROUND_LIGHT,
            foreground=Colors.TEXT,
            font=('Helvetica', 10, 'bold')
        )

def apply_theme(window):
    ModernTheme.configure_styles()
    window.configure(bg=Colors.BACKGROUND)
    
    # Apply the dark theme to the window
    window.tk_setPalette(
        background=Colors.BACKGROUND,
        foreground=Colors.TEXT,
        activeBackground=Colors.PRIMARY_DARK,
        activeForeground=Colors.TEXT
    )