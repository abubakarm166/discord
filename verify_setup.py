"""
Quick verification script to check if the project is set up correctly.
Run this with: python verify_setup.py
"""
import os
import sys
from pathlib import Path

# Check if .env exists
env_path = Path('.env')
if not env_path.exists():
    print("[X] ERROR: .env file not found!")
    print("   Create a .env file in the project root with the required variables.")
    sys.exit(1)
else:
    print("[OK] .env file exists")

# Check if required packages are installed
try:
    import django
    print("[OK] Django is installed")
except ImportError:
    print("[X] ERROR: Django is not installed")
    print("   Run: pip install -r requirements.txt")
    sys.exit(1)

try:
    import requests
    print("[OK] requests library is installed")
except ImportError:
    print("[X] ERROR: requests library is not installed")
    print("   Run: pip install -r requirements.txt")
    sys.exit(1)

try:
    from decouple import config
    print("[OK] python-decouple is installed")
except ImportError:
    print("[X] ERROR: python-decouple is not installed")
    print("   Run: pip install -r requirements.txt")
    sys.exit(1)

# Check environment variables
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'discord_rewards.settings')

try:
    import django
    django.setup()
    from django.conf import settings
    
    print("\n[CONFIG] Configuration Check:")
    print(f"   DISCORD_CLIENT_ID: {settings.DISCORD_CLIENT_ID[:10]}..." if settings.DISCORD_CLIENT_ID else "   DISCORD_CLIENT_ID: [X] NOT SET")
    print(f"   DISCORD_CLIENT_SECRET: {'[OK] SET' if settings.DISCORD_CLIENT_SECRET and settings.DISCORD_CLIENT_SECRET != 'YOUR_CLIENT_SECRET_HERE' else '[X] NOT SET'}")
    print(f"   DISCORD_REDIRECT_URI: {settings.DISCORD_REDIRECT_URI}")
    print(f"   DEBUG: {settings.DEBUG}")
    
    if not settings.DISCORD_CLIENT_ID:
        print("\n[!] WARNING: DISCORD_CLIENT_ID is not set in .env")
    if not settings.DISCORD_CLIENT_SECRET or settings.DISCORD_CLIENT_SECRET == 'YOUR_CLIENT_SECRET_HERE':
        print("\n[!] WARNING: DISCORD_CLIENT_SECRET is not set or still has placeholder value")
        print("   Get it from: https://discord.com/developers/applications > OAuth2 section")
    
    # Check database
    print("\n[DATABASE] Database Check:")
    db_path = Path('db.sqlite3')
    if db_path.exists():
        print("[OK] Database file exists")
    else:
        print("[!] Database file not found - run migrations: python manage.py migrate")
    
    print("\n[OK] Setup verification complete!")
    print("\n[NEXT STEPS] Next steps:")
    print("   1. Make sure Discord OAuth2 redirect URI is set in Discord Developer Portal")
    print("   2. Run migrations: python manage.py migrate")
    print("   3. Create admin user: python manage.py createsuperuser")
    print("   4. Start server: python manage.py runserver")
    print("   5. Open browser: http://localhost:8000")
    
except Exception as e:
    print(f"\n[X] Error checking configuration: {e}")
    print("   Make sure you're in the project root directory")
    sys.exit(1)
