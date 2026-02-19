#!/bin/bash
set -e

echo "🚀 Setting up Halilit Support Center v9.7..."

# Install pnpm globally
echo "📦 Installing pnpm..."
npm install -g pnpm

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
pip install --upgrade pip
pip install -r backend/requirements.txt

# Install frontend dependencies
echo "⚛️  Installing frontend dependencies..."
cd frontend && pnpm install && cd ..

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Add your GOOGLE_API_KEY to .env file"
    echo "   Get it from: https://makersuite.google.com/app/apikey"
    echo ""
fi

echo "✅ Setup complete!"
echo ""
echo "Quick start:"
echo "  1. Add GOOGLE_API_KEY to .env file"
echo "  2. Start Docker services: docker-compose up -d"
echo "  3. Run backend: PYTHONPATH=. python3 backend/server.py"
echo "  4. Run frontend: cd frontend && pnpm dev"
echo ""
echo "Or use npm scripts:"
echo "  npm run dev          # Start both backend & frontend"
echo "  npm run dev:backend  # Backend only"
echo "  npm run dev:frontend # Frontend only"
echo ""
