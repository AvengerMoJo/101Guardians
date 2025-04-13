# 101Guardians - Covenant Guardians: Journal of Blessings

This web application provides a simple starter template using:
- Python and Flask for both backend and frontend
- Google and LINE OAuth for authentication
- DuckDB for local database storage
- Flask-Babel for internationalization (i18n)

## Features

- User authentication via Google or LINE accounts
- Profile management
- Simple data storage and retrieval
- Responsive UI using Bulma CSS framework
- Multilingual support with Traditional Chinese (default), English, Japanese, and Korean

## Project Structure

```
app/
├── static/                # Static assets (CSS, JS)
│   ├── css/
│   │   ├── style.css
│   │   └── i18n.css
│   └── js/
│       ├── main.js
│       ├── i18n.js
│       └── ...
├── templates/             # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── dashboard.html
│   └── profile.html
├── translations/          # Translation files
│   ├── zh_TW/            # Traditional Chinese (default)
│   │   └── LC_MESSAGES/
│   │       ├── messages.po
│   │       └── messages.mo
│   ├── en/               # English
│   │   └── LC_MESSAGES/
│   │       ├── messages.po
│   │       └── messages.mo
│   └── ...
├── models/                # Database models
│   └── database.py
├── auth/                  # Authentication modules
│   ├── __init__.py
│   ├── google_auth.py
│   └── line_auth.py
├── babel.py               # Babel configuration
├── babel.cfg              # Babel extraction configuration
├── config.py              # Configuration
├── app.py                 # Main application file
└── requirements.txt       # Dependencies
```

## Setup Instructions

### 1. Clone the repository

```bash
git clone <repository-url>
cd <repository-directory>
```

### 2. Create a virtual environment and install dependencies

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Set up OAuth credentials

#### Google OAuth Setup:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Navigate to "APIs & Services" > "Credentials"
4. Create an OAuth 2.0 Client ID
5. Set authorized redirect URIs to `http://localhost:5000/login/google/callback`
6. Note your Client ID and Client Secret

#### LINE Login Setup:
1. Go to [LINE Developers Console](https://developers.line.biz/)
2. Create a new provider and channel
3. Enable LINE Login
4. Set the Callback URL to `http://localhost:5000/login/line/callback`
5. Note your Channel ID (Client ID) and Channel Secret (Client Secret)

### 4. Set environment variables

Copy the `.env.template` file to `.env` and fill in your credentials:

```bash
cp .env.template .env
```

Edit the `.env` file with your credentials:

```
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your_secret_key_here
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
LINE_CLIENT_ID=your_line_channel_id
LINE_CLIENT_SECRET=your_line_channel_secret
```

### 5. Compile translations

Before running the application, compile the translation files:

```bash
./compile_translations.sh
```

Or manually:

```bash
pybabel compile -d translations
```

### 6. Run the application

```bash
flask run
```

The application will be available at [http://localhost:5000](http://localhost:5000)

## Internationalization (i18n)

The application supports multiple languages through Flask-Babel:

- Traditional Chinese (zh_TW) - Default
- English (en)
- Japanese (ja) 
- Korean (ko)

### Adding translations for new strings

1. Mark strings for translation in templates with `{{ _('String to translate') }}` or in Python code with `_('String to translate')`
2. Extract the strings to the message catalog:

```bash
python manage_translations.py extract
```

3. Update existing translation files:

```bash
python manage_translations.py update
```

4. Edit the `.po` files in the `translations/<language_code>/LC_MESSAGES/` directory to add translations
5. Compile the translation files:

```bash
python manage_translations.py compile
```

### Adding a new language

1. Initialize the new language:

```bash
python manage_translations.py init <language_code>
```

Example: `python manage_translations.py init fr` for French

2. Edit the `.po` file in the `translations/<language_code>/LC_MESSAGES/` directory to add translations
3. Compile the translation files:

```bash
python manage_translations.py compile
```

4. Add the new language to the `LANGUAGES` dictionary in `app_config.py`

## Database

The application uses DuckDB, a lightweight analytical database that stores data in a single file. The database file (`app.db`) will be created automatically when you run the application for the first time.

## Extending the Application

### Adding new features
1. Define models in `models/database.py`
2. Implement API endpoints in `app.py`
3. Create or modify templates in the `templates/` directory
4. Add any client-side functionality in `static/js/main.js`

### Deployment
For production deployment:
1. Set `FLASK_ENV=production` in your environment
2. Use a proper WSGI server like Gunicorn
3. Set a strong, random `SECRET_KEY`

## License

This project is licensed under the MIT License - see the LICENSE file for details.