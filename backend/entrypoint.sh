#!/bin/bash
set -e

# Install Tailwind dependencies if node_modules doesn't exist
if [ ! -d "/app/theme/static_src/node_modules" ]; then
    echo "Installing Tailwind dependencies..."
    python manage.py tailwind install
fi

# Build Tailwind CSS
echo "Building Tailwind CSS..."
python manage.py tailwind build

# Execute the main command
exec "$@"
