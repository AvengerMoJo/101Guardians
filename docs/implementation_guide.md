# Internationalization (i18n) Implementation Guide for 101Guardians

This guide explains how we've implemented internationalization in the 101Guardians application using Flask-Babel, with Traditional Chinese (zh_TW) as the default language.

## Overview

We've implemented a complete i18n solution with:

1. **Server-side translation** using Flask-Babel
2. **Client-side language switching** without page reload
3. **Translation management workflow** with extraction, update, and compilation scripts
4. **Default language** set to Traditional Chinese (zh_TW)
5. **Support for multiple languages** including English, Japanese, and Korean

## Files Added or Modified

### Backend Components

1. **babel.py** - Core configuration for Flask-Babel
   - Defines the locale selector function
   - Sets up the Babel extension

2. **app_config.py** - Updated to initialize Babel and configure language settings
   - Added supported languages configuration
   - Set default locale to Traditional Chinese (zh_TW)

3. **routes/language_routes.py** - Added routes for language switching
   - Created a route to change the language in the user's session

4. **app.py** - Updated to register the language routes

### Translation Files

1. **translations/zh_TW/LC_MESSAGES/messages.po** - Traditional Chinese translations
2. **translations/en/LC_MESSAGES/messages.po** - English translations
3. **babel.cfg** - Configuration for the Babel extraction tool

### Management Scripts

1. **manage_translations.py** - Script to manage translation workflow
   - extract - Extract translatable strings from the application
   - init - Initialize a new language
   - update - Update existing translations
   - compile - Compile translation files into binary .mo files

2. **compile_translations.sh** - Shell script to quickly compile translations

### Templates (Updated)

1. **templates/base.html** - Added language switcher dropdown and i18n markup
2. **templates/index.html** - Updated with translation functions
3. **templates/dashboard.html** - Updated with translation functions
4. **templates/profile.html** - Updated with translation functions
5. **templates/debug.html** - Updated with translation functions and debugging info

### Frontend Components

1. **static/js/i18n.js** - Client-side internationalization support
   - Functions for language switching
   - Function for client-side translations (fallback)

2. **static/css/i18n.css** - Styling for internationalization features
   - Language-specific font adjustments
   - RTL (right-to-left) language support
   - Loading indicator for language switching

3. **static/js/main.js** - Updated to initialize the language switcher
4. **static/js/prayers/form.js** - Updated to support translations
5. **static/js/prayers/crud.js** - Updated to support translations

## How It Works

### Server-side Translation

1. In Jinja2 templates, strings are marked for translation using the `_()` function:
   ```html
   <h1>{{ _('Welcome to 101Guardians') }}</h1>
   ```

2. In Python code, strings are marked for translation using the `_()` function:
   ```python
   flash(_('Login successful'))
   ```

3. Flask-Babel extracts these strings into a message catalog (POT file)
4. Translators edit the PO files with translations for each language
5. Compiled MO files are used by the application to render strings in the user's language

### Language Selection Logic

1. User's selected language (stored in session) gets highest priority
2. Browser's accept-language header is checked next
3. Falls back to Traditional Chinese (zh_TW) if no preference is detected

### Language Switching

1. The user selects a language from the dropdown in the navigation bar
2. The browser sends a request to `/language/<language_code>`
3. The server updates the session with the selected language
4. The page reloads with content in the selected language

## Adding a New Language

To add support for a new language:

1. Run the initialization script:
   ```bash
   python manage_translations.py init <language_code>
   ```
   Example: `python manage_translations.py init fr` for French

2. Edit the generated PO file in `translations/<language_code>/LC_MESSAGES/messages.po`

3. Add the language to the `LANGUAGES` dictionary in `app_config.py`:
   ```python
   'LANGUAGES': {
       'zh_TW': '繁體中文',  # Traditional Chinese
       'en': 'English',
       'ja': '日本語',        # Japanese
       'ko': '한국어',        # Korean
       'fr': 'Français'      # French (new)
   }
   ```

4. Compile the translations:
   ```bash
   python manage_translations.py compile
   ```

## Updating Translations

When new translatable strings are added to the application:

1. Extract the new strings:
   ```bash
   python manage_translations.py extract
   ```

2. Update the translation files:
   ```bash
   python manage_translations.py update
   ```

3. Edit the updated PO files with translations for the new strings

4. Compile the translations:
   ```bash
   python manage_translations.py compile
   ```

## Best Practices

1. **Use context where needed**: For ambiguous terms, provide context using comments in the templates:
   ```html
   {# Translator: This refers to a prayer that has been fulfilled #}
   {{ _('Answered') }}
   ```

2. **Handle plurals properly**: Use ngettext for strings that have plural forms:
   ```python
   ngettext('%(count)d prayer', '%(count)d prayers', count) % {'count': count}
   ```

3. **Use named variables for string interpolation**:
   ```html
   {{ _('Welcome, %(username)s') % {'username': user.name} }}
   ```

4. **Keep translations up to date**: Regularly update translations when new features are added

## Testing

1. Test language switching using the dropdown
2. Verify that all UI elements are properly translated
3. Test with different browser language settings
4. Check RTL support if adding languages like Arabic or Hebrew