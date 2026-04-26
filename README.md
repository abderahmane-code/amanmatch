# AmanMatch

**AmanMatch** is a global, secure matchmaking platform that helps people find serious partners safely. The platform reduces fake profiles and emotional manipulation through mandatory identity verification before any contact is allowed.

> This is NOT a casual dating app — it is a serious matchmaking platform with privacy and safety at its core.

---

## Tech Stack

| Layer          | Technology                          |
|----------------|-------------------------------------|
| Backend        | Django 5+                           |
| Frontend       | Django Templates (HTML / CSS / JS)  |
| Database       | PostgreSQL                          |
| Authentication | Django built-in auth                |
| UI Theme       | Modern clean dark theme             |
| Languages      | English (default), Arabic, French   |

## Project Structure

```
amanmatch/
├── amanmatch/          # Django project settings & root URLs
├── accounts/           # User registration, login, logout
├── profiles/           # User profiles (future)
├── verification/       # Identity verification (future)
├── matchmaking/        # Smart matching algorithm (future)
├── messaging/          # Secure messaging (future)
├── reports/            # Report suspicious activity (future)
├── templates/          # Global templates
│   ├── base.html
│   ├── landing.html
│   ├── dashboard.html
│   ├── includes/
│   └── accounts/
├── static/
│   └── css/style.css
├── locale/             # i18n translation files (ar, fr)
├── requirements.txt
├── .env.example
└── manage.py
```

## Local Setup

### Prerequisites

- Python 3.10+
- PostgreSQL 14+

### 1. Clone & set up virtual environment

```bash
git clone https://github.com/abderahmane-code/amanmatch.git
cd amanmatch
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env with your PostgreSQL credentials
```

### 3. Create the database

```bash
# In psql or pgAdmin:
CREATE DATABASE amanmatch;
```

### 4. Apply migrations & create superuser

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 5. Run the development server

```bash
python manage.py runserver
```

Visit **http://127.0.0.1:8000/** to see the landing page.

## Pages

| URL                   | Description              |
|-----------------------|--------------------------|
| `/`                   | Landing page             |
| `/accounts/register/` | Sign up                  |
| `/accounts/login/`    | Login                    |
| `/accounts/logout/`   | Logout                   |
| `/dashboard/`         | Dashboard (login needed) |
| `/admin/`             | Django admin             |

## Internationalization

The project is structured for i18n. English is the default language. Arabic and French locale directories are ready at `locale/ar/` and `locale/fr/`.

To generate translation files:

```bash
python manage.py makemessages -l ar
python manage.py makemessages -l fr
python manage.py compilemessages
```

## License

This project is private.
