import json
import os
import sys
from typing import Dict

class LanguageManager:
    _instance = None
    _current_language = "en-US"
    _translations: Dict = {}
    _observers = []
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_translations()
            cls._instance._current_language = "en-US"
        return cls._instance
    
    def _load_translations(self):
        """Carica le traduzioni dai file JSON"""
        self._translations = {}
        
        # Determina il percorso base dell'applicazione (funziona sia in modalità di sviluppo che compilata)
        if getattr(sys, 'frozen', False):
            # Se l'app è compilata con PyInstaller
            base_path = sys._MEIPASS
        else:
            # In modalità di sviluppo
            base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        
        language_dir = os.path.join(base_path, "src", "interface", "language")
        
        # Percorso alternativo se il primo non esiste
        if not os.path.exists(language_dir):
            language_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "language")
        
        print(f"Looking for language files in: {language_dir}")
        
        if os.path.exists(language_dir):
            for filename in os.listdir(language_dir):
                if filename.endswith(".json"):
                    lang_code = filename.split(".")[0]
                    file_path = os.path.join(language_dir, filename)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            self._translations[lang_code] = json.load(f)
                            print(f"Loaded language file: {filename}")
                    except Exception as e:
                        print(f"Error loading language file {filename}: {e}")
        else:
            print(f"Language directory not found: {language_dir}")
        
        # Fallback to English if no translations loaded
        if not self._translations:
            print("No language files found, using hardcoded English")
            self._translations["en-US"] = {
                "app": {
                    "title": "Discord Server Cloner",
                    "subtitle": "Clone servers with ease"
                }
            }
    
    def get_text(self, key: str, **kwargs) -> str:
        """
        Get translated text for the specified key
        Example: get_text("settings.title")
        """
        try:
            keys = key.split(".")
            value = self._translations[self._current_language]
            for k in keys:
                value = value[k]
            return value.format(**kwargs) if kwargs else value
        except (KeyError, AttributeError):
            # If key doesn't exist, use English as fallback
            try:
                value = self._translations["en-US"]
                for k in keys:
                    value = value[k]
                return value.format(**kwargs) if kwargs else value
            except (KeyError, AttributeError):
                return key
    
    def set_language(self, lang_code: str) -> bool:
        """
        Change current language and notify observers
        """
        # Convert language name to correct code
        lang_map = {
            "English": "en-US",
            "Italiano": "it-IT",
            "Español": "es-ES"
        }
        
        lang_code = lang_map.get(lang_code, lang_code)
        
        if lang_code in self._translations:
            self._current_language = lang_code
            self._notify_observers()
            return True
        return False
    
    def get_available_languages(self) -> dict:
        """
        Returns available languages in format:
        {"it-IT": "Italiano", "en-US": "English", ...}
        """
        languages = {}
        for lang_code in self._translations.keys():
            try:
                languages[lang_code] = self._translations[lang_code]["settings"]["language"]["languages"][lang_code]
            except KeyError:
                languages[lang_code] = lang_code
        return languages
    
    def get_language_name(self, lang_code: str = None) -> str:
        """
        Returns current language name in current language
        """
        if lang_code is None:
            lang_code = self._current_language
        try:
            return self._translations[self._current_language]["settings"]["language"]["languages"][lang_code]
        except KeyError:
            return lang_code

    def add_observer(self, callback):
        """Add observer for language changes"""
        if callback not in self._observers:
            self._observers.append(callback)
    
    def remove_observer(self, callback):
        """Remove observer"""
        if callback in self._observers:
            self._observers.remove(callback)
    
    def _notify_observers(self):
        """Notify all observers of language change"""
        for callback in self._observers:
            try:
                callback()
            except Exception as e:
                print(f"Error notifying observer: {e}")

    @property
    def current_language(self):
        return self._current_language