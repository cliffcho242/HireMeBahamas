# 🗄️ Database Interface - Quick Reference

## Quick Access

**URL**: http://localhost:8081

## Login Credentials

| Field    | Value                  |
|----------|------------------------|
| System   | PostgreSQL             |
| Server   | postgres               |
| Username | hiremebahamas_user     |
| Password | hiremebahamas_password |
| Database | hiremebahamas          |

## Start Database Interface

```bash
# Start PostgreSQL and Adminer
docker-compose up -d postgres adminer

# Check status
docker-compose ps adminer

# View logs
docker-compose logs -f adminer
```

## Common SQL Queries

```sql
-- View all users
SELECT * FROM users;

-- Count posts
SELECT COUNT(*) FROM posts;

-- Recent activity
SELECT u.first_name, u.last_name, p.content, p.created_at
FROM posts p
JOIN users u ON p.user_id = u.id
ORDER BY p.created_at DESC
LIMIT 20;

-- Users by location
SELECT location, COUNT(*) as count
FROM users
GROUP BY location
ORDER BY count DESC;
```

## Troubleshooting

**Cannot access Adminer?**
```bash
docker-compose restart adminer
```

**Login fails?**
- Check server name is `postgres` (not localhost)
- Verify PostgreSQL is running: `docker-compose ps postgres`

**Need more help?**
📖 See [DATABASE_ADMIN_INTERFACE.md](./DATABASE_ADMIN_INTERFACE.md)
