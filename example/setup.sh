#!/bin/bash
# Quick setup script for the demo project

set -e

echo "=========================================="
echo "Thumbnail Choice Block Demo Setup"
echo "=========================================="
echo ""

# Check if we're in a virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Warning: No virtual environment detected"
    echo "   It's recommended to create one first:"
    echo "   python -m venv venv"
    echo "   source venv/bin/activate  # On Windows: venv\\Scripts\\activate"
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "📦 Installing wagtail-thumbnail-choice-block..."
pip install -e ..

echo ""
echo "🗄️  Running database migrations..."
python manage.py migrate

echo ""
echo "🚀 Setting up demo site..."
python manage.py setup_demo

echo ""
echo "=========================================="
echo "✅ Setup complete!"
echo "=========================================="
echo ""
echo "To start the demo:"
echo "  python manage.py runserver"
echo ""
echo "Then visit:"
echo "  Frontend: http://localhost:8000/"
echo "  Admin:    http://localhost:8000/admin/"
echo "  Login:    admin / admin"
echo ""
