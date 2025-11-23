# Profile Picture Gallery Feature

## Overview
This feature allows users to upload multiple profile pictures, manage a gallery of pictures, and select which one to use as their current active profile picture.

## System Requirements

### Backend Dependencies (Already Installed)
```bash
# System packages (Ubuntu/Debian)
sudo apt-get install -y libpng-dev libjpeg-dev libwebp-dev zlib1g-dev

# Python packages
pip install Pillow aiofiles fastapi uvicorn python-jose passlib python-multipart
```

### Database Setup
Run the migration script to create the profile_pictures table:
```bash
python3 create_profile_pictures_table.py
```

Expected output:
```
Creating profile_pictures table...
✅ Profile pictures table created successfully!
```

## Features

### 1. Upload Profile Pictures
- **Single Upload**: Upload one picture at a time
- **Multiple Upload**: Upload up to 10 pictures at once
- **Supported Formats**: JPEG, PNG, GIF, WebP
- **Maximum File Size**: 10MB per image
- **Auto-resize**: Images are automatically resized to optimize storage

### 2. Gallery Management
- View all uploaded profile pictures in a grid layout
- Each picture shows:
  - Thumbnail preview
  - File name
  - File size
  - Current status indicator

### 3. Set Active Profile Picture
- Click the checkmark icon on any picture to set it as your current profile picture
- The active picture is used across the platform:
  - User profile page
  - Posts and comments
  - Messages
  - Notifications

### 4. Delete Pictures
- Remove unwanted pictures from your gallery
- If you delete the current profile picture, the most recent remaining picture becomes the new current picture
- Deletes both the database record and the physical file

## API Endpoints

### Upload Single Picture
```http
POST /api/profile-pictures/upload
Content-Type: multipart/form-data
Authorization: Bearer <token>

Body:
  file: <image file>
```

**Response:**
```json
{
  "success": true,
  "message": "Profile picture uploaded successfully",
  "picture": {
    "id": 1,
    "file_url": "/uploads/profile_pictures/abc123.jpg",
    "filename": "abc123.jpg",
    "file_size": 102400,
    "is_current": true,
    "created_at": "2024-11-23T12:00:00"
  }
}
```

### Upload Multiple Pictures
```http
POST /api/profile-pictures/upload-multiple
Content-Type: multipart/form-data
Authorization: Bearer <token>

Body:
  files: [<image file 1>, <image file 2>, ...]
```

**Response:**
```json
{
  "success": true,
  "message": "3 profile pictures uploaded successfully",
  "pictures": [...]
}
```

### List All Pictures
```http
GET /api/profile-pictures/list
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "pictures": [...],
  "total": 5
}
```

### Set Current Picture
```http
POST /api/profile-pictures/{picture_id}/set-current
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "message": "Profile picture set as current",
  "picture": {
    "id": 2,
    "file_url": "/uploads/profile_pictures/def456.jpg",
    "is_current": true
  }
}
```

### Delete Picture
```http
DELETE /api/profile-pictures/{picture_id}
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "message": "Profile picture deleted successfully"
}
```

## Frontend Usage

### Using the ProfilePictureGallery Component

The component is automatically included in the Profile page. To use it elsewhere:

```tsx
import ProfilePictureGallery from '../components/ProfilePictureGallery';

function MyComponent() {
  return (
    <div>
      <ProfilePictureGallery />
    </div>
  );
}
```

### Using the API Service

```typescript
import { profilePicturesAPI } from '../services/api';

// Upload a single picture
const uploadSingle = async (file: File) => {
  const response = await profilePicturesAPI.uploadPicture(file);
  console.log(response);
};

// Upload multiple pictures
const uploadMultiple = async (files: File[]) => {
  const response = await profilePicturesAPI.uploadMultiplePictures(files);
  console.log(response);
};

// Get all pictures
const getPictures = async () => {
  const response = await profilePicturesAPI.listPictures();
  console.log(response.pictures);
};

// Set current picture
const setCurrent = async (pictureId: number) => {
  const response = await profilePicturesAPI.setCurrentPicture(pictureId);
  console.log(response);
};

// Delete picture
const deletePicture = async (pictureId: number) => {
  const response = await profilePicturesAPI.deletePicture(pictureId);
  console.log(response);
};
```

## Database Schema

### profile_pictures table
```sql
CREATE TABLE profile_pictures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    file_url VARCHAR(500) NOT NULL,
    filename VARCHAR(255) NOT NULL,
    file_size INTEGER NOT NULL,
    is_current BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

## File Storage

Pictures are stored in:
```
uploads/profile_pictures/
```

Each file is renamed with a UUID to prevent conflicts:
```
original_name.jpg -> a1b2c3d4-e5f6-7890-abcd-ef1234567890.jpg
```

## Security Considerations

1. **Authentication Required**: All endpoints require a valid JWT token
2. **File Type Validation**: Only image files are accepted
3. **File Size Limit**: Maximum 10MB per file
4. **User Isolation**: Users can only manage their own pictures
5. **Automatic Cleanup**: Physical files are deleted when picture is removed from gallery
6. **No CodeQL Vulnerabilities**: Security scan passed with 0 alerts

## Error Handling

### Common Errors

**400 Bad Request**
- Invalid file type (not an image)
- File too large (> 10MB)
- Too many files (> 10 in multiple upload)

**401 Unauthorized**
- Missing or invalid JWT token

**404 Not Found**
- Picture ID not found
- Picture doesn't belong to current user

**500 Internal Server Error**
- File upload failed
- Database error

## Performance Considerations

1. **Image Resizing**: Images are automatically resized to reduce storage space
2. **Lazy Loading**: Gallery images use lazy loading for better performance
3. **Optimized Queries**: Database queries are optimized with proper indexes
4. **Single File Read**: File content is read only once during upload process

## Testing

### Manual Testing
1. Navigate to your Profile page
2. Click "Add Pictures" button
3. Select one or multiple images
4. Verify upload success message
5. Hover over pictures to see action buttons
6. Click checkmark to set as current
7. Click trash icon to delete

### Expected Behavior
- First uploaded picture automatically becomes current
- User's avatar_url is updated when setting current picture
- Deleting current picture auto-selects next most recent picture
- Empty state shows when no pictures exist

## Troubleshooting

### Images not uploading
- Check file size (must be < 10MB)
- Verify file type is image (JPEG, PNG, GIF, WebP)
- Check backend logs for errors
- Ensure uploads directory has write permissions

### Gallery not displaying
- Check browser console for errors
- Verify API token is valid
- Check network tab for failed API calls
- Ensure backend server is running

### Pictures not displaying correctly
- Verify file_url paths are correct
- Check that files exist in uploads/profile_pictures/
- Ensure web server can serve static files from uploads directory

## Future Enhancements

Potential improvements for future versions:
- [ ] Crop and edit pictures before upload
- [ ] Reorder pictures in gallery
- [ ] Add captions to pictures
- [ ] Share pictures with specific users
- [ ] Set different pictures for different contexts (profile vs posts)
- [ ] Integration with cloud storage (Cloudinary, AWS S3)
- [ ] Bulk delete functionality
- [ ] Picture approval workflow for moderated platforms
