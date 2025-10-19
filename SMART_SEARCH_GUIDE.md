# 🔍 Smart Search Algorithm - User Guide

## ✨ Welcome to Intelligent Job Search!

HireBahamas now features an **AI-powered smart search** that makes finding the right jobs, services, and professionals incredibly easy!

---

## 🎯 How It Works

### **Example: Finding a Plumber**

Simply type **"plumber"** in the search bar and watch the magic happen:

1. **🤖 Smart Detection**: Automatically detects you're looking for "Trades & Construction"
2. **📍 Location Awareness**: Type "plumber in Nassau" to auto-filter by location
3. **🎯 Relevance Scoring**: Shows best matches first (90%+ match score)
4. **💡 Suggestions**: Get instant autocomplete suggestions as you type
5. **🔥 Popular Searches**: Quick access to common searches like Electrician, Chef, etc.

---

## 🚀 Features

### **1. Fuzzy Matching**
- Handles typos: "plubmer" → finds "plumber"
- Similar terms: "chef" = "cook" = "culinary"
- Partial matches: "elec" suggests "electrician"

### **2. Category Detection**
Our algorithm automatically detects these categories:

| Category | Examples |
|----------|----------|
| 🔧 **Trades & Construction** | plumber, electrician, carpenter, mason, welder |
| 🏥 **Healthcare** | doctor, nurse, dentist, therapist, caregiver |
| 🏨 **Hospitality & Tourism** | hotel, chef, waiter, bartender, tour guide |
| 💼 **Professional Services** | lawyer, accountant, consultant, manager |
| 💻 **Technology** | developer, programmer, IT, designer |
| 📚 **Education** | teacher, tutor, instructor, coach |
| 🚗 **Transportation** | driver, taxi, delivery, courier |
| 🏠 **Home Services** | cleaning, gardener, security, pest control |
| 💇 **Beauty & Wellness** | salon, barber, spa, massage, stylist |
| 🛍️ **Retail & Sales** | sales, cashier, store, merchant |

### **3. Smart Suggestions**
As you type, you get:
- **Autocomplete**: "plu..." → "plumber", "plumbing"
- **Related searches**: Similar jobs in same category
- **Location combos**: "plumber in Nassau", "jobs in Freeport"

### **4. Relevance Scoring**
Each job gets a match score:
- **100%** = Perfect match (exact title)
- **80-99%** = Strong match (title/category)
- **60-79%** = Good match (description/skills)
- **40-59%** = Fair match (company/location)

Jobs below 30% match are filtered out automatically.

### **5. Recent Searches**
Your last 5 searches are saved for quick access.

### **6. Popular Searches**
One-click access to:
- 🔧 Plumber
- ⚡ Electrician
- 👨‍🍳 Chef
- 🏨 Hotel Jobs
- 👨‍⚕️ Nurse
- 🚗 Driver
- 👨‍🏫 Teacher
- 💼 Accountant
- 💻 Developer
- 🪚 Carpenter

---

## 💡 Search Examples

### **Basic Search**
```
"plumber"
```
✅ Finds all plumbing jobs
✅ Shows relevance score
✅ Detects "Trades & Construction" category

### **Location-Specific**
```
"plumber in Nassau"
```
✅ Auto-filters to Nassau location
✅ Shows only local results
✅ Highlights location in results

### **Category + Location**
```
"chef in Freeport"
```
✅ Detects "Hospitality & Tourism"
✅ Filters to Freeport
✅ Shows hotel/restaurant jobs

### **Skill-Based**
```
"web developer"
```
✅ Detects "Technology" category
✅ Matches "developer", "programmer", "software engineer"
✅ Shows skill requirements

### **Service Search**
```
"repair services"
```
✅ Matches multiple categories
✅ Shows plumbers, electricians, mechanics
✅ Sorted by relevance

---

## 🎨 Visual Indicators

### **Match Score Badge**
Green badge shows relevance:
- 🟢 **90-100%** = Excellent match
- 🟡 **70-89%** = Good match
- 🟠 **50-69%** = Fair match

### **Matched Fields Tag**
Blue tag shows what matched:
- `title` = Job title match
- `category` = Category match
- `description` = Found in description
- `skills` = Skills match
- `company` = Company name match

---

## 📱 Mobile Features

### **Touch-Optimized**
- Large search bar
- Easy-to-tap suggestions
- Swipe to dismiss

### **Quick Filters**
Bottom sheet with:
- Popular searches
- Recent searches
- Location filters
- Category buttons

---

## 🔧 Advanced Tips

### **1. Use Natural Language**
❌ Don't type: "job+electrician+nassau"
✅ Do type: "electrician in Nassau"

### **2. Try Variations**
If "chef" doesn't work, try:
- "cook"
- "culinary"
- "kitchen staff"

### **3. Combine Terms**
- "hotel chef Nassau" = All three filters
- "remote developer" = Remote jobs only
- "part time teacher" = Part-time education jobs

### **4. Use Locations**
Supported locations:
- Nassau
- Freeport
- Grand Bahama
- Paradise Island
- Abaco
- Eleuthera
- Exuma
- Andros
- Bimini
- Long Island

### **5. Check Synonyms**
The algorithm knows:
- plumber = plumbing = pipe fitter
- electrician = electrical = wiring
- carpenter = woodworker = joiner
- chef = cook = culinary
- developer = programmer = coder
- driver = chauffeur = operator

---

## 🎯 Best Practices

### **For Job Seekers**
1. Start with general terms: "plumber"
2. Add location if needed: "plumber Nassau"
3. Check match scores for best fits
4. Click suggestions for related searches
5. Save searches you use often

### **For Employers**
1. Use clear job titles: "Plumber - Commercial"
2. Include skills in description
3. Tag location accurately
4. Choose correct category
5. Add relevant keywords

---

## 📊 Search Algorithm Details

### **Scoring System**
```
Title match:       40 points (highest weight)
Category match:    25 points
Description match: 15 points  
Company match:     10 points
Skills match:       5 points per skill
Location match:    10 points (bonus)
-------------------
Total:            100 points max
```

### **Similarity Calculation**
Uses **Levenshtein distance**:
- Exact match = 1.0 (100%)
- Contains match = 0.8 (80%)
- Similar spelling = 0.5-0.7 (50-70%)
- Different = < 0.5 (filtered out)

---

## 🆘 Troubleshooting

### **No Results Found?**
1. Check spelling
2. Try simpler search: "chef" instead of "head chef with 5 years"
3. Remove location filter
4. Click "Clear search" button
5. Try popular searches

### **Too Many Results?**
1. Add location: "plumber in Nassau"
2. Be more specific: "residential plumber"
3. Use filters: Category, Location dropdowns
4. Sort by relevance (default)

### **Wrong Category Detected?**
1. Be more specific in search
2. Use exact job title
3. Manually select category filter
4. Add more context words

---

## 🎉 Examples of Great Searches

### **Finding Trades People**
✅ "plumber Nassau commercial"
✅ "electrician residential Freeport"
✅ "carpenter experienced"
✅ "mason block work"

### **Finding Hospitality Workers**
✅ "chef fine dining"
✅ "hotel manager Paradise Island"
✅ "bartender resort"
✅ "tour guide Exuma"

### **Finding Professionals**
✅ "accountant CPA"
✅ "lawyer corporate Nassau"
✅ "developer full stack"
✅ "teacher high school"

### **Finding Services**
✅ "cleaning service"
✅ "gardening landscaping"
✅ "security guard"
✅ "delivery driver"

---

## 🌟 Pro Tips

1. **Save Time**: Use recent searches for frequent queries
2. **Explore**: Click suggested categories to discover related jobs
3. **Be Flexible**: Try different search terms if first attempt fails
4. **Check Badges**: High match scores (90%+) = best fits
5. **Mobile**: Pull down to refresh, swipe for suggestions

---

## 📞 Need Help?

If you're having trouble finding what you're looking for:

1. Check this guide's examples
2. Use popular searches as templates
3. Start simple, add details later
4. Try synonyms and related terms
5. Contact support if issues persist

---

## 🎯 Quick Reference Card

```
┌─────────────────────────────────────────┐
│  QUICK SEARCH TIPS                      │
├─────────────────────────────────────────┤
│  ✓ Type naturally: "plumber in Nassau" │
│  ✓ Use suggestions: Click autocomplete │
│  ✓ Check badges: Match score & fields  │
│  ✓ Try variations: chef = cook         │
│  ✓ Add location: "...in [city]"        │
│  ✓ Recent: Your last 5 searches saved  │
│  ✓ Popular: One-click common searches  │
└─────────────────────────────────────────┘
```

---

**🎉 Happy Job Hunting!**

The smarter you search, the faster you find!

---

*Created: October 2025*  
*Platform: HireBahamas*  
*Feature: Smart Search v1.0*
