# ⚡ Edge Functions + Postgres - Quick Reference Card

## 🎯 1-Minute Setup

### Install Package
```bash
npm install @vercel/postgres@^0.10.0
```

### Set Environment Variable (Vercel Dashboard)
```
POSTGRES_URL=postgresql://user:pass@host:5432/db?sslmode=require
```

### Create Edge Function
```typescript
// app/api/example/route.ts
import { sql } from "@vercel/postgres";
import { NextResponse } from "next/server";

export const runtime = "edge"; // ← THE KEY

export async function GET() {
  const { rows } = await sql`SELECT * FROM users LIMIT 10`;
  return NextResponse.json({ data: rows });
}
```

---

## 📖 Core SQL Operations

### SELECT
```typescript
const { rows } = await sql`
  SELECT id, name, email FROM users WHERE active = true
`;
```

### INSERT
```typescript
const { rows } = await sql`
  INSERT INTO users (name, email) 
  VALUES (${name}, ${email})
  RETURNING id, name, email
`;
```

### UPDATE
```typescript
const { rows } = await sql`
  UPDATE users 
  SET name = ${newName}, updated_at = NOW()
  WHERE id = ${userId}
  RETURNING id, name
`;
```

### DELETE
```typescript
const { rows } = await sql`
  DELETE FROM users WHERE id = ${userId}
  RETURNING id
`;
```

---

## 🔒 Security Best Practices

### ✅ SAFE - Parameterized Queries
```typescript
// Template literals automatically escape values
const { rows } = await sql`
  SELECT * FROM users WHERE email = ${userEmail}
`;
```

### ❌ UNSAFE - String Concatenation
```typescript
// NEVER DO THIS - SQL injection vulnerability
const { rows } = await sql.query(
  `SELECT * FROM users WHERE email = '${userEmail}'`
);
```

---

## 🎯 Production Patterns

### Error Handling
```typescript
try {
  const { rows } = await sql`SELECT * FROM jobs`;
  return NextResponse.json({ data: rows });
} catch (error) {
  return NextResponse.json(
    { error: "Database error" },
    { status: 500 }
  );
}
```

### With Authentication
```typescript
import { verifyAuth } from "@/lib/auth";

export async function POST(request: NextRequest) {
  const auth = await verifyAuth(request);
  if (!auth.success) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }
  
  const { rows } = await sql`
    INSERT INTO jobs (user_id, title) 
    VALUES (${auth.userId}, ${title})
    RETURNING id
  `;
  
  return NextResponse.json({ id: rows[0].id });
}
```

### With Validation
```typescript
import { z } from "zod";

const schema = z.object({
  title: z.string().min(3),
  email: z.string().email(),
});

export async function POST(request: NextRequest) {
  const body = await request.json();
  const validation = schema.safeParse(body);
  
  if (!validation.success) {
    return NextResponse.json(
      { error: validation.error.errors },
      { status: 400 }
    );
  }
  
  // Use validated data
  const { title, email } = validation.data;
  await sql`INSERT INTO users (title, email) VALUES (${title}, ${email})`;
}
```

---

## ⚡ Performance Tips

### 1. Select Only Needed Columns
```typescript
// ❌ Bad
const { rows } = await sql`SELECT * FROM users`;

// ✅ Good
const { rows } = await sql`SELECT id, name, email FROM users`;
```

### 2. Always Use LIMIT
```typescript
const { rows } = await sql`
  SELECT * FROM jobs 
  ORDER BY created_at DESC 
  LIMIT 50
`;
```

### 3. Create Indexes
```sql
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_jobs_active ON jobs(is_active);
```

### 4. Use Connection Pooling
```typescript
// ✅ Automatic with @vercel/postgres
import { sql } from "@vercel/postgres";

// ❌ No pooling with raw pg
import { Client } from "pg";
```

---

## 🔍 Common Query Patterns

### Pagination
```typescript
const page = 1;
const limit = 20;
const offset = (page - 1) * limit;

const { rows } = await sql`
  SELECT * FROM jobs 
  ORDER BY created_at DESC 
  LIMIT ${limit} OFFSET ${offset}
`;
```

### Search with ILIKE
```typescript
const { rows } = await sql`
  SELECT * FROM jobs 
  WHERE title ILIKE ${`%${searchTerm}%`}
  OR company ILIKE ${`%${searchTerm}%`}
`;
```

### JOIN Multiple Tables
```typescript
const { rows } = await sql`
  SELECT 
    j.id, j.title, 
    u.name as author,
    c.name as company_name
  FROM jobs j
  LEFT JOIN users u ON j.user_id = u.id
  LEFT JOIN companies c ON j.company_id = c.id
  WHERE j.is_active = true
`;
```

### Aggregate Functions
```typescript
const { rows } = await sql`
  SELECT 
    COUNT(*) as total,
    AVG(salary) as avg_salary,
    MAX(salary) as max_salary
  FROM jobs
  WHERE is_active = true
`;
```

### Conditional WHERE
```typescript
const location = searchParams.get("location");
const type = searchParams.get("type");

// Build query dynamically
let query = sql`SELECT * FROM jobs WHERE is_active = true`;

if (location) {
  query = sql`${query} AND location = ${location}`;
}
if (type) {
  query = sql`${query} AND job_type = ${type}`;
}

const { rows } = await query;
```

---

## 🐛 Troubleshooting

### Error: "Missing POSTGRES_URL"
**Solution:** Add `POSTGRES_URL` in Vercel Dashboard → Environment Variables

### Error: "Connection timeout"
**Solution:** Ensure connection string has `sslmode=require` and connection pooling

### Error: "Too many connections"
**Solution:** Use `@vercel/postgres` (automatic pooling), not raw `pg` client

### Error: "Cannot read property 'rows' of undefined"
**Solution:** Add error handling around queries

---

## 📊 Testing

### Local Development
```bash
npm run dev
curl http://localhost:3000/api/edge-sql-demo?operation=info
```

### Production Testing
```bash
# Test latency
curl -w "\nTime: %{time_total}s\n" \
  https://your-app.vercel.app/api/edge-sql-demo?operation=select
```

### Expected Performance
- USA: < 50ms
- Europe: < 60ms
- Asia: < 80ms

---

## 🎯 Key Takeaways

1. ✅ Use `export const runtime = "edge";`
2. ✅ Always parameterize user input
3. ✅ Use `@vercel/postgres` for automatic pooling
4. ✅ Add error handling to all queries
5. ✅ Select only needed columns
6. ✅ Add authentication for write operations
7. ✅ Use LIMIT on all queries
8. ✅ Create indexes for frequently queried columns

---

## 📚 Full Documentation
See: `EDGE_POSTGRES_GUIDE.md` for complete guide

## 🚀 Demo Endpoint
Visit: `/api/edge-sql-demo?operation=info`

---

**That's it! You now have Edge Functions + Postgres mastered! 🎉**
