import customtkinter as ctk
import discord
import asyncio
import time
import sys
import os
import aiohttp
import webbrowser
import tkinter as tk
import threading
from tkinter import simpledialog, messagebox
import re
from PIL import Image, ImageTk

# Import Colors directly
from src.interface.styles.colors import Colors
from src.operation_file.serverclone import Clone
from src.interface.utils.language_manager import LanguageManager

# Define a custom exception for request errors
class RequestsError(Exception):
    """Custom exception for Discord API request errors"""
    pass

class GuildInput(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        # Get language manager
        self.lang = LanguageManager()
        
        # Main frame
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="x", padx=20)
        
        # Source Guild Frame
        self.source_label = ctk.CTkLabel(
            self.main_frame,
            text=self.lang.get_text("input.guild.source.title"),
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.source_label.pack(anchor="w", pady=(10, 5))
        
        # Source dropdown e input frame
        self.source_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.source_frame.pack(fill="x", pady=(0, 10))
        
        # Dropdown per source (inizialmente vuoto)
        self.source_dropdown = ctk.CTkOptionMenu(
            self.source_frame,
            values=[""],
            command=self.source_selected,
            dynamic_resizing=False,
            height=40,
            width=350
        )
        self.source_dropdown.pack(side="left", fill="x", expand=True)
        self.source_dropdown.set(self.lang.get_text("input.guild.dropdown_placeholder"))
        
        # Configurazione del menu contestuale (tasto destro) sul dropdown source
        self._setup_context_menu(self.source_dropdown, is_source=True)
        
        # Entry per inserimento manuale ID source, inizialmente nascosto
        self.source_entry = ctk.CTkEntry(
            self.source_frame,
            placeholder_text=self.lang.get_text("input.guild.source.placeholder"),
            height=40,
            text_color=Colors.get_color(Colors.TEXT),
            fg_color=Colors.get_color(Colors.INPUT_BG)
        )
        # Non pacchettizziamo ancora, sarà mostrato quando necessario
        
        # Pulsante per passare da dropdown a input manuale
        self.source_toggle = ctk.CTkButton(
            self.source_frame,
            text="⌨️",
            width=40,
            command=self.toggle_source_input,
            fg_color=Colors.get_color(Colors.TEXT, ctk.get_appearance_mode().lower()),
            text_color=Colors.get_color(Colors.BACKGROUND, ctk.get_appearance_mode().lower()),
            hover_color=Colors.get_color(Colors.TEXT_MUTED, ctk.get_appearance_mode().lower())
        )
        self.source_toggle.pack(side="left", padx=(10, 0))
        
        # Destination Guild Frame
        self.dest_label = ctk.CTkLabel(
            self.main_frame,
            text=self.lang.get_text("input.guild.destination.title"),
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.dest_label.pack(anchor="w", pady=(10, 5))
        
        # Destination dropdown e input frame
        self.dest_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.dest_frame.pack(fill="x", pady=(0, 20))
        
        # Dropdown per destination (inizialmente vuoto)
        self.dest_dropdown = ctk.CTkOptionMenu(
            self.dest_frame,
            values=[""],
            command=self.dest_selected,
            dynamic_resizing=False,
            height=40,
            width=300
        )
        self.dest_dropdown.pack(side="left", fill="x", expand=True)
        self.dest_dropdown.set(self.lang.get_text("input.guild.dropdown_placeholder"))
        
        # Configurazione del menu contestuale (tasto destro) sul dropdown destination
        self._setup_context_menu(self.dest_dropdown, is_source=False)
        
        # Entry per inserimento manuale ID destination, inizialmente nascosto
        self.dest_entry = ctk.CTkEntry(
            self.dest_frame,
            placeholder_text=self.lang.get_text("input.guild.destination.placeholder"),
            height=40,
            text_color=Colors.get_color(Colors.TEXT),
            fg_color=Colors.get_color(Colors.INPUT_BG)
        )
        # Non pacchettizziamo ancora, sarà mostrato quando necessario
        
        # Pulsante per creare un nuovo server
        self.create_server_button = ctk.CTkButton(
            self.dest_frame,
            text="➕",
            width=40,
            command=self.create_new_server,
            fg_color=Colors.get_color(Colors.SUCCESS, ctk.get_appearance_mode().lower()),
            text_color=Colors.get_color(Colors.BACKGROUND, ctk.get_appearance_mode().lower()),
            hover_color=Colors.get_color(Colors.SUCCESS_DARK, ctk.get_appearance_mode().lower())
        )
        self.create_server_button.pack(side="left", padx=(10, 0))
        
        # Pulsante per passare da dropdown a input manuale
        self.dest_toggle = ctk.CTkButton(
            self.dest_frame,
            text="⌨️",
            width=40,
            command=self.toggle_dest_input,
            fg_color=Colors.get_color(Colors.TEXT, ctk.get_appearance_mode().lower()),
            text_color=Colors.get_color(Colors.BACKGROUND, ctk.get_appearance_mode().lower()),
            hover_color=Colors.get_color(Colors.TEXT_MUTED, ctk.get_appearance_mode().lower())
        )
        self.dest_toggle.pack(side="left", padx=(10, 0))
        
        # Flag per tenere traccia dell'input attivo
        self.source_manual_input = False
        self.dest_manual_input = False
        
        # Memorizziamo i server recuperati
        self.guilds_dict = {}  # Dizionario id -> details
        
        # Controlli avanzati
        self.controls_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.controls_frame.pack(fill="x", pady=(0, 10))
        
        # Pulsante per resettare i campi
        self.reset_button = ctk.CTkButton(
            self.controls_frame,
            text=self.lang.get_text("input.guild.reset_button"),
            command=self.reset_fields,
            height=30,
            width=100,
            fg_color=Colors.get_color(Colors.BACKGROUND_LIGHT, ctk.get_appearance_mode().lower()),
            text_color=Colors.get_color(Colors.TEXT_MUTED, ctk.get_appearance_mode().lower()),
            hover_color=Colors.get_color(Colors.BACKGROUND, ctk.get_appearance_mode().lower()),
            border_width=1,
            border_color=Colors.get_color(Colors.TEXT_MUTED)
        )
        self.reset_button.pack(side="left", padx=(0, 10))
        
        # Spazio vuoto espandibile
        spacer = ctk.CTkFrame(self.controls_frame, fg_color="transparent", height=30)
        spacer.pack(side="left", fill="x", expand=True)
        
        # Sezione delle opzioni di clonazione
        self.options_frame = ctk.CTkFrame(self.main_frame)
        self.options_frame.pack(fill="x", pady=10)
        
        # Titolo opzioni
        self.options_title = ctk.CTkLabel(
            self.options_frame,
            text=self.lang.get_text("input.guild.options_title"),
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.options_title.pack(anchor="w", pady=(10, 5), padx=10)
        
        # Contenitore per le checkbox
        self.checkboxes_frame = ctk.CTkFrame(self.options_frame, fg_color="transparent")
        self.checkboxes_frame.pack(fill="x", padx=20, pady=5)
        self.checkboxes_frame.grid_columnconfigure(0, weight=1)
        self.checkboxes_frame.grid_columnconfigure(1, weight=1)

        # Opzione Clone Name e Icon
        self.clone_name_icon_var = ctk.BooleanVar(value=True)
        self.clone_name_icon_checkbox = ctk.CTkCheckBox(
            self.checkboxes_frame,
            text=self.lang.get_text("input.guild.option_michelleneous"),  # add this key in your language files
            variable=self.clone_name_icon_var,
            onvalue=True,
            offvalue=False
        )
        self.clone_name_icon_checkbox.grid(row=3, column=0, sticky="w", pady=5)

        # Opzione ruoli
        self.clone_roles_var = ctk.BooleanVar(value=True)
        self.clone_roles_checkbox = ctk.CTkCheckBox(
            self.checkboxes_frame,
            text=self.lang.get_text("input.guild.option_roles"),
            variable=self.clone_roles_var,
            onvalue=True,
            offvalue=False
        )
        self.clone_roles_checkbox.grid(row=0, column=0, sticky="w", pady=5)
        
        # Opzione categorie
        self.clone_categories_var = ctk.BooleanVar(value=True)
        self.clone_categories_checkbox = ctk.CTkCheckBox(
            self.checkboxes_frame,
            text=self.lang.get_text("input.guild.option_categories"),
            variable=self.clone_categories_var,
            onvalue=True,
            offvalue=False
        )
        self.clone_categories_checkbox.grid(row=0, column=1, sticky="w", pady=5)
        
        # Opzione canali testuali
        self.clone_text_channels_var = ctk.BooleanVar(value=True)
        self.clone_text_channels_checkbox = ctk.CTkCheckBox(
            self.checkboxes_frame,
            text=self.lang.get_text("input.guild.option_text_channels"),
            variable=self.clone_text_channels_var,
            onvalue=True,
            offvalue=False
        )
        self.clone_text_channels_checkbox.grid(row=1, column=0, sticky="w", pady=5)
        
        # Opzione canali vocali
        self.clone_voice_channels_var = ctk.BooleanVar(value=True)
        self.clone_voice_channels_checkbox = ctk.CTkCheckBox(
            self.checkboxes_frame,
            text=self.lang.get_text("input.guild.option_voice_channels"),
            variable=self.clone_voice_channels_var,
            onvalue=True,
            offvalue=False
        )
        self.clone_voice_channels_checkbox.grid(row=1, column=1, sticky="w", pady=5)
        
        # Opzione messaggi
        self.clone_messages_var = ctk.BooleanVar(value=True)
        self.clone_messages_checkbox = ctk.CTkCheckBox(
            self.checkboxes_frame,
            text=self.lang.get_text("input.guild.option_messages"),
            variable=self.clone_messages_var,
            onvalue=True,
            offvalue=False,
            command=self.toggle_messages_options
        )
        self.clone_messages_checkbox.grid(row=2, column=0, sticky="w", pady=5)
        
        # Opzione numero massimo di messaggi
        self.messages_limit_frame = ctk.CTkFrame(self.checkboxes_frame, fg_color="transparent")
        self.messages_limit_frame.grid(row=2, column=1, sticky="w", pady=5)
        
        self.messages_limit_label = ctk.CTkLabel(
            self.messages_limit_frame,
            text=self.lang.get_text("input.guild.option_messages_limit")
        )
        self.messages_limit_label.pack(side="left", padx=(0, 5))
        
        self.messages_limit_var = ctk.StringVar(value="100")
        self.messages_limit_entry = ctk.CTkEntry(
            self.messages_limit_frame,
            width=60,
            textvariable=self.messages_limit_var
        )
        self.messages_limit_entry.pack(side="left")
        
        # Progress bar
        self.progress = ctk.CTkProgressBar(self.main_frame)
        self.progress.set(0)
        
        # Info panel (inizialmente nascosto)
        self.info_panel = ctk.CTkFrame(self.main_frame)
        self.info_panel.configure(fg_color=Colors.get_color(Colors.BACKGROUND_LIGHT))
        
        # Creiamo le etichette per le statistiche
        self.stats_title = ctk.CTkLabel(
            self.info_panel,
            text=self.lang.get_text("input.guild.stats_title"),
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.stats_title.pack(anchor="w", pady=(10, 5))
        
        # Contenitore per le statistiche
        self.stats_container = ctk.CTkFrame(self.info_panel, fg_color="transparent")
        self.stats_container.pack(fill="x", padx=10, pady=5)
        self.stats_container.grid_columnconfigure(1, weight=1)
        
        # Statistiche: ruoli
        self.roles_label = ctk.CTkLabel(
            self.stats_container, 
            text=self.lang.get_text("input.guild.stats_roles")
        )
        self.roles_label.grid(row=0, column=0, sticky="w", pady=2)
        
        self.roles_value = ctk.CTkLabel(
            self.stats_container,
            text="0/0"
        )
        self.roles_value.grid(row=0, column=1, sticky="e", pady=2)
        
        # Statistiche: canali
        self.channels_label = ctk.CTkLabel(
            self.stats_container, 
            text=self.lang.get_text("input.guild.stats_channels")
        )
        self.channels_label.grid(row=1, column=0, sticky="w", pady=2)
        
        self.channels_value = ctk.CTkLabel(
            self.stats_container,
            text="0/0"
        )
        self.channels_value.grid(row=1, column=1, sticky="e", pady=2)
        
        # Statistiche: messaggi
        self.messages_label = ctk.CTkLabel(
            self.stats_container, 
            text=self.lang.get_text("input.guild.stats_messages")
        )
        self.messages_label.grid(row=2, column=0, sticky="w", pady=2)
        
        self.messages_value = ctk.CTkLabel(
            self.stats_container,
            text="0"
        )
        self.messages_value.grid(row=2, column=1, sticky="e", pady=2)
        
        # Statistiche: errori
        self.errors_label = ctk.CTkLabel(
            self.stats_container, 
            text=self.lang.get_text("input.guild.stats_errors"),
            text_color="red"
        )
        self.errors_label.grid(row=3, column=0, sticky="w", pady=2)
        
        self.errors_value = ctk.CTkLabel(
            self.stats_container,
            text="0",
            text_color="red"
        )
        self.errors_value.grid(row=3, column=1, sticky="e", pady=2)
        
        # Statistiche: tempo
        self.time_label = ctk.CTkLabel(
            self.stats_container, 
            text=self.lang.get_text("input.guild.stats_time")
        )
        self.time_label.grid(row=4, column=0, sticky="w", pady=2)
        
        self.time_value = ctk.CTkLabel(
            self.stats_container,
            text="00:00"
        )
        self.time_value.grid(row=4, column=1, sticky="e", pady=2)
        
        # Clone Button
        self.clone_button = ctk.CTkButton(
            self.main_frame,
            text=self.lang.get_text("input.guild.clone_button"),
            command=self.start_clone,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=Colors.get_color(Colors.TEXT, ctk.get_appearance_mode().lower()),
            text_color=Colors.get_color(Colors.BACKGROUND, ctk.get_appearance_mode().lower()),
            hover_color=Colors.get_color(Colors.TEXT_MUTED, ctk.get_appearance_mode().lower())
        )
        self.clone_button.pack(pady=10)
        
        # Discord client
        self.client = None
        
        # Update colors when theme changes
        self._update_colors()
        self.bind('<Configure>', lambda e: self._update_colors())
        
        # Add observer for language changes
        self.lang.add_observer(self.update_texts)
        
    def _update_colors(self):
        mode = ctk.get_appearance_mode().lower()
        
        # Update button colors
        self.clone_button.configure(
            fg_color=Colors.get_color(Colors.TEXT, mode),
            text_color=Colors.get_color(Colors.BACKGROUND, mode),
            hover_color=Colors.get_color(Colors.TEXT_MUTED, mode)
        )
        
        # Update input colors
        for entry in [self.source_entry, self.dest_entry]:
            entry.configure(
                text_color=Colors.get_color(Colors.TEXT, mode),
                fg_color=Colors.get_color(Colors.INPUT_BG, mode)
            )

    def update_progress(self, value, show=True):
        """Update progress bar value and visibility"""
        if show and not self.progress.winfo_ismapped():
            self.progress.pack(fill="x", pady=(0, 10))
        elif not show and self.progress.winfo_ismapped():
            self.progress.pack_forget()
        self.progress.set(value)
        
    def toggle_source_input(self):
        """Passa dall'input da dropdown all'input manuale e viceversa"""
        self.source_manual_input = not self.source_manual_input
        
        if self.source_manual_input:
            # Nascondiamo il dropdown e mostriamo l'input manuale
            self.source_dropdown.pack_forget()
            self.source_entry.pack(side="left", fill="x", expand=True)
            self.source_toggle.configure(text="📋")
        else:
            # Nascondiamo l'input manuale e mostriamo il dropdown
            self.source_entry.pack_forget()
            self.source_dropdown.pack(side="left", fill="x", expand=True)
            self.source_toggle.configure(text="⌨️")
            
    def toggle_dest_input(self):
        """Passa dall'input da dropdown all'input manuale e viceversa"""
        self.dest_manual_input = not self.dest_manual_input
        
        if self.dest_manual_input:
            # Nascondiamo il dropdown e mostriamo l'input manuale
            self.dest_dropdown.pack_forget()
            self.dest_entry.pack(side="left", fill="x", expand=True)
            self.dest_toggle.configure(text="📋")
        else:
            # Nascondiamo l'input manuale e mostriamo il dropdown
            self.dest_entry.pack_forget()
            self.dest_dropdown.pack(side="left", fill="x", expand=True)
            self.dest_toggle.configure(text="⌨️")

    def source_selected(self, option):
        """Callback quando un server sorgente viene selezionato"""
        # Se è stato selezionato un vero server (non il placeholder)
        if option in self.guilds_dict:
            # Aggiorniamo lo stato
            main_window = self.winfo_toplevel()
            main_window.status_bar.update_status(
                self.lang.get_text("status.source_selected").format(name=option), 
                "black"
            )
    
    def dest_selected(self, option):
        """Callback quando un server destinazione viene selezionato"""
        # Se è stato selezionato un vero server (non il placeholder)
        if option in self.guilds_dict:
            # Aggiorniamo lo stato
            main_window = self.winfo_toplevel()
            main_window.status_bar.update_status(
                self.lang.get_text("status.destination_selected").format(name=option), 
                "black"
            )
    
    def update_guilds_dropdowns(self, guilds_list):
        """Aggiorna i dropdown con l'elenco dei server disponibili"""
        if not guilds_list:
            return
            
        # Resettiamo i dizionari e le liste
        self.guilds_dict = {}
        server_names = [self.lang.get_text("input.guild.dropdown_placeholder")]
        
        # Popoliamo il dizionario e la lista dei nomi
        for guild in guilds_list:
            guild_id = str(guild['id'])
            guild_name = guild['name']
            display_name = f"{guild_name} ({guild_id})"
            
            self.guilds_dict[display_name] = guild
            server_names.append(display_name)
        
        # Aggiorniamo i dropdown
        self.source_dropdown.configure(values=server_names)
        self.source_dropdown.set(server_names[0])
        
        self.dest_dropdown.configure(values=server_names)
        self.dest_dropdown.set(server_names[0])
        
        # Assicuriamoci che i dropdown siano visibili
        if self.source_manual_input:
            self.toggle_source_input()
        if self.dest_manual_input:
            self.toggle_dest_input()
            
        # Aggiorniamo lo stato
        main_window = self.winfo_toplevel()
        main_window.status_bar.update_status(
            self.lang.get_text("status.guilds_loaded").format(count=len(guilds_list)), 
            "green"
        )

    def reset_fields(self):
        """Cancella i campi di input"""
        # Resettiamo i dropdown
        placeholder = self.lang.get_text("input.guild.dropdown_placeholder")
        self.source_dropdown.set(placeholder)
        self.dest_dropdown.set(placeholder)
        
        # Cancelliamo gli input manuali
        self.source_entry.delete(0, 'end')
        self.dest_entry.delete(0, 'end')
        
        # Resettiamo le opzioni
        self.clone_roles_var.set(True)
        self.clone_categories_var.set(True)
        self.clone_text_channels_var.set(True)
        self.clone_voice_channels_var.set(True)
        self.clone_messages_var.set(True)
        self.messages_limit_var.set("100")
        self.toggle_messages_options()
        
        # Nascondiamo eventuali elementi visibili
        self.update_progress(0, show=False)
        self.hide_stats()
        
        # Reset dello stato
        main_window = self.winfo_toplevel()
        main_window.status_bar.update_status(self.lang.get_text("status.ready"), "black")
        
    def get_source_guild_id(self):
        """Ottiene l'ID del server sorgente selezionato"""
        if self.source_manual_input:
            return self.source_entry.get()
        else:
            selected = self.source_dropdown.get()
            if selected in self.guilds_dict:
                return str(self.guilds_dict[selected]['id'])
            return ""
    
    def get_dest_guild_id(self):
        """Ottiene l'ID del server destinazione selezionato"""
        if self.dest_manual_input:
            return self.dest_entry.get()
        else:
            selected = self.dest_dropdown.get()
            if selected in self.guilds_dict:
                return str(self.guilds_dict[selected]['id'])
            return ""

    def start_clone(self):
        """Start the cloning process"""
        # Get token from token input
        main_window = self.winfo_toplevel()
        token = main_window.verified_token if hasattr(main_window, 'verified_token') else main_window.token_input.entry.get()
        source_id = self.get_source_guild_id()
        dest_id = self.get_dest_guild_id()
        
        # Validazione migliorata
        error_message = None
        
        if not token:
            error_message = self.lang.get_text("input.token.error_empty")
        elif not source_id:
            error_message = self.lang.get_text("input.guild.source.error_empty")
        elif not dest_id:
            error_message = self.lang.get_text("input.guild.destination.error_empty")
        elif source_id == dest_id:
            error_message = self.lang.get_text("input.guild.error_same_ids")
        
        # Validazione formato IDs
        if not error_message:
            try:
                int(source_id)
                int(dest_id)
            except ValueError:
                error_message = self.lang.get_text("input.guild.error_invalid_id")
        
        # Validazione del limite messaggi
        if not error_message and self.clone_messages_var.get():
            try:
                messages_limit = int(self.messages_limit_var.get())
                if messages_limit <= 0:
                    error_message = self.lang.get_text("input.guild.error_invalid_limit")
            except ValueError:
                error_message = self.lang.get_text("input.guild.error_invalid_limit")
        
        # Mostra errore se presente
        if error_message:
            main_window.status_bar.update_status(error_message, "red")
            return
            
        # Disable clone button during process
        self.clone_button.configure(state="disabled")
        main_window.status_bar.update_status(
            self.lang.get_text("status.cloning"), 
            "blue"
        )
        
        # Mostra la progress bar
        self.update_progress(0, True)
        
        # Esegui il clone
        asyncio.run(self._clone_guild(token, source_id, dest_id))
    
    async def _clone_guild(self, token, source_id, dest_id):
        """Execute server cloning process using REST API"""
        main_window = self.winfo_toplevel()
        connector = None
        try:
            # Creiamo un connector sicuro per evitare memory leak
            connector = aiohttp.TCPConnector(force_close=True)
            
            # Prepariamo l'header per le richieste API - assicuriamoci che il token sia nel formato corretto
            if not token.startswith("Bot ") and not token.startswith("Bearer "):
                # Se non è specificato il tipo di token, assumiamo che sia un user token
                auth_token = token
            else:
                auth_token = token
                
            headers = {
                "Authorization": auth_token,
                "Content-Type": "application/json"
            }
            
            # Mostriamo la barra di progresso e impostiamo a 0
            self.update_progress(0, show=True)
            
            # Nascondiamo le statistiche all'inizio
            self.hide_stats()
            
            # Creiamo il cloner
            cloner = Clone(self._debug_log)
            
            # Timer per aggiornare le statistiche
            stats_timer = None
            
            # Configuriamo una funzione per aggiornare la barra di progresso
            def progress_callback(progress_percentage):
                # Convertiamo il progresso in un valore tra 0.1 e 0.9
                progress_value = 0.1 + (progress_percentage * 0.8)
                self.update_progress(progress_value)
            
            # Passiamo la callback al cloner
            cloner.set_progress_callback(progress_callback)
            
            # Verifichiamo l'accesso ai server source e destination
            async with aiohttp.ClientSession(connector=connector, headers=headers) as session:
                # Verifichiamo il server source
                self._debug_log(f"Verifico accesso al server source (ID: {source_id})")
                source_url = f"https://discord.com/api/v10/guilds/{source_id}"
                async with session.get(source_url) as source_response:
                    if source_response.status != 200:
                        self._debug_log(f"Errore nell'accesso al server source: {source_response.status}", "ERROR")
                        self.update_progress(0, show=False)  # Nascondiamo la barra di progresso
                        return
                    
                    source_data = await source_response.json()
                    source_name = source_data.get("name", "Unknown")
                    self._debug_log(f"Accesso al server source verificato: {source_name}")
                
                # Verifichiamo il server destination
                self._debug_log(f"Verifico accesso al server destination (ID: {dest_id})")
                dest_url = f"https://discord.com/api/v10/guilds/{dest_id}"
                async with session.get(dest_url) as dest_response:
                    if dest_response.status != 200:
                        self._debug_log(f"Errore nell'accesso al server destination: {dest_response.status}", "ERROR")
                        self.update_progress(0, show=False)  # Nascondiamo la barra di progresso
                        return
                    
                    dest_data = await dest_response.json()
                    dest_name = dest_data.get("name", "Unknown")
                    self._debug_log(f"Accesso al server destination verificato: {dest_name}")
                
                # Aggiorniamo la barra di progresso al 10%
                self.update_progress(0.1)
                
                # Configuriamo un timer per aggiornare le statistiche ogni secondo
                async def update_stats_timer():
                    try:
                        while True:
                            self.update_stats(cloner.get_stats())
                            await asyncio.sleep(1)
                    except asyncio.CancelledError:
                        # Gestiamo la cancellazione pulita del task
                        pass
                
                # Avviamo il timer in un task separato
                stats_timer = asyncio.create_task(update_stats_timer())
                
                # Avviamo la clonazione con le opzioni
                try:
                    self._debug_log(f"Avvio clonazione da {source_name} a {dest_name}")
                    success = await cloner.start_clone(
                        guild_from=source_data,
                        guild_to=dest_data,
                        session=session,
                        options={
                            "clone_roles": self.clone_roles_var.get(),
                            "clone_categories": self.clone_categories_var.get(),
                            "clone_text_channels": self.clone_text_channels_var.get(),
                            "clone_voice_channels": self.clone_voice_channels_var.get(),
                            "clone_messages": self.clone_messages_var.get(),
                            "clone_name_icon": self.clone_name_icon_var.get(),
                            "messages_limit": int(self.messages_limit_var.get()) if self.clone_messages_var.get()
                            else 0
                        }
                    )
                    
                    if success:
                        # Impostiamo la barra al 100% al completamento
                        self.update_progress(1.0)
                        self._debug_log(self.lang.get_text("logs.clone.completed"), "SUCCESS")
                        # Aggiorniamo un'ultima volta le statistiche
                        self.update_stats(cloner.get_stats())
                    else:
                        self.update_progress(0, show=False)  # Nascondiamo la barra in caso di errore
                except Exception as clone_error:
                    self._debug_log(
                        self.lang.get_text("logs.clone.error").format(error=str(clone_error)), 
                        "ERROR"
                    )
                    self.update_progress(0, show=False)  # Nascondiamo la barra in caso di errore
        except Exception as e:
            self._debug_log(
                self.lang.get_text("logs.clone.connection_error").format(error=str(e)), 
                "ERROR"
            )
            self.update_progress(0, show=False)  # Nascondiamo la barra in caso di errore
        finally:
            # Cancelliamo il timer se esistente
            if 'stats_timer' in locals() and stats_timer and not stats_timer.done():
                stats_timer.cancel()
                await asyncio.sleep(0.1)  # Piccola pausa per assicurarsi che il task venga cancellato
            
            # Ripristiniamo il pulsante
            self.clone_button.configure(state="normal")
            
            # Chiudiamo il connector anche in caso di errore
            if connector:
                try:
                    await connector.close()
                except Exception as connector_error:
                    print(f"Error closing connector: {connector_error}")

    def _debug_log(self, message, level="INFO"):
        """Send log to debug window if active"""
        main_window = self.winfo_toplevel()
        if hasattr(main_window, 'debug_mode') and main_window.debug_mode:
            if hasattr(main_window, 'debug_window'):
                try:
                    # Verifichiamo che la finestra di debug esista ancora e sia valida
                    if main_window.debug_window.winfo_exists():
                        main_window.debug_window.log(message, level)
                except Exception as e:
                    print(f"Debug window error: {e}")
        
        # Always update status bar
        color = "red" if level == "ERROR" else "blue" if level == "INFO" else "green"
        main_window.status_bar.update_status(message, color)

    def update_texts(self):
        """Update texts when language changes"""
        self.source_label.configure(text=self.lang.get_text("input.guild.source.title"))
        self.source_entry.configure(placeholder_text=self.lang.get_text("input.guild.source.placeholder"))
        self.dest_label.configure(text=self.lang.get_text("input.guild.destination.title"))
        self.dest_entry.configure(placeholder_text=self.lang.get_text("input.guild.destination.placeholder"))
        self.clone_button.configure(text=self.lang.get_text("input.guild.clone_button"))
        self.reset_button.configure(text=self.lang.get_text("input.guild.reset_button"))
        
        # Aggiorniamo i dropdown
        placeholder = self.lang.get_text("input.guild.dropdown_placeholder")
        if self.source_dropdown.get() == "":
            self.source_dropdown.set(placeholder)
        if self.dest_dropdown.get() == "":
            self.dest_dropdown.set(placeholder)
        
        # Aggiorniamo i testi delle opzioni
        self.options_title.configure(text=self.lang.get_text("input.guild.options_title"))
        self.clone_roles_checkbox.configure(text=self.lang.get_text("input.guild.option_roles"))
        self.clone_categories_checkbox.configure(text=self.lang.get_text("input.guild.option_categories"))
        self.clone_text_channels_checkbox.configure(text=self.lang.get_text("input.guild.option_text_channels"))
        self.clone_voice_channels_checkbox.configure(text=self.lang.get_text("input.guild.option_voice_channels"))
        self.clone_messages_checkbox.configure(text=self.lang.get_text("input.guild.option_messages"))
        self.messages_limit_label.configure(text=self.lang.get_text("input.guild.option_messages_limit"))
        
        # Aggiorniamo anche i testi del pannello statistiche
        self.stats_title.configure(text=self.lang.get_text("input.guild.stats_title"))
        self.roles_label.configure(text=self.lang.get_text("input.guild.stats_roles"))
        self.channels_label.configure(text=self.lang.get_text("input.guild.stats_channels"))
        self.messages_label.configure(text=self.lang.get_text("input.guild.stats_messages"))
        self.errors_label.configure(text=self.lang.get_text("input.guild.stats_errors"))
        self.time_label.configure(text=self.lang.get_text("input.guild.stats_time"))

    def update_stats(self, stats: dict):
        """Aggiorna il pannello delle statistiche con i dati forniti"""
        # Assicuriamoci che il pannello sia visibile
        if not self.info_panel.winfo_ismapped():
            self.info_panel.pack(fill="x", pady=10, before=self.clone_button)
            
        # Aggiorniamo i valori
        self.roles_value.configure(text=f"{stats.get('roles_created', 0)}/{stats.get('total_roles', 0)}")
        self.channels_value.configure(text=f"{stats.get('channels_created', 0)}/{stats.get('total_channels', 0)}")
        self.messages_value.configure(text=str(stats.get('messages_copied', 0)))
        
        # Errori in rosso se presenti
        errors = stats.get('errors', 0)
        self.errors_value.configure(text=str(errors))
        
        # Formattiamo il tempo in minuti:secondi
        elapsed_time = stats.get('elapsed_time', 0)
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        self.time_value.configure(text=f"{minutes:02d}:{seconds:02d}")
        
    def hide_stats(self):
        """Nasconde il pannello delle statistiche"""
        if self.info_panel.winfo_ismapped():
            self.info_panel.pack_forget()

    def toggle_messages_options(self):
        """Abilita/disabilita le opzioni relative ai messaggi"""
        if self.clone_messages_var.get():
            self.messages_limit_entry.configure(state="normal")
            self.messages_limit_label.configure(text_color=Colors.get_color(Colors.TEXT))
        else:
            self.messages_limit_entry.configure(state="disabled")
            self.messages_limit_label.configure(text_color=Colors.get_color(Colors.TEXT_MUTED))

    def _setup_context_menu(self, widget, is_source=True):
        """Configura il menu contestuale (tasto destro) per i dropdown dei server"""
        context_menu = tk.Menu(widget, tearoff=0)
        
        if is_source:
            # Menu per il server sorgente
            context_menu.add_command(
                label=self.lang.get_text("input.guild.open_in_browser"), 
                command=lambda: self.open_server_in_browser(self.get_source_guild_id())
            )
        else:
            # Menu per il server destinazione
            context_menu.add_command(
                label=self.lang.get_text("input.guild.open_in_browser"), 
                command=lambda: self.open_server_in_browser(self.get_dest_guild_id())
            )
            
        # Bind per il tasto destro 
        widget.bind("<Button-3>", lambda event: self._show_context_menu(event, context_menu))
        
        # Salva un riferimento al menu
        if is_source:
            self.source_context_menu = context_menu
        else:
            self.dest_context_menu = context_menu
    
    def _show_context_menu(self, event, menu):
        """Mostra il menu contestuale alla posizione del mouse"""
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
    
    def open_server_in_browser(self, guild_id):
        """Apre il server Discord nel browser"""
        if not guild_id:
            return
            
        # URL del server Discord
        discord_url = f"https://discord.com/channels/{guild_id}"
        
        try:
            # Apri il browser con l'URL
            webbrowser.open(discord_url)
            
            # Log dell'azione
            self._debug_log(f"Apertura server {guild_id} nel browser", "INFO")
        except Exception as e:
            self._debug_log(f"Errore nell'apertura del browser: {str(e)}", "ERROR")
    
    async def create_guild_request(self, token, guild_name):
        """Crea un nuovo server Discord tramite API REST"""
        self._debug_log(f"Creazione nuovo server: {guild_name}", "INFO")
        
        try:
            # Creiamo un connector sicuro per evitare memory leak
            connector = aiohttp.TCPConnector(force_close=True)
            
            # URL dell'API per creare un nuovo server
            api_url = "https://discord.com/api/v10/guilds"
            
            # Prepariamo l'header per le richieste API - assicuriamoci che il token sia nel formato corretto
            if not token.startswith("Bot ") and not token.startswith("Bearer "):
                # Se non è specificato il tipo di token, assumiamo che sia un user token
                auth_token = token
            else:
                auth_token = token
                
            headers = {
                "Authorization": auth_token,
                "Content-Type": "application/json"
            }
            
            # Dati per la creazione del server
            guild_data = {
                "name": guild_name,
                "region": "eu-central", # Regione predefinita
                "icon": None,          # Nessuna icona iniziale
                "verification_level": 0 # Livello di verifica più basso
            }
            
            async with aiohttp.ClientSession(connector=connector, headers=headers) as session:
                async with session.post(api_url, json=guild_data) as response:
                    if response.status == 201: # 201 Created
                        # Server creato con successo
                        result = await response.json()
                        guild_id = result.get("id")
                        guild_name = result.get("name")
                        self._debug_log(f"Server creato: {guild_name} (ID: {guild_id})", "SUCCESS")
                        return {"success": True, "id": guild_id, "name": guild_name}
                    else:
                        # Errore nella creazione
                        error_data = await response.text()
                        self._debug_log(f"Errore nella creazione del server: {response.status} - {error_data}", "ERROR")
                        return {"success": False, "error": f"Errore API ({response.status}): {error_data}"}
        except Exception as e:
            self._debug_log(f"Errore imprevisto: {str(e)}", "ERROR")
            return {"success": False, "error": str(e)}
    
    def create_new_server(self):
        """Mostra un dialogo per creare un nuovo server Discord"""
        main_window = self.winfo_toplevel()
        
        # Verifica se abbiamo un token
        token = main_window.verified_token if hasattr(main_window, 'verified_token') else main_window.token_input.entry.get()
        
        if not token:
            main_window.status_bar.update_status(
                self.lang.get_text("input.token.error_empty"), 
                "red"
            )
            return
        
        # Chiedi il nome del nuovo server
        server_name = simpledialog.askstring(
            self.lang.get_text("input.guild.create_server_title"), 
            self.lang.get_text("input.guild.create_server_prompt"),
            parent=self
        )
        
        if not server_name:
            return  # Utente ha annullato
            
        # Disabilita i controlli durante la creazione
        self.create_server_button.configure(state="disabled")
        
        # Aggiorna la barra di stato
        main_window.status_bar.update_status(
            self.lang.get_text("status.creating_server").format(name=server_name), 
            "blue"
        )
        
        # Esegui la richiesta in un thread separato
        threading.Thread(target=self._create_server_thread, args=(token, server_name), daemon=True).start()
    
    def _create_server_thread(self, token, server_name):
        """Thread per la creazione di un nuovo server"""
        main_window = self.winfo_toplevel()
        
        try:
            # Creiamo un loop asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Eseguiamo la richiesta API
            result = loop.run_until_complete(self.create_guild_request(token, server_name))
            
            # Gestiamo il risultato nel thread principale
            if result["success"]:
                self.after(0, lambda: self._handle_server_creation_success(result))
            else:
                self.after(0, lambda: self._handle_server_creation_error(result["error"]))
            
        except Exception as e:
            # Gestiamo eventuali errori
            self.after(0, lambda: self._handle_server_creation_error(str(e)))
        finally:
            # Chiudiamo l'event loop
            loop.close()
    
    def _handle_server_creation_success(self, result):
        """Gestisce la creazione riuscita di un server"""
        main_window = self.winfo_toplevel()
        
        # Ripristina il pulsante
        self.create_server_button.configure(state="normal")
        
        # Aggiorna la barra di stato
        main_window.status_bar.update_status(
            self.lang.get_text("status.server_created").format(name=result['name']), 
            "green"
        )
        
        # Aggiorna l'elenco server facendo riutilizzare il token esistente
        main_window.token_input.verify_token()
        
        # Mostra un messaggio di conferma
        messagebox.showinfo(
            self.lang.get_text("input.guild.create_server_success"), 
            f"{self.lang.get_text('input.guild.create_server_success')}:\n\n{result['name']}\nID: {result['id']}"
        )
    
    def _handle_server_creation_error(self, error_message):
        """Gestisce gli errori durante la creazione del server"""
        main_window = self.winfo_toplevel()
        
        # Ripristina il pulsante
        self.create_server_button.configure(state="normal")
        
        # Aggiorna la barra di stato
        main_window.status_bar.update_status(
            f"{self.lang.get_text('input.guild.create_server_error')}: {error_message}", 
            "red"
        )
        
        # Mostra un errore
        messagebox.showerror(
            self.lang.get_text("input.guild.create_server_error"), 
            f"{self.lang.get_text('input.guild.create_server_error')}:\n\n{error_message}"
        )