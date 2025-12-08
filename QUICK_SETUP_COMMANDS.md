# Quick Setup Commands

This guide provides quick commands to set up your local development environment for HireMeBahamas.

## Generate All Secrets at Once

Run this in your terminal to generate all secrets:

```bash
# Generate JWT_SECRET_KEY (32-byte hex)
echo "JWT_SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')"

# Generate SECRET_KEY (24-byte hex) 
echo "SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(24))')"
```

**OR** use the automated script:

```bash
./scripts/generate_secrets.sh
```

This will output both secrets in one go. Copy these values to your `.env` files.

---

## Create .env File for Local Development

### Backend Environment (.env or backend/.env)

Create a file named `.env` in the backend directory with the following content:

```bash
# backend/.env
DATABASE_URL=postgresql://localhost:5432/hiremebahamas_local
JWT_SECRET_KEY=your_jwt_secret_key_here
SECRET_KEY=your_flask_secret_key_here
FLASK_ENV=development
CORS_ORIGINS=http://localhost:5173
```

**Quick create command:**

```bash
cat > backend/.env << 'EOL'
DATABASE_URL=postgresql://localhost:5432/hiremebahamas_local
JWT_SECRET_KEY=your_jwt_secret_key_here
SECRET_KEY=your_flask_secret_key_here
FLASK_ENV=development
CORS_ORIGINS=http://localhost:5173
EOL
```

> **Note:** Replace `your_jwt_secret_key_here` and `your_flask_secret_key_here` with the secrets generated above.

### Frontend Environment (frontend/.env)

Create a file named `.env` in the frontend directory with the following content:

```bash
# frontend/.env
VITE_API_URL=http://localhost:8080
VITE_APP_NAME=HireMeBahamas
```

**Quick create command:**

```bash
cat > frontend/.env << 'EOL'
VITE_API_URL=http://localhost:8080
VITE_APP_NAME=HireMeBahamas
EOL
```

---

## Complete Setup Steps

1. **Generate secrets:**
   ```bash
   ./scripts/generate_secrets.sh
   ```

2. **Create backend .env file:**
   ```bash
   cp backend/.env.example backend/.env
   # Then edit backend/.env with your generated secrets
   ```

3. **Create frontend .env file:**
   ```bash
   cp frontend/.env.example frontend/.env
   # Edit if needed for local development
   ```

4. **Install dependencies:**
   ```bash
   # Backend
   pip install -r requirements.txt
   
   # Frontend
   cd frontend && npm install
   ```

5. **Start the application:**
   ```bash
   # Backend (in one terminal)
   python app.py
   
   # Frontend (in another terminal)
   cd frontend && npm run dev
   ```

---

## Environment Variable Reference

### Backend Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://localhost:5432/hiremebahamas_local` |
| `JWT_SECRET_KEY` | Secret for JWT token signing | Generate with `secrets.token_hex(32)` |
| `SECRET_KEY` | Flask session secret | Generate with `secrets.token_hex(24)` |
| `FLASK_ENV` | Flask environment | `development` or `production` |
| `CORS_ORIGINS` | Allowed CORS origins | `http://localhost:5173` |

### Frontend Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API URL | `http://localhost:8080` |
| `VITE_APP_NAME` | Application name | `HireMeBahamas` |

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'secrets'"

The `secrets` module is built into Python 3.6+. If you see this error, upgrade Python:

```bash
python3 --version  # Should be 3.6 or higher
```

### Database Connection Issues

If you can't connect to PostgreSQL:

1. Ensure PostgreSQL is running:
   ```bash
   # Linux/macOS
   sudo service postgresql status
   
   # macOS with Homebrew
   brew services list
   ```

2. Create the database:
   ```bash
   createdb hiremebahamas_local
   ```

3. Check your connection string format:
   ```
   postgresql://[user]:[password]@[host]:[port]/[database]
   ```

### Frontend Can't Connect to Backend

1. Verify backend is running on port 8080
2. Check CORS settings in backend
3. Ensure `VITE_API_URL` matches your backend URL

---

## Production Deployment

For production deployments, see:
- [Deployment Guide](./DEPLOYMENT_CONNECTION_GUIDE.md)
- [Vercel Setup](./VERCEL_POSTGRES_SETUP.md)
- [Railway Setup](./RAILWAY_DATABASE_SETUP.md)

**Important:** Never commit `.env` files with real secrets to version control!
