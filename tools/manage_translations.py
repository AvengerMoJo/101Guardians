#!/usr/bin/env python
import os
import sys
import subprocess
import argparse

def extract_messages():
    """Extract translatable messages from the application."""
    print("Extracting messages...")
    
    # The output directory for translation files
    os.makedirs('translations', exist_ok=True)
    
    # Extract messages with pybabel
    cmd = [
        'pybabel', 'extract', 
        '-F', 'babel.cfg',
        '--keywords=_', 
        '--project=101Guardians',
        '-o', 'translations/messages.pot',
        '.'
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("Messages extracted successfully to translations/messages.pot")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error extracting messages: {e}")
        return False

def init_language(lang_code):
    """Initialize translations for a new language."""
    print(f"Initializing translation for {lang_code}...")
    
    # Check if messages.pot exists
    if not os.path.exists('translations/messages.pot'):
        if not extract_messages():
            return False
    
    # Initialize the language
    cmd = [
        'pybabel', 'init',
        '-i', 'translations/messages.pot',
        '-d', 'translations',
        '-l', lang_code
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print(f"Translation initialized for {lang_code}")
        print(f"Edit translations/{lang_code}/LC_MESSAGES/messages.po to add translations")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error initializing translation: {e}")
        return False

def update_translations():
    """Update all existing translation files."""
    print("Updating translations...")
    
    # First extract updated messages
    if not extract_messages():
        return False
    
    # Update all translation files
    cmd = [
        'pybabel', 'update',
        '-i', 'translations/messages.pot',
        '-d', 'translations'
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("Translations updated successfully")
        print("Edit the .po files in translations/<lang_code>/LC_MESSAGES/ to update translations")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error updating translations: {e}")
        return False

def compile_translations():
    """Compile all translation files."""
    print("Compiling translations...")
    
    cmd = [
        'pybabel', 'compile',
        '-d', 'translations'
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("Translations compiled successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error compiling translations: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Manage translations for the 101Guardians application")
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Extract command
    extract_parser = subparsers.add_parser('extract', help='Extract translatable messages')
    
    # Init command
    init_parser = subparsers.add_parser('init', help='Initialize a new language')
    init_parser.add_argument('lang_code', help='Language code (e.g., zh_TW, en, ja, ko)')
    
    # Update command
    update_parser = subparsers.add_parser('update', help='Update existing translations')
    
    # Compile command
    compile_parser = subparsers.add_parser('compile', help='Compile translation files')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Execute the selected command
    if args.command == 'extract':
        extract_messages()
    elif args.command == 'init':
        init_language(args.lang_code)
    elif args.command == 'update':
        update_translations()
    elif args.command == 'compile':
        compile_translations()
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
