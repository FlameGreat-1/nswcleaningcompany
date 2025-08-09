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

# Create and run database migrations
echo "🗄️ Creating new migrations..."
python manage.py makemigrations --noinput

echo "🗄️ Running database migrations..."
python manage.py migrate --noinput

# Create superuser if it doesn't exist
echo "👤 Creating superuser if needed..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    try:
        User.objects.create_superuser(
            email='admin@nswcleaningcompany.com.au',
            password='admin123',
            first_name='Admin',
            last_name='User'
        )
        print("✅ Superuser created successfully")
    except Exception as e:
        print(f"❌ Error creating superuser: {e}")
else:
    print("✅ Superuser already exists")
EOF

# Warm up the application
echo "🔥 Warming up application..."
python manage.py check --deploy

echo "✅ Build completed successfully!"

#####################################################~~~~~~~~~~~~~~~~~ FLAME GREAT ~~~~~~~~~~~~~~~~~~~~~~~~~~#########################################################