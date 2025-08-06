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

# Install additional production dependencies if not in requirements.txt
echo "📦 Installing production dependencies..."
pip install gunicorn whitenoise psycopg2-binary

# Collect static files
echo "🎨 Collecting static files..."
python manage.py collectstatic --noinput --clear

# Run database migrations
echo "🗄️ Running database migrations..."
python manage.py migrate --noinput

# Create superuser if it doesn't exist (optional)
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

# Load initial data if fixtures exist
if [ -d "fixtures" ]; then
    echo "📊 Loading initial data..."
    python manage.py loaddata fixtures/*.json || echo "⚠️ No fixtures to load or error loading fixtures"
fi

# Warm up the application
echo "🔥 Warming up application..."
python manage.py check --deploy

echo "✅ Build completed successfully!"
