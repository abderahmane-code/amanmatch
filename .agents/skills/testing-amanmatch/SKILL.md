# AmanMatch — Testing Skill

## Local Dev Setup

1. Ensure PostgreSQL is running: `sudo service postgresql start`
2. Create database if needed: `sudo -u postgres psql -c "CREATE DATABASE amanmatch;" 2>/dev/null || true`
3. Install dependencies: `pip install -r requirements.txt`
4. Run migrations: `python manage.py migrate`
5. Start dev server: `python manage.py runserver 0.0.0.0:8000`

## Devin Secrets Needed

None — the app uses local PostgreSQL with default `postgres` user and no password by default. The `.env` file or environment variables configure `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`.

## Key URLs

| URL | Auth Required | Purpose |
|-----|--------------|--------|
| `/` | No | Landing page (shows dashboard if logged in) |
| `/accounts/register/` | No | Registration form |
| `/accounts/login/` | No | Login form |
| `/accounts/logout/` | Yes (POST) | Logout (requires POST with CSRF token) |
| `/dashboard/` | Yes | Dashboard (redirects to login if unauthenticated) |
| `/admin/` | Superuser | Django admin |

## Auth Flow Testing

The core E2E flow to verify:
1. Visit `/` — landing page with hero, features, footer
2. Click "Create verified account" → `/accounts/register/`
3. Submit empty form → validation errors in red
4. Fill valid credentials (username + strong password) → submit
5. Auto-redirects to `/dashboard/` with green success alert
6. Verify dashboard shows username, 3 status cards, 6 action cards
7. Click "Logout" in navbar → redirects to landing `/`
8. Click "Login" → `/accounts/login/`
9. Submit wrong password → red error alert
10. Submit correct credentials → redirects to `/dashboard/`

## URL Namespacing

URLs in `accounts/urls.py` use `app_name = "accounts"`, so template references must use `accounts:login`, `accounts:register`, `accounts:logout`. The `dashboard` and `landing` views are top-level (no namespace).

## Logout Requires POST

Django 5+ `LogoutView` requires POST method. The navbar uses a `<form method="post">` with CSRF token. Do NOT use `<a>` links for logout.

## Template Structure

- `templates/base.html` — base layout with navbar include, messages, footer
- `templates/includes/navbar.html` — navigation (different for auth/unauth)
- `templates/landing.html` — public landing page
- `templates/dashboard.html` — authenticated dashboard
- `templates/accounts/login.html` — login glass card
- `templates/accounts/register.html` — register glass card

## CSS Design System

- Single file: `static/css/style.css`
- CSS custom properties in `:root` for colors, spacing, gradients
- Key classes: `.container`, `.section`, `.card`, `.glass`, `.btn`, `.btn-primary`, `.btn-secondary`, `.badge`, `.status-card`, `.action-grid`, `.hero`
- Responsive breakpoints: 1024px, 768px, 480px
- Font: Inter (loaded from Google Fonts)

## Testing Tips

- The dev server might already be running from a previous session on port 8000. Check with `curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/` before starting a new one.
- `ALLOWED_HOSTS` might not include `testserver` — use `curl` against `localhost:8000` or browser testing rather than Django's `Client()` for E2E tests.
- All text is wrapped in `{% trans %}` tags for i18n — when checking DOM text, the English text should appear as-is.
- The navbar changes based on authentication state: unauthenticated shows "Login" + "Get Started"; authenticated shows Dashboard, Profile, Verification, Matches, Messages, Safety, Logout.
