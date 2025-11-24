# UserProfile Page Components and Dependencies

This document outlines the components and dependencies required for the UserProfile page to function correctly.

## Overview

The UserProfile page (`src/pages/UserProfile.tsx`) is a fully-featured user profile viewing page that displays user information, posts, and provides interaction capabilities like following/unfollowing and messaging.

## Required Dependencies

The following dependencies are essential for the UserProfile page to work correctly:

### 1. **framer-motion** (^12.23.24)
- **Purpose**: Provides smooth animations and transitions for the page
- **Used for**: 
  - Page transition animations
  - Card entrance animations
  - Smooth fade-in effects

### 2. **@heroicons/react** (^2.2.0)
- **Purpose**: Provides beautiful, consistent icons throughout the UI
- **Used for**:
  - User profile icons (UserCircleIcon)
  - Location icons (MapPinIcon)
  - Job/occupation icons (BriefcaseIcon, BuildingOfficeIcon)
  - Contact icons (EnvelopeIcon, PhoneIcon)
  - Action icons (ChatBubbleLeftIcon, ArrowLeftIcon, UserPlusIcon, UserMinusIcon)
  - Date icons (CalendarIcon)

### 3. **react-hot-toast** (^2.6.0)
- **Purpose**: Displays elegant toast notifications for user feedback
- **Used for**:
  - Success messages (follow/unfollow actions)
  - Error messages (API failures)
  - Info messages (navigation events)

### 4. **react-router-dom** (^7.9.4)
- **Purpose**: Handles routing and navigation
- **Used for**:
  - URL parameter extraction (userId)
  - Navigation between pages
  - Back button functionality

### 5. **react** & **react-dom** (^18.2.0)
- **Purpose**: Core React library
- **Used for**: Component rendering and state management

## Visual Theme Components

The UserProfile page uses a consistent visual theme powered by:

1. **Tailwind CSS**: Utility-first CSS framework for styling
2. **Gradient Backgrounds**: Blue to purple gradients for headers
3. **Card-based Layout**: White cards with shadows for content sections
4. **Responsive Design**: Mobile-first responsive layouts
5. **Animation**: Smooth transitions and hover effects

## Key Features

### Profile Header
- Avatar with gradient background
- User name and username
- Occupation and company information
- Location display
- Action buttons (Follow/Unfollow, Message)

### Statistics Section
- Post count
- Followers count
- Following count
- Availability status badge

### Tabbed Content
- **Posts Tab**: Displays user's posts with images and engagement metrics
- **About Tab**: Shows detailed user information including bio and contact details

### Error Handling
- Graceful 404 handling with auto-redirect
- User-friendly error messages
- Loading states with spinners

## Verification

To verify that all required dependencies are properly installed, run:

```bash
npm run verify:user-page
```

This will check:
- ✅ All dependencies are in package.json
- ✅ All packages are installed in node_modules
- ✅ UserProfile.tsx exists and has correct imports
- ✅ Build can complete successfully

## Troubleshooting

If you encounter issues with the UserProfile page:

1. **Missing Dependencies**: Run `npm install` to ensure all packages are installed
2. **Build Errors**: Run `npm run build` to check for TypeScript or build errors
3. **Import Errors**: Verify all imports at the top of UserProfile.tsx are correct
4. **Styling Issues**: Ensure Tailwind CSS is properly configured in `tailwind.config.js`

## Related Files

- `/src/pages/UserProfile.tsx` - Main component file
- `/src/services/api.ts` - API service for user data
- `/src/contexts/AuthContext.tsx` - Authentication context
- `/tailwind.config.js` - Tailwind configuration
- `/src/index.css` - Global styles

## Development

When making changes to the UserProfile page:

1. Always test with `npm run build` before committing
2. Run `npm run lint` to check for code style issues
3. Verify dependencies with `npm run verify:user-page`
4. Test on multiple screen sizes for responsive design

## Support

For issues related to the UserProfile page, check:
- The verification script: `npm run verify:user-page`
- Build logs: `npm run build`
- TypeScript errors: `npx tsc --noEmit`
