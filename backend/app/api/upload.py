import os
from typing import List, Optional

from app.core.security import get_current_user
from app.core.upload import (
    ALLOWED_IMAGE_TYPES,
    delete_file,
    save_file_locally,
    upload_image,
    upload_multiple_files,
    upload_to_cloudinary,
    upload_to_gcs,
)
from app.database import get_db
from app.models import UploadedFile, User
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.post("/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload user avatar"""
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400, detail="Only image files are allowed for avatars"
        )

    try:
        # Delete old avatar if exists
        if current_user.profile_image:
            delete_file(current_user.profile_image)

        # Upload new avatar
        file_url = await upload_image(file, folder="avatars", resize=True)

        # Update user profile
        current_user.profile_image = file_url
        await db.commit()

        return {"message": "Avatar uploaded successfully", "file_url": file_url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/portfolio")
async def upload_portfolio_images(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload portfolio images"""
    if len(files) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 files allowed")

    # Validate all files are images
    for file in files:
        if file.content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=400, detail=f"File {file.filename} is not an image"
            )

    try:
        # Upload files
        uploaded_urls = await upload_multiple_files(files, folder="portfolio")

        # Update user portfolio images
        existing_portfolio = current_user.portfolio_images or []
        new_portfolio = existing_portfolio + uploaded_urls

        # Limit to 20 total portfolio images
        if len(new_portfolio) > 20:
            new_portfolio = new_portfolio[-20:]

        current_user.portfolio_images = new_portfolio
        await db.commit()

        # Save file records
        for i, url in enumerate(uploaded_urls):
            file_record = UploadedFile(
                filename=os.path.basename(url),
                original_filename=files[i].filename,
                file_path=url,
                file_size=files[i].size or 0,
                content_type=files[i].content_type,
                user_id=current_user.id,
            )
            db.add(file_record)

        await db.commit()

        return {
            "message": f"{len(uploaded_urls)} files uploaded successfully",
            "uploaded_files": uploaded_urls,
            "total_portfolio_images": len(new_portfolio),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.delete("/portfolio")
async def delete_portfolio_image(
    file_url: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a portfolio image"""
    if (
        not current_user.portfolio_images
        or file_url not in current_user.portfolio_images
    ):
        raise HTTPException(status_code=404, detail="Portfolio image not found")

    try:
        # Remove from user's portfolio
        portfolio_images = current_user.portfolio_images.copy()
        portfolio_images.remove(file_url)
        current_user.portfolio_images = portfolio_images

        # Delete physical file
        delete_file(file_url)

        # Delete file record
        result = await db.execute(
            select(UploadedFile).where(
                UploadedFile.file_path == file_url,
                UploadedFile.user_id == current_user.id,
            )
        )
        file_record = result.scalar_one_or_none()
        if file_record:
            await db.delete(file_record)

        await db.commit()

        return {
            "message": "Portfolio image deleted successfully",
            "remaining_images": len(portfolio_images),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")


@router.post("/document")
async def upload_document(
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload a document (resume, portfolio, etc.)
    
    This endpoint uses Cloudinary for cloud storage if configured.
    For Google Cloud Storage, use the /document-gcs endpoint instead.
    Falls back to local storage if no cloud provider is configured.
    """
    try:
        # Use Cloudinary for documents if available, otherwise local storage
        file_url = await upload_to_cloudinary(file, folder="documents")

        # Save file record
        file_record = UploadedFile(
            filename=os.path.basename(file_url),
            original_filename=file.filename,
            file_path=file_url,
            file_size=file.size or 0,
            content_type=file.content_type,
            user_id=current_user.id,
        )
        db.add(file_record)
        await db.commit()
        await db.refresh(file_record)

        return {
            "message": "Document uploaded successfully",
            "file_id": str(file_record.id),
            "file_url": file_url,
            "original_filename": file.filename,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/document-gcs")
async def upload_document_to_gcs(
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload a document to Google Cloud Storage
    Uses GCS for cloud storage if configured, otherwise uses local storage.
    """
    try:
        # Use Google Cloud Storage for documents if available, otherwise local storage
        file_url = await upload_to_gcs(file, folder="documents")

        # Save file record
        file_record = UploadedFile(
            filename=os.path.basename(file_url),
            original_filename=file.filename,
            file_path=file_url,
            file_size=file.size or 0,
            content_type=file.content_type,
            user_id=current_user.id,
        )
        db.add(file_record)
        await db.commit()
        await db.refresh(file_record)

        return {
            "message": "Document uploaded successfully to GCS",
            "file_id": str(file_record.id),
            "file_url": file_url,
            "original_filename": file.filename,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/my-files")
async def get_my_files(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """Get all uploaded files for current user"""
    result = await db.execute(
        select(UploadedFile)
        .where(UploadedFile.user_id == current_user.id)
        .order_by(UploadedFile.created_at.desc())
    )

    files = result.scalars().all()

    return {
        "files": [
            {
                "id": str(file.id),
                "filename": file.filename,
                "original_filename": file.original_filename,
                "file_url": file.file_path,
                "file_size": file.file_size,
                "content_type": file.content_type,
                "created_at": file.created_at,
            }
            for file in files
        ],
        "total_files": len(files),
    }


@router.delete("/file/{file_id}")
async def delete_uploaded_file(
    file_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete an uploaded file"""
    result = await db.execute(
        select(UploadedFile).where(
            UploadedFile.id == file_id, UploadedFile.user_id == current_user.id
        )
    )

    file_record = result.scalar_one_or_none()
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")

    try:
        # Delete physical file
        delete_file(file_record.file_path)

        # Delete database record
        await db.delete(file_record)
        await db.commit()

        return {"message": "File deleted successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")
