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

# Create a temporary cleanup command
echo "🧹 Creating database cleanup command..."
mkdir -p accounts/management/commands
cat > accounts/management/commands/cleanup_database.py << 'EOF'
from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Cleans up problematic database entries'

    def handle(self, *args, **options):
        self.stdout.write('Cleaning up database...')
        try:
            with connection.cursor() as cursor:
                self.stdout.write('Deleting problematic client profiles...')
                cursor.execute('DELETE FROM client_profiles WHERE user_id IN (25, 26)')
                self.stdout.write('Deleting problematic social auth profiles...')
                cursor.execute('DELETE FROM social_auth_profiles WHERE user_id IN (25, 26)')
                self.stdout.write('Deleting problematic user accounts...')
                cursor.execute('DELETE FROM accounts_user WHERE id IN (25, 26)')
                self.stdout.write(self.style.SUCCESS('Database cleanup completed successfully'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Database cleanup failed: {str(e)}'))
EOF

# Run the cleanup command
echo "🧹 Running database cleanup..."
python manage.py cleanup_database

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

# Remove temporary cleanup command
echo "🧹 Removing temporary cleanup command..."
rm -f accounts/management/commands/cleanup_database.py

echo "✅ Build completed successfully!"
