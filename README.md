# Discord Community Rewards Platform

A fast MVP for a Discord-based community rewards platform where users can earn keys through activity and redeem them for fixed rewards.

## Features

- Discord OAuth2 authentication
- Key balance management
- Reward redemption system
- Admin panel for managing rewards and user keys
- Clean, responsive Bootstrap UI

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Discord OAuth

1. Create a Discord Developer Application at https://discord.com/developers/applications
2. Go to OAuth2 section
3. Add redirect URI: `http://localhost:8000/auth/discord/callback/` (or your production URL)
4. Copy Client ID and Client Secret

### 3. Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-django-secret-key-here
DEBUG=True
DISCORD_CLIENT_ID=your-discord-client-id
DISCORD_CLIENT_SECRET=your-discord-client-secret
DISCORD_REDIRECT_URI=http://localhost:8000/auth/discord/callback/
```

### 4. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Superuser

```bash
python manage.py createsuperuser
```

### 6. Run Development Server

```bash
python manage.py runserver
```

## Usage

1. Visit `http://localhost:8000` to see the landing page
2. Click "Login with Discord" to authenticate
3. After login, you'll see the dashboard with your key balance and available rewards
4. Click "Redeem" on any reward to use your keys
5. Admin can manage rewards and user keys at `/admin`

## Admin Features

- Add/edit rewards (name, image, key cost, active status)
- View and modify user key balances
- View redemption logs

## Production Deployment

Before deploying to production:

1. Set `DEBUG=False` in `.env`
2. Update `DISCORD_REDIRECT_URI` to your production domain
3. Add your domain to `ALLOWED_HOSTS` in `settings.py`
4. Use a production database (PostgreSQL recommended)
5. Set up proper static file serving
6. Use environment variables for all secrets

## Technology Stack

- Backend: Django 4.2
- Frontend: Bootstrap 5.3, HTML, CSS, JavaScript
- Authentication: Discord OAuth2
- Database: SQLite (development) / PostgreSQL (production)
