# My Prisma Postgres App

This is an example Next.js application using Prisma with Prisma Postgres (Accelerate) for database management.

## 🚀 Quick Start

Follow these steps to set up and run the application:

### Prerequisites

- Node.js 18+ installed
- A Prisma Postgres account (free tier available at [console.prisma.io](https://console.prisma.io/))

### Automated Setup (Recommended)

```bash
cd my-prisma-postgres-app

# Make the setup script executable (if needed)
chmod +x setup.sh

# Run the setup script
./setup.sh
```

The script will:
1. Install dependencies
2. Create .env file from template
3. Generate Prisma Client
4. Optionally run migrations
5. Optionally seed the database

### Manual Setup Instructions

```bash
cd my-prisma-postgres-app

# 1. Install dependencies
npm install

# 2. Create .env file with DATABASE_URL
# Copy .env.example to .env and add your API key
cp .env.example .env
# Edit .env: DATABASE_URL="prisma+postgres://accelerate.prisma-data.net/?api_key=YOUR_KEY"

# 3. Generate Prisma Client
npx prisma generate

# 4. Run migrations
npx prisma migrate dev --name init

# 5. Seed database (optional)
npm run db:seed

# 6. Start development server
npm run dev
```

### Starting Fresh with Prisma Init

If you want to initialize Prisma from scratch (without our example schema):

```bash
cd my-prisma-postgres-app

# 1. Initialize Prisma Postgres database
npx prisma init --db

# 2. Create .env file with DATABASE_URL
# DATABASE_URL="prisma+postgres://accelerate.prisma-data.net/?api_key=YOUR_KEY"

# 3. Run migrations
npx prisma migrate dev --name init

# 4. Seed database (optional)
npx prisma db seed

# 5. Start development server
npm run dev
```

## 📋 Detailed Setup Guide

### Step 1: Initialize Prisma Postgres

The `npx prisma init --db` command will:
- Create a `prisma` directory with `schema.prisma`
- Set up the Prisma Client
- Create a `.env.example` file

### Step 2: Configure Database Connection

1. Sign up for Prisma Postgres at [console.prisma.io](https://console.prisma.io/)
2. Create a new project and database
3. Copy your API key
4. Create a `.env` file in the project root:

```env
DATABASE_URL="prisma+postgres://accelerate.prisma-data.net/?api_key=YOUR_API_KEY_HERE"
```

### Step 3: Run Migrations

This command creates your database tables based on the schema:

```bash
npx prisma migrate dev --name init
```

This will:
- Create the tables defined in `schema.prisma`
- Generate the Prisma Client
- Apply the migration to your database

### Step 4: Seed the Database (Optional)

Populate your database with sample data:

```bash
npx prisma db seed
```

This runs the `prisma/seed.js` script which creates:
- 2 sample users (Alice and Bob)
- 3 sample posts

### Step 5: Start Development Server

```bash
npm run dev
```

Visit [http://localhost:3000](http://localhost:3000) to see your app.

## 📁 Project Structure

```
my-prisma-postgres-app/
├── prisma/
│   ├── schema.prisma      # Database schema
│   └── seed.js            # Seed script
├── .env                   # Environment variables (not in git)
├── .env.example           # Example env vars
├── package.json           # Dependencies and scripts
└── README.md              # This file
```

## 🗄️ Database Schema

The example includes two models:

- **User**: Stores user information (email, name)
- **Post**: Stores blog posts with author relationship

See `prisma/schema.prisma` for the complete schema definition.

## 📚 Prisma Commands

```bash
# Generate Prisma Client after schema changes
npx prisma generate

# Create a new migration
npx prisma migrate dev --name your_migration_name

# Apply migrations in production
npx prisma migrate deploy

# Open Prisma Studio (visual database editor)
npx prisma studio

# Reset database (WARNING: deletes all data)
npx prisma migrate reset

# Seed database
npx prisma db seed
```

## 🔧 Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | Prisma Postgres connection string with Accelerate | `prisma+postgres://accelerate.prisma-data.net/?api_key=xxx` |
| `DIRECT_DATABASE_URL` | (Optional) Direct PostgreSQL connection | `postgresql://user:pass@host:5432/db` |

## 🎯 Features

- ✅ **Prisma Postgres**: Managed PostgreSQL with global edge caching
- ✅ **Prisma Accelerate**: < 100ms query latency worldwide
- ✅ **Type Safety**: Full TypeScript support with Prisma Client
- ✅ **Migrations**: Version-controlled database schema changes
- ✅ **Seeding**: Easy database population for development

## 🚀 Deployment

### Vercel Deployment

1. Push your code to GitHub
2. Connect your repo to Vercel
3. Add the `DATABASE_URL` environment variable in Vercel dashboard
4. Deploy!

### Render Deployment

1. Connect your repo to Render
2. Add the `DATABASE_URL` environment variable
3. Deploy!

## 📖 Learn More

- [Prisma Documentation](https://www.prisma.io/docs)
- [Prisma Postgres Documentation](https://www.prisma.io/docs/accelerate/getting-started)
- [Prisma Accelerate](https://www.prisma.io/docs/accelerate)
- [Next.js Documentation](https://nextjs.org/docs)

## 🤝 Contributing

This is an example application. Feel free to modify it for your needs!

## 📄 License

MIT
