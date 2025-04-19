class Colors:
    # Main colors
    PRIMARY = "#5865F2"       # Discord Blurple
    PRIMARY_DARK = "#4752C4"  # Dark Blurple
    SECONDARY = "#99AAB5"     # Discord Grey
    
    # Backgrounds
    BACKGROUND = {
        "dark": "#36393F",     # Discord Dark
        "light": "#FFFFFF"     # White
    }
    BACKGROUND_LIGHT = {
        "dark": "#2F3136",     # Lighter Discord Dark
        "light": "#F2F3F5"     # Light gray for light mode
    }
    SETTINGS_BG = {
        "dark": "#2F3136",     # Settings menu background dark
        "light": "#FFFFFF"     # Settings menu background light
    }
    SETTINGS_ITEM_BG = {
        "dark": "#36393F",     # Menu item background dark
        "light": "#F2F3F5"     # Menu item background light
    }
    INPUT_BG = {
        "dark": "#202225",     # Input background dark
        "light": "#EBEDEF"     # Input background light
    }
    
    # Text
    TEXT = {
        "dark": "#DCDDDE",     # Light gray for dark mode
        "light": "#2E3338"     # Dark gray for light mode
    }
    TEXT_MUTED = {
        "dark": "#72767D",     # Gray for dark mode
        "light": "#747F8D"     # Darker gray for light mode
    }
    
    # UI Elements
    BUTTON_BG = {
        "dark": "#FFFFFF",     # White in dark mode
        "light": "#000000"     # Black in light mode
    }
    BUTTON_FG = {
        "dark": "#2F3136",     # Dark background in dark mode
        "light": "#FFFFFF"     # White in light mode
    }
    BUTTON_HOVER = {
        "dark": "#DCDDDE",     # Light gray hover in dark mode
        "light": "#2E3338"     # Dark gray hover in light mode
    }
    
    # Bordi e divisori
    BORDER = {
        "dark": "#2D2F33",     # Bordi scuri in tema scuro
        "light": "#C7CCD1"     # Bordi chiari in tema chiaro
    }
    
    # States
    ERROR = "#ED4245"         # Discord Red
    SUCCESS = "#57F287"       # Discord Green
    WARNING = "#FEE75C"       # Discord Yellow
    LINK = "#00B0F4"          # Discord Blue
    DISABLED = "#72767D"      # Disabled gray
    SUCCESS_DARK = "#45C269"  # Verde più scuro

    @staticmethod
    def get_color(color_dict, mode="dark"):
        """Gets the correct color based on the theme"""
        if isinstance(color_dict, dict):
            return color_dict.get(mode, color_dict["dark"])
        return color_dict