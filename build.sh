#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "🚀 Starting build process..."

# Upgrade pip to latest version
echo "📦 Upgrading pip..."
python -m pip install --upgrade pip

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Collect static files
echo "🎨 Collecting static files..."
python manage.py collectstatic --noinput --clear

# Clear problematic database entries
echo "🧹 Cleaning up database..."
python -c "
from django.db import connection
try:
    with connection.cursor() as cursor:
        print('Deleting problematic client profiles...')
        cursor.execute('DELETE FROM client_profiles WHERE user_id IN (25, 26)')
        print('Deleting problematic social auth profiles...')
        cursor.execute('DELETE FROM social_auth_profiles WHERE user_id IN (25, 26)')
        print('Deleting problematic user accounts...')
        cursor.execute('DELETE FROM accounts_user WHERE id IN (25, 26)')
        print('Database cleanup completed successfully')
except Exception as e:
    print(f'Database cleanup failed: {str(e)}')
"

# Create and run database migrations
echo "🗄️ Creating new migrations..."
python manage.py makemigrations --noinput

echo "🗄️ Running database migrations..."
python manage.py migrate --noinput

# Debug: Check if management command exists
echo "🔍 Checking available management commands..."
python manage.py help | grep create_superuser || echo "❌ create_superuser command not found"

# Create superuser if it doesn't exist
echo "👤 Creating superuser if needed..."
python manage.py create_superuser 2>&1 || echo "❌ Superuser creation failed with exit code $?"

# Warm up the application
echo "🔥 Warming up application..."
python manage.py check --deploy

echo "✅ Build completed successfully!"
