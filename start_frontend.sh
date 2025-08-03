#!/bin/bash

# Start Trading Bot Frontend
echo "🌐 Starting Trading Bot Frontend..."

cd frontend

# Install Composer dependencies if needed
if [ ! -d "vendor" ]; then
    echo "📦 Installing Composer dependencies..."
    composer install --no-dev --optimize-autoloader
fi

# Generate key if needed
if ! grep -q "APP_KEY=base64:" .env 2>/dev/null; then
    echo "🔑 Generating application key..."
    php artisan key:generate --force
fi

# Run migrations
echo "🗄️  Setting up database..."
php artisan migrate --force

# Ensure backend URL is configured
if ! grep -q "BACKEND_URL" .env 2>/dev/null; then
    echo "⚙️  Configuring backend connection..."
    echo "BACKEND_URL=http://localhost:8080" >> .env
fi

echo ""
echo "🌐 Starting frontend server on port 8000..."
php artisan serve --port=8000