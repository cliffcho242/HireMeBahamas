@echo off
REM ============================================
REM  Step 5: Share With Users & Marketing
REM  Beta Launch Strategy
REM ============================================

echo.
echo ============================================
echo   Step 5: Share HireMeBahamas
echo ============================================
echo.

REM Read Vercel URL
if exist VERCEL_URL.txt (
    set /p VERCEL_URL=<VERCEL_URL.txt
) else (
    set /p VERCEL_URL="Enter your Vercel URL: "
)

echo Your HireMeBahamas site is live at:
echo %VERCEL_URL%
echo.

echo ============================================
echo   BETA LAUNCH STRATEGY
echo ============================================
echo.

echo Phase 1: Friends & Family (Week 1)
echo ------------------------------------
echo 1. Share with 5-10 people you know
echo 2. Ask them to create accounts and test
echo 3. Gather initial feedback
echo 4. Fix any obvious bugs
echo.
pause

echo Phase 2: Social Media Launch (Week 2)
echo ---------------------------------------
echo 1. Create Facebook Business Page for HireMeBahamas
echo 2. Post about the launch in Bahamian groups:
echo    - Bahamas Jobs
echo    - Nassau/Freeport community groups
echo    - Professional networking groups
echo.
echo 3. Instagram Posts:
echo    - Share screenshots of the platform
echo    - Use hashtags: #BahamasJobs #HireBahamas #242Jobs
echo.
echo 4. Twitter/X:
echo    - Announce launch
echo    - Tag Bahamian influencers
echo.
pause

echo Phase 3: Direct Outreach (Week 3-4)
echo -------------------------------------
echo 1. Email local businesses:
echo    - Hotels, restaurants, retail stores
echo    - Offer free job posting for first month
echo.
echo 2. Contact Bahamian recruitment agencies
echo 3. Reach out to Bahamian universities:
echo    - College of the Bahamas
echo    - Share with career services
echo.
pause

echo ============================================
echo   MARKETING MATERIALS
echo ============================================
echo.

echo Creating shareable content...
echo.

REM Create a shareable message
(
echo 🇧🇸 HireMeBahamas is LIVE! 🇧🇸
echo.
echo The Bahamas' new job platform connecting Bahamian talent with opportunities!
echo.
echo ✅ Create your profile
echo ✅ Find jobs in Nassau, Freeport, and beyond
echo ✅ Post job openings
echo ✅ 100%% FREE to use
echo.
echo Visit: %VERCEL_URL%
echo.
echo #BahamasJobs #HireBahamas #242 #CareerBahamas
) > SHARE_MESSAGE.txt

echo.
echo Share message created: SHARE_MESSAGE.txt
echo.

echo ============================================
echo   SOCIAL MEDIA POST IDEAS
echo ============================================
echo.

(
echo POST 1 - ANNOUNCEMENT
echo ----------------------
echo 🎉 Introducing HireMeBahamas! 🇧🇸
echo.
echo Finding a job or hiring in the Bahamas just got easier!
echo.
echo Our new platform connects Bahamian job seekers with employers across all islands.
echo.
echo 👉 Visit: %VERCEL_URL%
echo.
echo #BahamasJobs #HireBahamas #CareerBahamas
echo.
echo.
echo POST 2 - JOB SEEKERS
echo ---------------------
echo 💼 Looking for work in the Bahamas? 🇧🇸
echo.
echo HireMeBahamas makes job hunting simple:
echo ✅ Browse hundreds of jobs
echo ✅ Apply with one click
echo ✅ Track your applications
echo ✅ Get matched with opportunities
echo.
echo Start your job search: %VERCEL_URL%
echo.
echo #BahamasJobs #JobSearch #242Jobs
echo.
echo.
echo POST 3 - EMPLOYERS
echo ------------------
echo 📢 Hiring in the Bahamas? 🇧🇸
echo.
echo Post your jobs on HireMeBahamas and reach qualified Bahamian talent:
echo ✅ FREE job postings
echo ✅ Reach local candidates
echo ✅ Easy application management
echo ✅ Find the right fit
echo.
echo Post a job now: %VERCEL_URL%
echo.
echo #BahamasJobs #Hiring #BahamasBusiness
echo.
echo.
echo POST 4 - ISLAND FOCUS
echo ----------------------
echo 🏝️ Jobs in Nassau, Freeport, Eleuthera, Abaco, and beyond! 🇧🇸
echo.
echo HireMeBahamas connects talent across all Bahamian islands.
echo.
echo Whether you're in the capital or the Family Islands, find opportunities near you.
echo.
echo Start today: %VERCEL_URL%
echo.
echo #BahamasJobs #FamilyIslands #242
) > SOCIAL_MEDIA_POSTS.txt

echo.
echo Social media posts created: SOCIAL_MEDIA_POSTS.txt
echo.

echo ============================================
echo   EMAIL TEMPLATE FOR BUSINESSES
echo ============================================
echo.

(
echo Subject: Introducing HireMeBahamas - Find Bahamian Talent
echo.
echo Dear [Business Name],
echo.
echo I'm excited to introduce HireMeBahamas (%VERCEL_URL%), 
echo a new job platform designed specifically for the Bahamian market.
echo.
echo As a local business, you can:
echo • Post job openings for FREE
echo • Reach qualified Bahamian candidates
echo • Manage applications easily
echo • Find the right talent for your team
echo.
echo We're offering FREE job postings during our launch period.
echo.
echo Visit %VERCEL_URL% to get started today!
echo.
echo Best regards,
echo HireMeBahamas Team
echo support@hiremebahamas.com
) > EMAIL_TEMPLATE.txt

echo.
echo Email template created: EMAIL_TEMPLATE.txt
echo.

echo ============================================
echo   QUICK SHARE OPTIONS
echo ============================================
echo.

echo 1. Copy share message (SHARE_MESSAGE.txt)
echo 2. Open social media posts (SOCIAL_MEDIA_POSTS.txt)
echo 3. Use email template (EMAIL_TEMPLATE.txt)
echo.

echo Opening files...
timeout /t 2 >nul

start SHARE_MESSAGE.txt
start SOCIAL_MEDIA_POSTS.txt

echo.
echo ============================================
echo   FEEDBACK COLLECTION
echo ============================================
echo.

echo Create a Google Form to collect user feedback:
echo 1. Go to: https://forms.google.com
echo 2. Create form with questions:
echo    - How easy was it to use HireMeBahamas?
echo    - What features do you want added?
echo    - Any bugs or issues?
echo    - Would you recommend to others?
echo 3. Share form link with users
echo.

start https://forms.google.com

echo.
pause

echo.
echo ============================================
echo   TRACKING SUCCESS
echo ============================================
echo.

echo Monitor these metrics:
echo.
echo Week 1:  Target 10-20 users
echo Week 2:  Target 50-100 users  
echo Week 3:  Target 200+ users
echo Week 4:  Target 500+ users
echo.
echo Track:
echo ✅ User registrations
echo ✅ Job postings
echo ✅ Applications submitted
echo ✅ User feedback
echo.

echo ============================================
echo   NEXT: BUILD MOBILE APPS
echo ============================================
echo.

echo Once you have:
echo ✅ 100+ active users
echo ✅ Positive feedback
echo ✅ Stable platform
echo.
echo Then start building mobile apps!
echo.
echo See: MOBILE_APP_GUIDE.md (coming soon)
echo.

echo ============================================
echo   CONGRATULATIONS! 🎉
echo ============================================
echo.
echo HireMeBahamas is live and ready for users!
echo.
echo Your site: %VERCEL_URL%
echo.
echo Good luck with your launch! 🇧🇸🚀
echo.
pause
