# Database Migrations Guide

## Overview

This application uses **Alembic** for database schema migrations. This is the correct approach for production applications.

## ❌ Never Use `Base.metadata.create_all(engine)` in Production

**Why?**
- Creates race conditions when multiple instances start simultaneously
- No version control for schema changes
- No rollback capability
- Can cause data loss or inconsistencies

## ✅ Correct Approach: Alembic Migrations

### Initial Setup (Already Done)

```bash
# Install alembic
pip install alembic

# Initialize alembic (already done)
alembic init alembic
```

### Running Migrations

#### 1. Apply All Pending Migrations

```bash
# Run all pending migrations
alembic upgrade head
```

#### 2. View Migration History

```bash
# Show current migration version
alembic current

# Show migration history
alembic history --verbose
```

#### 3. Rollback Migrations

```bash
# Rollback one migration
alembic downgrade -1

# Rollback to specific version
alembic downgrade <revision_id>

# Rollback all migrations
alembic downgrade base
```

### Creating New Migrations

#### Auto-generate Migration from Model Changes

```bash
# Create migration with auto-detected changes
alembic revision --autogenerate -m "Description of changes"

# Review the generated migration file in alembic/versions/
# Edit if necessary

# Apply the migration
alembic upgrade head
```

#### Create Empty Migration

```bash
# Create empty migration for manual changes
alembic revision -m "Description of changes"

# Edit the generated file in alembic/versions/
# Add upgrade() and downgrade() logic

# Apply the migration
alembic upgrade head
```

### Deployment Workflows

#### Option 1: Manual Migration (Render Console)

```bash
# SSH into Render container or use Render CLI
render shell

# Run migrations
alembic upgrade head
```

#### Option 2: CI/CD Pipeline

Add to your deployment workflow:

```yaml
# .github/workflows/deploy.yml
- name: Run Database Migrations
  run: |
    alembic upgrade head
  env:
    DATABASE_URL: ${{ secrets.DATABASE_URL }}
```

#### Option 3: One-off Job (Recommended for Render)

Create a separate service in Render:
1. Clone your repository
2. Set `START_COMMAND` to: `alembic upgrade head`
3. Run once on each deployment
4. Set to "One-off" job type

### Environment Configuration

Make sure `DATABASE_URL` is set in your environment:

```bash
# Local development
export DATABASE_URL="postgresql://user:password@localhost:5432/database"

# Production (automatically set by Render/Render/Vercel)
# DATABASE_URL is provided by the platform
```

### Migration Best Practices

1. **Always review auto-generated migrations** - Alembic might not catch everything
2. **Test migrations on staging first** - Never run untested migrations in production
3. **Write reversible migrations** - Always implement `downgrade()` function
4. **Use descriptive names** - Make migration names meaningful
5. **One change per migration** - Keep migrations focused and small
6. **Backup before migrating** - Always have a backup before running migrations in production

### Common Migration Patterns

#### Adding a Column

```python
def upgrade():
    op.add_column('users', sa.Column('phone', sa.String(20), nullable=True))

def downgrade():
    op.drop_column('users', 'phone')
```

#### Creating an Index

```python
def upgrade():
    op.create_index('idx_users_email', 'users', ['email'])

def downgrade():
    op.drop_index('idx_users_email', 'users')
```

#### Adding a Foreign Key

```python
def upgrade():
    op.create_foreign_key(
        'fk_posts_user_id',
        'posts', 'users',
        ['user_id'], ['id'],
        ondelete='CASCADE'
    )

def downgrade():
    op.drop_constraint('fk_posts_user_id', 'posts', type_='foreignkey')
```

### Troubleshooting

#### "Database is not configured"

Make sure `DATABASE_URL` environment variable is set.

#### "Target database is not up to date"

```bash
# Check current version
alembic current

# Upgrade to latest
alembic upgrade head
```

#### "Can't locate revision"

```bash
# Stamp database with current schema
alembic stamp head
```

#### Migration Conflicts

```bash
# If multiple developers created migrations, you may need to merge
# Create a merge migration
alembic merge heads -m "Merge migrations"
```

### Production Checklist

- [ ] Migrations tested on staging environment
- [ ] Database backup created
- [ ] Downgrade strategy prepared
- [ ] Team notified of deployment
- [ ] Monitoring enabled
- [ ] Rollback plan documented

### Additional Resources

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Documentation](https://www.sqlalchemy.org/)
- [Database Migration Best Practices](https://www.sqlalchemy.org/library.html#migration)
