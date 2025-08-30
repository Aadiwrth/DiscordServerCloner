#!/usr/bin/env python3
"""
Build script for Discord Server Cloner
Creates a distributable executable using PyInstaller
"""

import os
import sys
import shutil
import subprocess
import datetime
import platform

# Configuration
APP_NAME = "Discord Server Cloner"
APP_VERSION = "2.0.0"
MAIN_SCRIPT = "main.py"
OUTPUT_DIR = "dist"
BUILD_DIR = "build"
ICON_PATH = os.path.join("src", "interface", "assets", "discord_logo.png")

# PyInstaller options
PYINSTALLER_OPTS = [
    f"--name={APP_NAME}",
    "--onefile",  # Crea un singolo file eseguibile
    "--windowed",  # Non mostra la console quando l'app viene eseguita
    f"--icon={ICON_PATH}",
    "--clean",  # Pulisce la cartella di build prima di creare il nuovo eseguibile
    "--noconfirm",  # Non chiede conferma per sovrascrivere file esistenti
    "--log-level=INFO",
    "--add-data=src/interface/assets;src/interface/assets",  # Includi le risorse
    "--add-data=src/interface/language;src/interface/language"  # Includi i file di traduzione
]

def clear_directory(dir_path):
    """Pulisce una directory se esiste"""
    if os.path.exists(dir_path):
        print(f"Cleaning {dir_path}...")
        try:
            shutil.rmtree(dir_path)
            os.makedirs(dir_path)
        except Exception as e:
            print(f"Error cleaning directory: {str(e)}")
    else:
        os.makedirs(dir_path)

def clean_pycache():
    """Rimuove tutti i file __pycache__ dalla directory corrente e sottodirectory"""
    for root, dirs, files in os.walk(".", topdown=False):
        for d in dirs:
            if d == "__pycache__":
                cache_dir = os.path.join(root, d)
                print(f"Removing {cache_dir}")
                shutil.rmtree(cache_dir)

def run_pyinstaller():
    """Esegue PyInstaller con le opzioni configurate"""
    # Build the command
    cmd = ["pyinstaller"] + PYINSTALLER_OPTS + [MAIN_SCRIPT]
    
    try:
        print("Running PyInstaller...")
        print(f"Command: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"PyInstaller failed with error code {e.returncode}")
        return False
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return False

def create_distribution_package():
    """Crea una cartella ZIP contenente l'eseguibile e le risorse necessarie"""
    dist_dir = os.path.join(OUTPUT_DIR, APP_NAME)
    if not os.path.exists(dist_dir):
        dist_dir = OUTPUT_DIR  # Fallback se la prima opzione non esiste
    
    if os.path.exists(dist_dir):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_name = f"{APP_NAME.replace(' ', '_')}_{APP_VERSION}_{timestamp}"
        
        # Aggiunge il sistema operativo al nome del file
        system = platform.system().lower()
        if system == "windows":
            zip_name += "_win"
        elif system == "linux":
            zip_name += "_linux"
        elif system == "darwin":
            zip_name += "_mac"
        
        shutil.make_archive(
            zip_name,  # Nome base del file ZIP
            'zip',     # Formato
            dist_dir   # Directory da zippare
        )
        print(f"Created distribution package: {zip_name}.zip")
        return True
    else:
        print(f"Error: Distribution directory {dist_dir} not found")
        return False

def check_prerequisites():
    """Verifica che tutti i prerequisiti siano installati"""
    try:
        # Verifica PyInstaller
        proc = subprocess.run(
            ["pyinstaller", "--version"], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
        )
        if proc.returncode != 0:
            print("PyInstaller is not installed or not in PATH")
            print("Please install it using: pip install pyinstaller")
            return False
        else:
            print(f"PyInstaller version: {proc.stdout.strip()}")
            
        return True
    except Exception as e:
        print(f"Error checking prerequisites: {str(e)}")
        return False

def main():
    """Main build process"""
    print(f"=== Building {APP_NAME} v{APP_VERSION} ===")
    
    # Verifica prerequisiti
    if not check_prerequisites():
        sys.exit(1)
    
    # Pulisci directory
    clean_pycache()
    clear_directory(BUILD_DIR)
    clear_directory(OUTPUT_DIR)
    
    # Costruisci l'applicazione
    if not run_pyinstaller():
        sys.exit(1)
    
    # Crea il pacchetto di distribuzione
    if not create_distribution_package():
        sys.exit(1)
    
    print("=== Build completed successfully ===")

if __name__ == "__main__":
    main() 