# HireMeBahamas Deployment Guide

## Phase 1: Web Deployment (DO THIS BEFORE APP STORES)

### Why Deploy Website First?
1. ✅ Test with real users
2. ✅ Gather feedback
3. ✅ Build user base
4. ✅ Satisfy app store requirements
5. ✅ Faster updates and fixes

---

## Vercel CLI 48.12.0 - 5-Step Deploy Checklist

> **IMPORTANT:** The `vercel.json` is already configured correctly. Follow these steps for guaranteed success.

### Step 1: Update Vercel CLI & Clear Cache
```bash
npm i -g vercel@latest && vercel --version && rm -rf .vercel
```

### Step 2: Verify vercel.json (Already Fixed)
The runtime has been removed from the functions block - Vercel auto-detects Python 3.12:
```json
"functions": {
  "api/**/*.py": {
    "maxDuration": 30
  }
}
```

### Step 3: Deploy to Vercel
```bash
vercel --prod
```

### Step 4: Verify Build Succeeds
```bash
curl https://your-project.vercel.app/api/health
```

### Step 5: Confirm Git Integration (Dashboard)
- Go to: https://vercel.com/dashboard
- Select project → Settings → Git
- Ensure "Production Branch" is set to `main`

### ✅ Expected Results:
- Build succeeds in <30 seconds
- No "Function Runtimes must have a valid version" errors
- Python API functions work at `/api/*`
- Static React/Vite frontend served correctly

---

## RECOMMENDED: Quick Free Deployment

### Option 1: Vercel (Frontend) + Railway (Backend)

#### A. Deploy Backend to Railway

1. **Create Railway Account:**
   - Go to: https://railway.app
   - Sign up with GitHub

2. **Create New Project:**
   ```
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Connect your HireMeBahamas repository
   ```

3. **Configure Backend:**
   Create `railway.json` in root:
   ```json
   {
     "build": {
       "builder": "NIXPACKS"
     },
     "deploy": {
       "startCommand": "gunicorn -w 4 -b 0.0.0.0:$PORT final_backend:app",
       "restartPolicyType": "ON_FAILURE",
       "restartPolicyMaxRetries": 10
     }
   }
   ```

4. **Add Environment Variables in Railway:**
   ```
   SECRET_KEY=your-production-secret-key-here
   DATABASE_URL=postgresql://... (Railway provides this)
   FLASK_ENV=production
   ```
   
   📖 **[Detailed DATABASE_URL Setup Guide](./RAILWAY_DATABASE_SETUP.md)** - Complete step-by-step instructions for adding PostgreSQL to Railway.

5. **Deploy:**
   - Railway auto-deploys on git push
   - Get your backend URL: `https://your-app.railway.app`

#### B. Deploy Frontend to Vercel

1. **Create Vercel Account:**
   - Go to: https://vercel.com
   - Sign up with GitHub

2. **Import Project:**
   ```
   - Click "New Project"
   - Import from GitHub
   - Select HireMeBahamas/frontend folder
   ```

3. **Configure Build:**
   ```
   Build Command: npm run build
   Output Directory: dist
   Install Command: npm install
   ```

4. **Add Environment Variables in Vercel:**
   ```
   VITE_API_URL=https://your-backend.railway.app
   VITE_SOCKET_URL=https://your-backend.railway.app
   ```

5. **Deploy:**
   - Vercel auto-deploys
   - Get your frontend URL: `https://hiremebahamas.vercel.app`

---

## Option 2: All-in-One (DigitalOcean)

### Cost: $6/month for basic droplet

1. **Create Droplet:**
   ```
   - Ubuntu 22.04
   - Basic plan: $6/month
   - Choose region closest to Bahamas (Miami)
   ```

2. **Install Dependencies:**
   ```bash
   # SSH into droplet
   ssh root@your-droplet-ip
   
   # Update system
   apt update && apt upgrade -y
   
   # Install Node.js
   curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
   apt install -y nodejs
   
   # Install Python
   apt install -y python3-pip python3-venv nginx
   
   # Install PM2 for process management
   npm install -g pm2
   ```

3. **Deploy Backend:**
   ```bash
   # Clone repository
   git clone https://github.com/yourusername/HireMeBahamas.git
   cd HireMeBahamas
   
   # Setup Python environment
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   
   # Start backend with PM2
   pm2 start "gunicorn -w 4 -b 127.0.0.1:9999 final_backend:app" --name hireme-backend
   pm2 save
   pm2 startup
   ```

4. **Deploy Frontend:**
   ```bash
   cd frontend
   npm install
   npm run build
   
   # Copy build to nginx
   cp -r dist/* /var/www/html/
   ```

5. **Configure Nginx:**
   ```bash
   nano /etc/nginx/sites-available/hiremebahamas
   ```
   
   Add:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       # Frontend
       location / {
           root /var/www/html;
           try_files $uri $uri/ /index.html;
       }
       
       # Backend API
       location /api {
           proxy_pass http://127.0.0.1:9999;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

6. **Enable and Start:**
   ```bash
   ln -s /etc/nginx/sites-available/hiremebahamas /etc/nginx/sites-enabled/
   nginx -t
   systemctl restart nginx
   ```

7. **Add SSL (Free):**
   ```bash
   apt install -y certbot python3-certbot-nginx
   certbot --nginx -d your-domain.com
   ```

---

## Database Migration (SQLite → PostgreSQL)

For production, migrate to PostgreSQL:

### On Railway/DigitalOcean:

1. **Create PostgreSQL database**
2. **Update connection string:**
   ```python
   # In final_backend.py
   DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///hiremebahamas.db')
   
   if DATABASE_URL.startswith('postgres://'):
       # Use PostgreSQL
       from sqlalchemy import create_engine
       engine = create_engine(DATABASE_URL.replace('postgres://', 'postgresql://'))
   else:
       # Keep SQLite for local
       conn = sqlite3.connect(DATABASE_URL)
   ```

3. **Migrate data:**
   ```bash
   # Export from SQLite
   sqlite3 hiremebahamas.db .dump > backup.sql
   
   # Import to PostgreSQL (after converting syntax)
   psql $DATABASE_URL < backup.sql
   ```

---

## Pre-Deployment Checklist

### Backend:
- [ ] Update SECRET_KEY to production value
- [ ] Set FLASK_ENV=production
- [ ] Update CORS origins to production domain
- [ ] Configure production database
- [ ] Add error monitoring (Sentry)
- [ ] Set up logging
- [ ] Add rate limiting
- [ ] Configure file upload limits

### Frontend:
- [ ] Update API URLs to production
- [ ] Enable production build optimizations
- [ ] Add Google Analytics
- [ ] Configure error tracking
- [ ] Add privacy policy page
- [ ] Add terms of service page
- [ ] Add contact/support page

### Security:
- [ ] HTTPS enabled (SSL certificate)
- [ ] Secure password hashing (bcrypt) ✓
- [ ] JWT token expiration configured ✓
- [ ] Input validation on all endpoints ✓
- [ ] SQL injection protection ✓
- [ ] XSS protection
- [ ] CSRF protection

---

## Testing Production Deployment

1. **Load Testing:**
   ```bash
   # Install Apache Bench
   apt install apache2-utils
   
   # Test backend
   ab -n 1000 -c 10 https://your-backend.com/api/health
   ```

2. **Security Testing:**
   ```bash
   # Install OWASP ZAP or use online tools
   # Scan: https://securityheaders.com
   ```

3. **Performance Testing:**
   - Google PageSpeed Insights
   - GTmetrix
   - WebPageTest

---

## Domain Setup

### Get a Domain:
1. **Namecheap** - $8.88/year for .com
2. **GoDaddy** - Similar pricing
3. **Google Domains** - $12/year

### Configure DNS:
```
A Record: @ → Your server IP
A Record: www → Your server IP
CNAME: api → your-backend.railway.app (if using Railway)
```

---

## Monitoring & Analytics

### Add to Frontend:
```typescript
// Google Analytics
import ReactGA from 'react-ga4';
ReactGA.initialize('G-XXXXXXXXXX');

// Track page views
ReactGA.send({ hitType: "pageview", page: window.location.pathname });
```

### Add to Backend:
```python
# Sentry error tracking
import sentry_sdk
sentry_sdk.init(dsn="your-sentry-dsn")
```

---

## Post-Deployment

### 1. Test Everything:
- [ ] User registration
- [ ] User login
- [ ] Profile updates
- [ ] Job posting
- [ ] Search functionality
- [ ] All API endpoints

### 2. Monitor:
- [ ] Server uptime
- [ ] Error rates
- [ ] Response times
- [ ] User activity

### 3. Gather Feedback:
- [ ] Add feedback form
- [ ] Monitor user issues
- [ ] Track feature requests
- [ ] Analyze usage patterns

---

## Timeline

### Week 1: Deploy to Free Platforms
- Deploy backend to Railway
- Deploy frontend to Vercel
- Test thoroughly

### Week 2-4: Beta Testing
- Invite users to test
- Gather feedback
- Fix bugs
- Improve UX

### Week 5-6: App Development
- Create React Native apps
- Test on iOS/Android
- Prepare app store listings

### Week 7-8: App Store Submission
- Submit to Apple App Store
- Submit to Google Play Store
- Include website URL in listings

---

## Cost Breakdown

### Free Option (Recommended for Start):
- **Railway Backend:** Free tier (500 hrs/month)
- **Vercel Frontend:** Free tier (unlimited)
- **Domain:** $8.88/year (optional)
- **Total:** ~$0-9/year

### Paid Option (More Control):
- **DigitalOcean Droplet:** $6/month
- **Domain:** $8.88/year
- **SSL Certificate:** Free (Let's Encrypt)
- **Total:** ~$72/year + $9 = $81/year

---

## Next Steps

1. **Push code to GitHub** (if not already)
2. **Choose deployment platform** (Railway + Vercel recommended)
3. **Deploy backend first**
4. **Deploy frontend** 
5. **Test thoroughly**
6. **Share with beta users**
7. **Gather feedback**
8. **Iterate and improve**
9. **Start app development**
10. **Submit to app stores**

---

## Resources

- **Railway Docs:** https://docs.railway.app
- **Vercel Docs:** https://vercel.com/docs
- **DigitalOcean Tutorials:** https://www.digitalocean.com/community/tutorials
- **Flask Deployment:** https://flask.palletsprojects.com/en/2.3.x/deploying/
- **React Deployment:** https://create-react-app.dev/docs/deployment/

---

**Remember:** Start with the free web deployment, test with real users, gather feedback, THEN build and submit mobile apps. This approach significantly increases your success rate! 🚀
