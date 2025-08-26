#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "🚀 Starting build process..."

# Install Node.js dependencies and build frontend
echo "📦 Installing Node.js dependencies..."
npm ci || npm install

echo "🏗️ Building frontend application..."
npm run build

# Upgrade pip to latest version
echo "📦 Upgrading pip..."
python -m pip install --upgrade pip

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

echo "📦 Copying frontend assets to staticfiles..."
cp -r dist/* staticfiles/

# Collect static files
echo "🎨 Collecting static files..."
python manage.py collectstatic --noinput --clear

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
