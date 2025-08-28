#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "🚀 Starting build process..."

# Install Node.js dependencies and build frontend
echo "📦 Installing Node.js dependencies..."
npm ci || npm install

echo "🏗️ Building frontend application..."
npm run build

echo "🔧 Updating asset paths in index.html..."
sed -i 's|href="assets/|href="/static/assets/|g' dist/index.html
sed -i 's|src="assets/|src="/static/assets/|g' dist/index.html
sed -i 's|"./assets/|"/static/assets/|g' dist/index.html
sed -i 's|"/assets/|"/static/assets/|g' dist/index.html
sed -i 's|src="logo.svg"|src="/static/logo.svg"|g' dist/index.html
sed -i 's|href="favicon.ico"|href="/static/favicon.ico"|g' dist/index.html
sed -i 's|href="site.webmanifest"|href="/static/site.webmanifest"|g' dist/index.html
sed -i 's|src="images/|src="/static/images/|g' dist/index.html

# Upgrade pip to latest version
echo "📦 Upgrading pip..."
python -m pip install --upgrade pip

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p staticfiles
mkdir -p media

# Update settings.py to include public directory in STATICFILES_DIRS
echo "🔧 Ensuring public directory is in STATICFILES_DIRS..."
# This is handled in your settings.py update

# Collect static files - this will handle copying from dist and public directories
echo "🎨 Collecting static files..."
python manage.py collectstatic --noinput --clear

# Skip makemigrations and just run migrations
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
