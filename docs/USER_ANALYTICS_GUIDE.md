# User Analytics & Login Monitoring Guide

## Overview

The User Analytics system provides comprehensive monitoring and diagnostic tools for tracking user login activity, identifying inactive users, and diagnosing login issues. This guide covers how to use both the web dashboard and command-line tools.

## Access Requirements

**Admin Only**: All analytics features require admin privileges (`is_admin=True` in the database or `user_type='admin'`).

## Web Dashboard

### Accessing the Dashboard

1. Log in as an admin user
2. Click on your profile menu (top right)
3. Select **"User Analytics"** from the dropdown
4. Or navigate directly to: `/admin/analytics/users`

### Dashboard Features

#### Key Metrics Cards

The dashboard displays four main metrics at the top:

1. **Total Users**: Total number of registered users
2. **Active Users (30 days)**: Users who logged in within the last 30 days
3. **Never Logged In**: Users who registered but never logged in
4. **Inactive Users (30+ days)**: Users who haven't logged in for 30+ days

#### Authentication Methods

Shows the breakdown of users by authentication method:
- **OAuth Users**: Users who sign in with Google/Apple
- **Password Users**: Users who use email/password login

Visual progress bars show the percentage distribution.

#### Login Activity

Displays login statistics for the last 30 days:
- **Total Logins**: Total successful logins
- **Avg per Day**: Average logins per day
- **Avg per Week**: Average logins per week
- **Failed Attempts**: Number of users with failed login attempts

#### Inactive Users Table

Load and view detailed information about inactive users:

1. **Select Threshold**: Choose inactivity threshold (7, 14, 30, 60, or 90 days)
2. **Click "Load Inactive Users"**: Fetches up to 100 inactive users
3. **Review Table**: View user details including:
   - User name and email
   - Last login date
   - Days since last login
   - Authentication method
   - Account status (active/inactive)

## API Endpoints

All endpoints require admin authentication via Bearer token.

### 1. Get Overall Statistics

```
GET /api/analytics/user-logins
```

Returns comprehensive login statistics including total users, active users, inactive users, authentication methods, and login activity metrics.

**Example Response:**
```json
{
  "total_users": 150,
  "active_users": {
    "last_30_days": 45,
    "last_7_days": 20
  },
  "never_logged_in": 10,
  "inactive_users_30d": 95,
  "authentication_methods": {
    "oauth_users": 60,
    "password_users": 90
  },
  "login_activity": {
    "total_logins_30d": 450,
    "avg_logins_per_day": 15.0,
    "avg_logins_per_week": 105.0
  }
}
```

### 2. Get Individual User History

```
GET /api/analytics/user-logins/{user_id}?limit=50
```

Returns detailed login history for a specific user.

**Parameters:**
- `user_id`: User ID (required)
- `limit`: Maximum login attempts to return (default: 50, max: 500)

### 3. Get Inactive Users

```
GET /api/analytics/inactive-users?days=30&limit=100&offset=0
```

Returns list of users who haven't logged in recently.

**Parameters:**
- `days`: Inactivity threshold in days (default: 30)
- `limit`: Maximum users to return (default: 100, max: 1000)
- `offset`: Pagination offset (default: 0)

### 4. Get Login Activity Timeline

```
GET /api/analytics/login-activity?days=30
```

Returns daily login counts for charting/visualization.

**Parameters:**
- `days`: Number of days to analyze (default: 30, max: 90)

## Diagnostic Tools

### Debug API Endpoints

Admin-only endpoints for diagnosing login issues:

#### Check User Login Status

```
GET /api/debug/user-login-status/{email}
```

Diagnoses why a specific user can't log in. Checks:
- User exists in database
- Account is active
- Password is set (or OAuth configuration)
- Recent failed login attempts
- Last successful login

**Example:**
```bash
curl -H "Authorization: Bearer $TOKEN" \
  https://api.hiremebahamas.com/api/debug/user-login-status/user@example.com
```

#### Recent Login Failures

```
GET /api/debug/recent-failures?hours=24&limit=50
```

View recent failed login attempts across all users to identify patterns or system-wide issues.

#### Problem Accounts

```
GET /api/debug/problem-accounts
```

Identifies accounts with potential issues:
- Users created but never logged in (30+ days)
- Inactive accounts
- Accounts with many failed login attempts
- Users with no authentication method configured

## Command-Line Scripts

### 1. Diagnose Login Issues

Run comprehensive diagnosis of all users:

```bash
# From the project root
python -m backend_app.scripts.diagnose_login_issues

# With auto-fix (attempts to fix common issues)
python -m backend_app.scripts.diagnose_login_issues --fix
```

**Checks performed:**
- Users with no authentication method
- Inactive accounts
- Users who never logged in (30+ days)
- Users with excessive failed login attempts
- Summary statistics

**Output:** Console report with issues found and recommendations.

### 2. Generate User Login Report

Create CSV export of all users and their login activity:

```bash
# Default output: reports/user_login_report_[date].csv
python -m backend_app.scripts.user_login_report

# Custom output location
python -m backend_app.scripts.user_login_report --output /path/to/report.csv
```

**CSV Columns:**
- `id`: User ID
- `email`: User email address
- `first_name`, `last_name`: User name
- `created_at`: Account creation date
- `last_login`: Last successful login date
- `days_since_login`: Days since last login
- `is_active`: Account status (yes/no)
- `is_admin`: Admin status (yes/no)
- `auth_method`: Authentication method (password/oauth_google/oauth_apple)
- `failed_attempts_30d`: Failed login attempts in last 30 days
- `location`: User location
- `role`: User role

## Interpreting the Metrics

### Activity Rate

**Formula:** `(Active Users 30d / Total Users) * 100`

**Guidelines:**
- **Below 30%**: Poor engagement - investigate inactive users
- **30-50%**: Average engagement - room for improvement
- **50-70%**: Good engagement
- **Above 70%**: Excellent engagement

### Never Logged In Users

High numbers may indicate:
- Registration issues
- Incomplete onboarding
- Email verification problems
- Users created for testing

**Action:** Review registration flow and onboarding experience.

### Failed Login Attempts

High failure rates may indicate:
- Password reset issues
- OAuth configuration problems
- Account confusion (using wrong auth method)
- Potential security issues

**Action:** Use diagnostic tools to identify patterns.

## Common Use Cases

### 1. Identify Inactive Users for Re-engagement

1. Open User Analytics dashboard
2. Set threshold to 30 days
3. Click "Load Inactive Users"
4. Export data (or use CSV report script)
5. Use email addresses for re-engagement campaign

### 2. Diagnose Why a User Can't Log In

1. Get user's email address from support request
2. Call debug endpoint: `GET /api/debug/user-login-status/{email}`
3. Review diagnostic report
4. Follow recommendations (e.g., reset password, check OAuth)

### 3. Monitor Login System Health

1. Check "Failed Attempts" metric on dashboard
2. If high, call `GET /api/debug/recent-failures?hours=24`
3. Review failure reasons for patterns
4. Address systemic issues (e.g., OAuth misconfiguration)

### 4. Generate Monthly Report

```bash
# Generate comprehensive CSV
python -m backend_app.scripts.user_login_report \
  --output reports/monthly_report_$(date +%Y%m).csv

# Run diagnostic
python -m backend_app.scripts.diagnose_login_issues > \
  reports/diagnostic_$(date +%Y%m).txt
```

## Best Practices

### Regular Monitoring

- **Daily**: Check dashboard for unusual activity
- **Weekly**: Review failed login patterns
- **Monthly**: Generate full user report
- **Quarterly**: Run diagnostic script for deep analysis

### Privacy & Security

- **Access Control**: Ensure only admins have access
- **Data Protection**: Handle user data according to privacy policy
- **Audit Logging**: All admin actions are logged
- **Email Campaigns**: Respect unsubscribe preferences

### Performance

- **Pagination**: Use offset/limit for large datasets
- **Caching**: Analytics data is cached for 5 minutes
- **Batch Operations**: For bulk actions, use scripts instead of API

## Troubleshooting

### Dashboard Won't Load

**Symptom:** Dashboard shows error or won't load
**Solutions:**
1. Verify you're logged in as admin
2. Check browser console for errors
3. Verify API endpoint is accessible
4. Check authentication token is valid

### No Data Showing

**Symptom:** Metrics show 0 or empty
**Solutions:**
1. Verify database contains users
2. Check LoginAttempt table exists (run migrations)
3. Ensure login tracking is active
4. Try refreshing the page

### Script Errors

**Symptom:** Command-line scripts fail
**Solutions:**
1. Verify Python environment is activated
2. Check DATABASE_URL is configured
3. Run from correct directory
4. Verify dependencies are installed

## Support

For issues or questions:
1. Check this guide first
2. Review diagnostic output
3. Check application logs
4. Contact development team

## Future Enhancements

Planned features:
- Email notification system for inactive users
- Scheduled reports via email
- Advanced charting and visualization
- Export to multiple formats (PDF, Excel)
- Custom date ranges for all reports
- Automated alerts for unusual activity
