import os
from typing import List

from app.api.auth import get_current_user
from app.core.upload import ALLOWED_IMAGE_TYPES, delete_file, upload_image
from app.database import get_db
from app.models import ProfilePicture, User
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.post("/upload")
async def upload_profile_picture(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload a new profile picture to the gallery"""
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400, detail="Only image files are allowed"
        )

    try:
        # ✅ UPLOAD HARDENING: Get file size from Content-Length header if available
        # This avoids reading the entire file into memory just to get size
        file_size = file.size if file.size else 0
        
        # Upload image (will validate size early and stream upload)
        file_url = await upload_image(file, folder="profile_pictures", resize=True)

        # Check if this is the user's first profile picture
        result = await db.execute(
            select(ProfilePicture).where(ProfilePicture.user_id == current_user.id)
        )
        existing_pictures = result.scalars().all()
        is_first = len(existing_pictures) == 0

        # Create profile picture record
        profile_picture = ProfilePicture(
            user_id=current_user.id,
            file_url=file_url,
            filename=os.path.basename(file_url),
            file_size=file_size,
            is_current=is_first,  # Set as current if it's the first picture
        )
        db.add(profile_picture)

        # If this is the first picture, also update user's avatar_url
        if is_first:
            current_user.avatar_url = file_url

        await db.commit()
        await db.refresh(profile_picture)

        return {
            "success": True,
            "message": "Profile picture uploaded successfully",
            "picture": {
                "id": profile_picture.id,
                "file_url": profile_picture.file_url,
                "filename": profile_picture.filename,
                "file_size": profile_picture.file_size,
                "is_current": profile_picture.is_current,
                "created_at": profile_picture.created_at.isoformat() if profile_picture.created_at else None,
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/upload-multiple")
async def upload_multiple_profile_pictures(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload multiple profile pictures at once"""
    if len(files) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 files allowed at once")

    # Validate all files are images
    for file in files:
        if file.content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=400, detail=f"File {file.filename} is not an image"
            )

    try:
        # Check if user has any existing pictures
        result = await db.execute(
            select(ProfilePicture).where(ProfilePicture.user_id == current_user.id)
        )
        existing_pictures = result.scalars().all()
        has_existing = len(existing_pictures) > 0

        uploaded_pictures = []

        for idx, file in enumerate(files):
            # ✅ UPLOAD HARDENING: Get file size from Content-Length header if available
            # This avoids reading the entire file into memory just to get size
            file_size = file.size if file.size else 0
            
            # Upload image (will validate size early and stream upload)
            file_url = await upload_image(file, folder="profile_pictures", resize=True)

            # Set first picture as current if no existing pictures
            is_current = (not has_existing and idx == 0)

            # Create profile picture record
            profile_picture = ProfilePicture(
                user_id=current_user.id,
                file_url=file_url,
                filename=os.path.basename(file_url),
                file_size=file_size,
                is_current=is_current,
            )
            db.add(profile_picture)
            
            uploaded_pictures.append(profile_picture)

            # If this is the first picture, update user's avatar_url
            if is_current:
                current_user.avatar_url = file_url

        await db.commit()

        # Refresh all uploaded pictures
        for picture in uploaded_pictures:
            await db.refresh(picture)

        return {
            "success": True,
            "message": f"{len(uploaded_pictures)} profile pictures uploaded successfully",
            "pictures": [
                {
                    "id": picture.id,
                    "file_url": picture.file_url,
                    "filename": picture.filename,
                    "file_size": picture.file_size,
                    "is_current": picture.is_current,
                    "created_at": picture.created_at.isoformat() if picture.created_at else None,
                }
                for picture in uploaded_pictures
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/list")
async def get_profile_pictures(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all profile pictures for the current user"""
    result = await db.execute(
        select(ProfilePicture)
        .where(ProfilePicture.user_id == current_user.id)
        .order_by(ProfilePicture.created_at.desc())
    )
    pictures = result.scalars().all()

    return {
        "success": True,
        "pictures": [
            {
                "id": picture.id,
                "file_url": picture.file_url,
                "filename": picture.filename,
                "file_size": picture.file_size,
                "is_current": picture.is_current,
                "created_at": picture.created_at.isoformat() if picture.created_at else None,
            }
            for picture in pictures
        ],
        "total": len(pictures),
    }


@router.post("/{picture_id}/set-current")
async def set_current_profile_picture(
    picture_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Set a specific profile picture as the current one"""
    # Get the picture
    result = await db.execute(
        select(ProfilePicture).where(
            and_(
                ProfilePicture.id == picture_id,
                ProfilePicture.user_id == current_user.id
            )
        )
    )
    picture = result.scalar_one_or_none()

    if not picture:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile picture not found"
        )

    # Unset all other pictures as current
    all_pictures_result = await db.execute(
        select(ProfilePicture).where(ProfilePicture.user_id == current_user.id)
    )
    all_pictures = all_pictures_result.scalars().all()
    
    for p in all_pictures:
        p.is_current = (p.id == picture_id)

    # Update user's avatar_url
    current_user.avatar_url = picture.file_url

    await db.commit()

    return {
        "success": True,
        "message": "Profile picture set as current",
        "picture": {
            "id": picture.id,
            "file_url": picture.file_url,
            "is_current": True,
        }
    }


@router.delete("/{picture_id}")
async def delete_profile_picture(
    picture_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a profile picture"""
    # Get the picture
    result = await db.execute(
        select(ProfilePicture).where(
            and_(
                ProfilePicture.id == picture_id,
                ProfilePicture.user_id == current_user.id
            )
        )
    )
    picture = result.scalar_one_or_none()

    if not picture:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile picture not found"
        )

    was_current = picture.is_current
    file_url = picture.file_url

    # Delete the database record
    await db.delete(picture)
    await db.commit()

    # Delete the physical file
    delete_file(file_url)

    # If this was the current picture, set another as current
    if was_current:
        result = await db.execute(
            select(ProfilePicture)
            .where(ProfilePicture.user_id == current_user.id)
            .order_by(ProfilePicture.created_at.desc())
            .limit(1)
        )
        new_current = result.scalar_one_or_none()
        
        if new_current:
            new_current.is_current = True
            current_user.avatar_url = new_current.file_url
            await db.commit()
        else:
            # No more pictures, clear avatar_url
            current_user.avatar_url = None
            await db.commit()

    return {
        "success": True,
        "message": "Profile picture deleted successfully"
    }
