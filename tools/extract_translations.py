#!/usr/bin/env python
import os
import sys
import subprocess

def main():
    """
    Extract translatable messages from the application.
    This will create or update the messages.pot file.
    """
    print("Extracting messages...")
    
    # The output directory for translation files
    os.makedirs('translations', exist_ok=True)
    
    # Extract messages with pybabel
    # Command will search through Python files and Jinja2 templates
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
    except subprocess.CalledProcessError as e:
        print(f"Error extracting messages: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
