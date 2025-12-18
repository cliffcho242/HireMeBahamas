# 🗄️ Database Admin Interface Guide

This guide explains how to use the built-in database admin interface (Adminer) to manage and inspect the HireMeBahamas PostgreSQL database.

## 📋 What is Adminer?

Adminer is a lightweight, full-featured database management tool that provides:
- ✅ Easy database inspection and querying
- ✅ Table browsing and editing
- ✅ SQL query execution
- ✅ Database schema visualization
- ✅ Import/Export capabilities
- ✅ User and permission management

## 🚀 Quick Start

### Step 1: Start the Services

Start the database and admin interface using Docker Compose:

```bash
# Start PostgreSQL and Adminer
docker-compose -f docker-compose.local.yml up -d postgres adminer

# Or start all services
docker-compose -f docker-compose.local.yml up -d
```

### Step 2: Access Adminer

Open your browser and navigate to:
```
http://localhost:8081
```

### Step 3: Login to Database

Use the following credentials (from docker-compose.yml):

**⚠️ Note**: These are default development credentials. For production, use strong, unique passwords and never commit them to version control.

| Field    | Value                    |
|----------|--------------------------|
| System   | PostgreSQL               |
| Server   | postgres                 |
| Username | hiremebahamas_user       |
| Password | hiremebahamas_password   |
| Database | hiremebahamas (optional) |

Click **Login** to access the database.

---

## 🎯 Common Tasks

### Viewing Tables

1. After logging in, you'll see a list of tables on the left sidebar
2. Click any table name to view its structure and data
3. Click "Select data" to see all records in the table

### Running SQL Queries

1. Click **SQL command** in the left sidebar
2. Enter your SQL query in the text area
3. Click **Execute** to run the query
4. Results will appear below

Example queries:
```sql
-- View all users
SELECT * FROM users;

-- Count total posts
SELECT COUNT(*) FROM posts;

-- Find users by location
SELECT * FROM users WHERE location = 'Nassau';

-- View recent posts with user info
SELECT p.*, u.first_name, u.last_name 
FROM posts p 
JOIN users u ON p.user_id = u.id 
ORDER BY p.created_at DESC 
LIMIT 10;
```

### Editing Data

1. Navigate to the table you want to edit
2. Click **Select data** to see records
3. Click **edit** next to any row to modify it
4. Make your changes and click **Save**

⚠️ **Caution**: Be careful when editing production data!

### Exporting Data

1. Click on a table name
2. Click **Export** in the toolbar
3. Choose format (SQL, CSV, etc.)
4. Click **Export** to download

### Importing Data

1. Click **Import** in the left sidebar
2. Choose your file (SQL or CSV)
3. Click **Execute** to import

---

## 🔧 Configuration

### Environment Variables

Adminer is configured in `docker-compose.yml` with these settings:

```yaml
adminer:
  image: adminer:latest
  ports:
    - "8081:8080"  # Access via http://localhost:8081
  environment:
    ADMINER_DEFAULT_SERVER: postgres
    ADMINER_DESIGN: pepa-linha  # Modern UI theme
  depends_on:
    postgres:
      condition: service_healthy
  restart: unless-stopped
```

### Customization

To change the port or theme:

1. Edit `docker-compose.yml`
2. Modify the `adminer` service settings:
   - Change `8081:8080` to use a different port
   - Change `ADMINER_DESIGN` for different themes (options: pepa-linha, nette, nette2, etc.)
3. Restart services:
   ```bash
   docker-compose restart adminer
   ```

---

## 🔒 Security Best Practices

### Development Environment

For local development, the default credentials are fine.

### Production Environment

⚠️ **IMPORTANT**: Do NOT expose Adminer publicly in production!

If you need database access in production:

1. **Use SSH Tunneling**:
   ```bash
   ssh -L 8081:localhost:8081 user@your-server.com
   ```

2. **Restrict Access**: Use firewall rules to limit access to trusted IPs

3. **Use Strong Passwords**: Change database passwords from defaults

4. **Use Render/Cloud Provider Tools**: Render provides a built-in database interface

### Render Production Setup

Render provides its own database interface:

1. Go to [Render Dashboard](https://render.app/dashboard)
2. Click on your PostgreSQL service
3. Click **"Data"** tab to view/query tables
4. No additional setup required!

For Render deployments, you don't need to deploy Adminer separately.

---

## 🔍 Troubleshooting

### Cannot Connect to Adminer

**Problem**: Browser shows "This site can't be reached" at localhost:8081

**Solution**:
```bash
# Check if Adminer is running
docker-compose ps adminer

# If not running, start it
docker-compose -f docker-compose.local.yml up -d adminer

# Check logs
docker-compose -f docker-compose.local.yml logs adminer
```

### Login Failed

**Problem**: "Login without password is forbidden"

**Solution**:
- Verify you're using the correct credentials from docker-compose.yml
- Server should be `postgres` (not `localhost`)
- Check if PostgreSQL is running:
  ```bash
  docker-compose ps postgres
  ```

### Database Not Found

**Problem**: "Database does not exist"

**Solution**:
- Leave the Database field empty on login
- After logging in, you can create or select the database
- Or verify the database exists:
  ```bash
  docker-compose exec postgres psql -U hiremebahamas_user -l
  ```

### Tables Not Showing

**Problem**: Database appears empty

**Solution**:
- Ensure backend has initialized tables
- Run migrations:
  ```bash
  docker-compose exec backend-flask python create_all_tables.py
  ```

### Adminer Container Keeps Restarting

**Problem**: Adminer service is unhealthy

**Solution**:
```bash
# Check logs
docker-compose -f docker-compose.local.yml logs adminer

# Check PostgreSQL health
docker-compose ps postgres

# Restart services
docker-compose restart postgres adminer
```

---

## 📊 Alternative Database Interfaces

### pgAdmin (More Features)

If you prefer pgAdmin over Adminer, add this to docker-compose.yml:

```yaml
  pgadmin:
    image: dpage/pgadmin4:latest
    ports:
      - "8082:80"
    environment:
      PGADMIN_DEFAULT_EMAIL: admin@hiremebahamas.com
      PGADMIN_DEFAULT_PASSWORD: admin123
    depends_on:
      - postgres
    volumes:
      - pgadmin_data:/var/lib/pgadmin
```

Then add to volumes:
```yaml
volumes:
  pgadmin_data:
```

Access at: http://localhost:8082

### Render Database Interface

For production deployments on Render:
1. No additional setup needed
2. Built-in database viewer in Render dashboard
3. More secure than exposing Adminer publicly

---

## 🎓 Learning Resources

### Adminer Documentation
- [Official Adminer Site](https://www.adminer.org/)
- [Adminer Docker Hub](https://hub.docker.com/_/adminer)

### PostgreSQL Resources
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [PostgreSQL Tutorial](https://www.postgresqltutorial.com/)

### SQL Learning
- [SQL Tutorial](https://www.sqltutorial.org/)
- [PostgreSQL Exercises](https://pgexercises.com/)

---

## ✅ Quick Reference

### Start Services
```bash
docker-compose -f docker-compose.local.yml up -d
```

### Access Adminer
```
http://localhost:8081
```

### Login Credentials (Development)
- **Server**: postgres
- **Username**: hiremebahamas_user
- **Password**: hiremebahamas_password
- **Database**: hiremebahamas

### Stop Services
```bash
docker-compose -f docker-compose.local.yml down
```

### View Logs
```bash
# Adminer logs
docker-compose -f docker-compose.local.yml logs -f adminer

# Database logs
docker-compose -f docker-compose.local.yml logs -f postgres
```

### Restart Adminer
```bash
docker-compose restart adminer
```

---

## 🎉 Success Indicators

After setup, you should be able to:
- ✅ Access Adminer at http://localhost:8081
- ✅ Login with PostgreSQL credentials
- ✅ View all database tables
- ✅ Run SQL queries
- ✅ Edit database records
- ✅ Export/import data

---

**Need Help?** Check the [Troubleshooting](#-troubleshooting) section or refer to the [PostgreSQL Setup Guide](./POSTGRESQL_SETUP.md).
