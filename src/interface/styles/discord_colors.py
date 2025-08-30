"""Discord-specific color scheme for authentic UI replication."""

class DiscordColors:
    """Discord color palette for authentic UI styling."""
    
    # Primary Discord colors
    BLURPLE = "#5865F2"  # Discord's signature blue
    BLURPLE_DARK = "#4752C4"  # Darker variant for hover states
    BLURPLE_LIGHT = "#7289DA"  # Lighter variant (legacy Discord blue)
    
    # Background colors (Dark theme)
    DARK_PRIMARY = "#36393f"  # Main background
    DARK_SECONDARY = "#2f3136"  # Secondary background (sidebar)
    DARK_TERTIARY = "#202225"  # Tertiary background (channels list)
    DARK_QUATERNARY = "#40444b"  # Input fields, modals
    
    # Background colors (Light theme)
    LIGHT_PRIMARY = "#ffffff"  # Main background
    LIGHT_SECONDARY = "#f2f3f5"  # Secondary background
    LIGHT_TERTIARY = "#e3e5e8"  # Tertiary background
    LIGHT_QUATERNARY = "#ebedef"  # Input fields
    
    # Text colors (Dark theme)
    TEXT_NORMAL_DARK = "#dcddde"  # Primary text
    TEXT_MUTED_DARK = "#72767d"  # Secondary text
    TEXT_FAINT_DARK = "#4f545c"  # Tertiary text
    TEXT_LINK_DARK = "#00b0f4"  # Links
    
    # Text colors (Light theme)
    TEXT_NORMAL_LIGHT = "#2e3338"  # Primary text
    TEXT_MUTED_LIGHT = "#747f8d"  # Secondary text
    TEXT_FAINT_LIGHT = "#99aab5"  # Tertiary text
    TEXT_LINK_LIGHT = "#0067cc"  # Links
    
    # Interactive colors
    INTERACTIVE_NORMAL = "#b9bbbe"  # Normal interactive elements
    INTERACTIVE_HOVER = "#dcddde"  # Hover state
    INTERACTIVE_ACTIVE = "#ffffff"  # Active/selected state
    INTERACTIVE_MUTED = "#4f545c"  # Muted interactive elements
    
    # Channel colors
    CHANNEL_DEFAULT = "#8e9297"  # Default channel text
    CHANNEL_HOVER = "#dcddde"  # Channel hover
    CHANNEL_SELECTED = "#ffffff"  # Selected channel
    CHANNEL_UNREAD = "#ffffff"  # Unread channel
    CHANNEL_LOCKED = "#72767d"  # Locked channel
    
    # Status colors
    GREEN = "#3ba55d"  # Online, success
    YELLOW = "#faa81a"  # Away, warning
    RED = "#ed4245"  # DND, error
    GREY = "#747f8d"  # Offline, disabled
    
    # Message colors
    MESSAGE_HOVER = "#32353b"  # Message hover background
    MESSAGE_MENTION = "#414675"  # Mention background
    MESSAGE_REPLY = "#4f545c"  # Reply line color
    
    # Scrollbar colors
    SCROLLBAR_THIN = "#202225"  # Thin scrollbar
    SCROLLBAR_THUMB = "#1e2124"  # Scrollbar thumb
    SCROLLBAR_TRACK = "#2f3136"  # Scrollbar track
    
    @classmethod
    def get_background_color(cls, mode: str, level: str = "primary") -> str:
        """Get background color based on theme mode and level.
        
        Args:
            mode: 'dark' or 'light'
            level: 'primary', 'secondary', 'tertiary', 'quaternary'
        """
        if mode.lower() == "dark":
            return {
                "primary": cls.DARK_PRIMARY,
                "secondary": cls.DARK_SECONDARY,
                "tertiary": cls.DARK_TERTIARY,
                "quaternary": cls.DARK_QUATERNARY
            }.get(level, cls.DARK_PRIMARY)
        else:
            return {
                "primary": cls.LIGHT_PRIMARY,
                "secondary": cls.LIGHT_SECONDARY,
                "tertiary": cls.LIGHT_TERTIARY,
                "quaternary": cls.LIGHT_QUATERNARY
            }.get(level, cls.LIGHT_PRIMARY)
    
    @classmethod
    def get_text_color(cls, mode: str, variant: str = "normal") -> str:
        """Get text color based on theme mode and variant.
        
        Args:
            mode: 'dark' or 'light'
            variant: 'normal', 'muted', 'faint', 'link'
        """
        if mode.lower() == "dark":
            return {
                "normal": cls.TEXT_NORMAL_DARK,
                "muted": cls.TEXT_MUTED_DARK,
                "faint": cls.TEXT_FAINT_DARK,
                "link": cls.TEXT_LINK_DARK
            }.get(variant, cls.TEXT_NORMAL_DARK)
        else:
            return {
                "normal": cls.TEXT_NORMAL_LIGHT,
                "muted": cls.TEXT_MUTED_LIGHT,
                "faint": cls.TEXT_FAINT_LIGHT,
                "link": cls.TEXT_LINK_LIGHT
            }.get(variant, cls.TEXT_NORMAL_LIGHT)
    
    @classmethod
    def get_channel_color(cls, state: str = "default") -> str:
        """Get channel color based on state.
        
        Args:
            state: 'default', 'hover', 'selected', 'unread', 'locked'
        """
        return {
            "default": cls.CHANNEL_DEFAULT,
            "hover": cls.CHANNEL_HOVER,
            "selected": cls.CHANNEL_SELECTED,
            "unread": cls.CHANNEL_UNREAD,
            "locked": cls.CHANNEL_LOCKED
        }.get(state, cls.CHANNEL_DEFAULT)