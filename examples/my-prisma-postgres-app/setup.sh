#!/bin/bash

# Quick setup script for Prisma Postgres App
# This script automates the setup process described in README.md

set -e  # Exit on error

echo "🚀 Starting Prisma Postgres App setup..."
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

echo "✅ Node.js version: $(node --version)"
echo ""

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

echo "✅ npm version: $(npm --version)"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
npm install
echo "✅ Dependencies installed"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating from .env.example..."
    cp .env.example .env
    echo "📝 Please edit .env file and add your Prisma Postgres API key:"
    echo "   DATABASE_URL=\"prisma+postgres://accelerate.prisma-data.net/?api_key=YOUR_API_KEY_HERE\""
    echo ""
    echo "Get your API key from: https://console.prisma.io/"
    echo ""
    read -p "Press Enter after you've updated the .env file..."
fi

# Generate Prisma Client
echo "🔧 Generating Prisma Client..."
npx prisma generate
echo "✅ Prisma Client generated"
echo ""

# Ask user if they want to run migrations
read -p "Do you want to run database migrations? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔄 Running migrations..."
    npx prisma migrate dev --name init
    echo "✅ Migrations complete"
    echo ""
fi

# Ask user if they want to seed the database
read -p "Do you want to seed the database with sample data? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🌱 Seeding database..."
    npm run db:seed
    echo "✅ Database seeded"
    echo ""
fi

echo "🎉 Setup complete!"
echo ""
echo "To start the development server, run:"
echo "  npm run dev"
echo ""
echo "Then visit: http://localhost:3000"
