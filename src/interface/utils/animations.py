import customtkinter as ctk
from typing import Callable
import math

class AnimationManager:
    @staticmethod
    def smooth_fade(widget: ctk.CTk, start: float, end: float, duration: int, on_complete: Callable = None):
        """
        Executes a smooth opacity transition
        """
        steps = 120  # Increased FPS for smoother animation
        step_time = duration / steps
        
        def animate(current_step=0):
            if current_step <= steps:
                progress = current_step / steps
                # Cubic easing function for more natural movement
                eased = progress * (2 - progress)
                current = start + (end - start) * eased
                
                widget.attributes('-alpha', current)
                widget.after(int(step_time), lambda: animate(current_step + 1))
            elif on_complete:
                on_complete()
                
        animate()
    
    @staticmethod
    def slide_in(widget: ctk.CTkFrame, direction: str = "right", duration: int = 200, on_complete: Callable = None):
        """
        Slides a widget into view with smooth movement
        """
        original_pos = widget.winfo_x(), widget.winfo_y()
        screen_width = widget.winfo_screenwidth()
        
        steps = 120  # Increased FPS
        step_time = duration / steps
        
        def animate(current_step=0):
            if current_step <= steps:
                progress = current_step / steps
                # Elastic easing function for more natural movement
                eased = 1 - math.pow(1 - progress, 5)
                
                if direction == "right":
                    current_x = screen_width - (screen_width - original_pos[0]) * eased
                    widget.place(x=current_x, y=original_pos[1])
                
                widget.after(int(step_time), lambda: animate(current_step + 1))
            elif on_complete:
                on_complete()
                
        animate()
    
    @staticmethod
    def slide_out(widget: ctk.CTkFrame, direction: str = "right", duration: int = 200, on_complete: Callable = None):
        """
        Slides a widget out of view with smooth movement
        """
        original_pos = widget.winfo_x(), widget.winfo_y()
        screen_width = widget.winfo_screenwidth()
        
        steps = 120  # Increased FPS
        step_time = duration / steps
        
        def animate(current_step=0):
            if current_step <= steps:
                progress = current_step / steps
                # Accelerated easing function for more natural exit
                eased = progress * progress
                
                if direction == "right":
                    current_x = original_pos[0] + (screen_width - original_pos[0]) * eased
                    widget.place(x=current_x, y=original_pos[1])
                
                widget.after(int(step_time), lambda: animate(current_step + 1))
            elif on_complete:
                on_complete()
                
        animate()