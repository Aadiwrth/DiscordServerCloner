class Colors:
    """Sistema di colori moderno e migliorato per l'interfaccia"""
    
    # Palette primaria moderna
    PRIMARY = {
        "dark": "#6366F1",    # Indigo moderno
        "light": "#4F46E5"
    }
    
    PRIMARY_HOVER = {
        "dark": "#7C3AED",    # Viola per hover
        "light": "#6366F1"
    }
    
    ACCENT = {
        "dark": "#10B981",    # Verde emerald
        "light": "#059669"
    }
    
    # Grayscale moderno
    GRAY_50 = "#f9fafb"   # Quasi bianco
    GRAY_100 = "#f3f4f6"  # Grigio molto chiaro
    GRAY_200 = "#e5e7eb"  # Grigio chiaro
    GRAY_300 = "#d1d5db"  # Grigio medio-chiaro
    GRAY_400 = "#9ca3af"  # Grigio medio
    GRAY_500 = "#6b7280"  # Grigio
    GRAY_600 = "#4b5563"  # Grigio scuro
    GRAY_700 = "#374151"  # Grigio molto scuro
    GRAY_800 = "#1f2937"  # Grigio quasi nero
    GRAY_900 = "#111827"  # Grigio nero
    
    # Sfondi adattivi
    BACKGROUND = {
        "light": "#ffffff",
        "dark": "#111827"
    }
    BACKGROUND_SECONDARY = {
        "light": "#f9fafb",
        "dark": "#1f2937"
    }
    
    BACKGROUND_TERTIARY = {
        "dark": "#334155",    # Slate 700
        "light": "#F1F5F9"    # Slate 100
    }
    
    # Superfici con elevazione
    SURFACE = {
        "light": "#ffffff",
        "dark": "#1f2937"
    }
    
    SURFACE_ELEVATED = {
        "light": "#f9fafb",
        "dark": "#374151"
    }
    
    # Testo moderno
    TEXT = {
        "light": "#111827",
        "dark": "#f9fafb"
    }
    
    TEXT_SECONDARY = {
        "light": "#6b7280",
        "dark": "#9ca3af"
    }
    
    TEXT_MUTED = {
        "light": "#9ca3af",
        "dark": "#6b7280"
    }
    
    TEXT_DISABLED = {
        "light": "#9ca3af",
        "dark": "#6b7280"
    }
    
    # Bordi moderni
    BORDER = {
        "light": "#e5e7eb",
        "dark": "#4b5563"
    }
    
    BORDER_LIGHT = {
        "light": "#d1d5db",
        "dark": "#6b7280"
    }
    
    BORDER_FOCUS = {
        "light": "#3b82f6",
        "dark": "#60a5fa"
    }
    
    # Stati semantici moderni
    SUCCESS = {
        "light": "#22c55e",
        "dark": "#4ade80"
    }
    
    SUCCESS_BG = {
        "light": "#ecfdf5",
        "dark": "#064e3b"
    }
    
    ERROR = {
        "light": "#ef4444",
        "dark": "#f87171"
    }
    
    ERROR_BG = {
        "light": "#fef2f2",
        "dark": "#7f1d1d"
    }
    
    WARNING = {
        "light": "#f59e0b",
        "dark": "#fbbf24"
    }
    
    WARNING_BG = {
        "light": "#fffbeb",
        "dark": "#78350f"
    }
    
    INFO = {
        "light": "#3b82f6",
        "dark": "#60a5fa"
    }
    
    INFO_BG = {
        "light": "#eff6ff",
        "dark": "#1e3a8a"
    }
    
    # Elementi interattivi
    BUTTON = {
        "dark": "#475569",    # Slate 600
        "light": "#E2E8F0"     # Slate 200
    }
    
    BUTTON_HOVER = {
        "dark": "#64748B",    # Slate 500
        "light": "#CBD5E1"     # Slate 300
    }
    
    BUTTON_ACTIVE = {
        "dark": "#334155",    # Slate 700
        "light": "#94A3B8"     # Slate 400
    }
    
    INPUT = {
        "dark": "#1E293B",    # Slate 800
        "light": "#F8FAFC"     # Slate 50
    }
    
    INPUT_FOCUS = {
        "dark": "#334155",    # Slate 700
        "light": "#FFFFFF"
    }
    
    # Gradienti moderni
    GRADIENT_PRIMARY = {
        "dark": "linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%)",
        "light": "linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%)"
    }
    
    GRADIENT_ACCENT = {
        "dark": "linear-gradient(135deg, #10B981 0%, #059669 100%)",
        "light": "linear-gradient(135deg, #059669 0%, #047857 100%)"
    }
    
    # Ombre semplificate per CustomTkinter
    SHADOW_COLOR = {
        "light": "#e5e7eb",
        "dark": "#374151"
    }
    
    # Compatibilità con il sistema esistente
    MAIN = PRIMARY  # Alias per compatibilità
    MAIN_HOVER = PRIMARY_HOVER  # Alias per compatibilità
    BACKGROUND_LIGHT = BACKGROUND_SECONDARY  # Alias per compatibilità
    SETTINGS_BG = SURFACE  # Alias per compatibilità
    INPUT_BG = INPUT  # Alias per compatibilità
    SUCCESS_DARK = SUCCESS  # Alias per compatibilità
    TEXT_TERTIARY = TEXT_MUTED  # Alias per compatibilità
    LINK = INFO  # Alias per compatibilità
    DISABLED = TEXT_DISABLED  # Alias per compatibilità
    SETTINGS_ITEM_BG = SURFACE_ELEVATED
    BUTTON_BG = PRIMARY
    BUTTON_HOVER = PRIMARY_HOVER
    TEXT_ON_PRIMARY = "#FFFFFF"
    PRIMARY_DARK = "#4752C4"
    
    # Colori Discord specifici (mantenuti per compatibilità)
    DISCORD_BLURPLE = "#5865F2"
    DISCORD_GREEN = "#57F287"
    DISCORD_YELLOW = "#FEE75C"
    DISCORD_FUCHSIA = "#EB459E"
    DISCORD_RED = "#ED4245"
    DISCORD_WHITE = "#FFFFFF"
    DISCORD_BLACK = "#000000"

    @staticmethod
    def get_color(color_dict, theme="dark"):
        """Ottiene il colore appropriato per il tema specificato"""
        if isinstance(color_dict, dict):
            return color_dict.get(theme, color_dict.get("dark"))
        return color_dict
    
    @staticmethod
    def get_color_with_opacity(color_dict, theme="dark", opacity=1.0):
        """Ottiene il colore (opacità non supportata in CustomTkinter)"""
        return Colors.get_color(color_dict, theme)
    
    @staticmethod
    def get_semantic_color(semantic_type, theme="dark", background=False):
        """Ottiene colori semantici (success, error, warning, info)"""
        color_map = {
            "success": Colors.SUCCESS_BG if background else Colors.SUCCESS,
            "error": Colors.ERROR_BG if background else Colors.ERROR,
            "warning": Colors.WARNING_BG if background else Colors.WARNING,
            "info": Colors.INFO_BG if background else Colors.INFO
        }
        return Colors.get_color(color_map.get(semantic_type, Colors.PRIMARY), theme)