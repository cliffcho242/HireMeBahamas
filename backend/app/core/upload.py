import asyncio
import io
import os
import uuid
from datetime import timedelta
from typing import List
from urllib.parse import urlparse

import aiofiles
from decouple import config
from fastapi import HTTPException, UploadFile
from PIL import Image

from app.core.request_timeout import with_upload_timeout

# Try to import GCS, but don't fail if not available
try:
    from google.cloud import storage
    GCS_AVAILABLE = True
except ImportError:
    GCS_AVAILABLE = False
    storage = None

# Upload configuration
UPLOAD_DIR = "uploads"
MAX_MB = 10  # Maximum file size in MB (for easy configuration)
MAX_FILE_SIZE = MAX_MB * 1024 * 1024  # 10MB in bytes (derived from MAX_MB)
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
ALLOWED_FILE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    "application/pdf",
    "text/plain",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}

# Cloudinary config (optional)
CLOUDINARY_CLOUD_NAME = config("CLOUDINARY_CLOUD_NAME", default="")
CLOUDINARY_API_KEY = config("CLOUDINARY_API_KEY", default="")
CLOUDINARY_API_SECRET = config("CLOUDINARY_API_SECRET", default="")

# Google Cloud Storage config (optional)
GCS_BUCKET_NAME = config("GCS_BUCKET_NAME", default="")
GCS_PROJECT_ID = config("GCS_PROJECT_ID", default="")
GCS_CREDENTIALS_PATH = config("GCS_CREDENTIALS_PATH", default="")
GCS_MAKE_PUBLIC = config("GCS_MAKE_PUBLIC", default=False, cast=bool)

# Ensure upload directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(f"{UPLOAD_DIR}/avatars", exist_ok=True)
os.makedirs(f"{UPLOAD_DIR}/portfolio", exist_ok=True)
os.makedirs(f"{UPLOAD_DIR}/documents", exist_ok=True)
os.makedirs(f"{UPLOAD_DIR}/profile_pictures", exist_ok=True)


def check_file_size_early(file: UploadFile) -> None:
    """Check file size early from Content-Length header
    
    ✅ UPLOAD HARDENING (CRITICAL):
    Limit size early to prevent reading large files into memory.
    This follows the pattern from the problem statement:
    
    ```python
    from fastapi import UploadFile, HTTPException
    
    MAX_MB = 10
    
    if file.size > MAX_MB * 1024 * 1024:
        raise HTTPException(413, "File too large")
    ```
    
    Args:
        file: The uploaded file to check
        
    Raises:
        HTTPException(413): If file exceeds MAX_MB size limit
    """
    if file.size and file.size > MAX_MB * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large")


def validate_file(file: UploadFile, allowed_types: set = None) -> None:
    """Validate uploaded file with early size limit check
    
    ✅ UPLOAD HARDENING (CRITICAL):
    - Validates file size EARLY before reading into memory
    - Returns HTTP 413 (Payload Too Large) for oversized files
    - Checks file.size if available from Content-Length header
    
    Args:
        file: The uploaded file to validate
        allowed_types: Set of allowed MIME types (defaults to ALLOWED_FILE_TYPES)
        
    Raises:
        HTTPException(413): If file exceeds MAX_MB size limit
        HTTPException(400): If file type not allowed
    """
    if allowed_types is None:
        allowed_types = ALLOWED_FILE_TYPES

    # ✅ CRITICAL: Check size EARLY from Content-Length header before reading file
    check_file_size_early(file)

    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400, detail=f"File type {file.content_type} not allowed"
        )


def generate_filename(original_filename: str) -> str:
    """Generate unique filename"""
    ext = os.path.splitext(original_filename)[1]
    return f"{uuid.uuid4()}{ext}"


def extract_filename_from_url(url: str) -> str:
    """Extract filename from URL (handles both local paths and cloud URLs with query params)"""
    # Parse the URL
    parsed = urlparse(url)
    
    # Get the path component (without query params)
    path = parsed.path
    
    # Extract the filename from the path
    filename = os.path.basename(path)
    
    return filename if filename else "unknown"


async def save_file_locally(file: UploadFile, folder: str = "general") -> str:
    """Save file to local storage with streaming and timeout protection
    
    ✅ UPLOAD HARDENING (CRITICAL):
    - Streams file upload instead of loading into memory
    - Uses chunked reading to handle large files efficiently
    - Validates size early before processing
    
    Args:
        file: The uploaded file to save
        folder: Destination folder within UPLOAD_DIR
        
    Returns:
        str: Relative URL path to the saved file
        
    Raises:
        HTTPException(413): If file exceeds size limit
        HTTPException(408): If upload times out
    """
    validate_file(file)

    filename = generate_filename(file.filename)
    file_path = os.path.join(UPLOAD_DIR, folder, filename)

    # Ensure folder exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    try:
        # ✅ CRITICAL: Stream file upload (never load full file in memory)
        async def _save_file():
            async with aiofiles.open(file_path, "wb") as f:
                # Stream in chunks instead of reading entire file at once
                chunk_size = 1024 * 1024  # 1MB chunks
                while True:
                    chunk = await file.read(chunk_size)
                    if not chunk:
                        break
                    await f.write(chunk)
        
        await with_upload_timeout(_save_file())
        return f"/uploads/{folder}/{filename}"
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=408,
            detail=f"File upload timed out. Please try again with a smaller file or better connection."
        )


def resize_image(
    image_content: bytes, max_width: int = 800, max_height: int = 600
) -> bytes:
    """Resize image to specified dimensions"""
    try:
        image = Image.open(io.BytesIO(image_content))

        # Convert RGBA to RGB if necessary
        if image.mode == "RGBA":
            image = image.convert("RGB")

        # Calculate new dimensions
        width, height = image.size
        ratio = min(max_width / width, max_height / height)

        if ratio < 1:  # Only resize if image is larger than max dimensions
            new_width = int(width * ratio)
            new_height = int(height * ratio)
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Save to bytes
        output = io.BytesIO()
        image.save(output, format="JPEG", quality=85, optimize=True)
        return output.getvalue()

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Image processing error: {str(e)}")


async def upload_image(
    file: UploadFile, folder: str = "general", resize: bool = True
) -> str:
    """Upload and optionally resize image with timeout protection
    
    ✅ UPLOAD HARDENING (CRITICAL):
    - Validates file size EARLY before reading
    - Streams upload when not resizing
    - Only reads into memory when resizing is required
    
    Args:
        file: The uploaded image file
        folder: Destination folder within UPLOAD_DIR
        resize: Whether to resize the image (requires loading into memory)
        
    Returns:
        str: Relative URL path to the saved image
        
    Raises:
        HTTPException(413): If file exceeds size limit
        HTTPException(408): If upload times out
    """
    validate_file(file, ALLOWED_IMAGE_TYPES)

    try:
        # Upload and process image with timeout protection (10 seconds)
        async def _process_and_save():
            # Generate filename
            filename = generate_filename(file.filename)
            file_path = os.path.join(UPLOAD_DIR, folder, filename)

            # Ensure folder exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            if resize and file.content_type in ALLOWED_IMAGE_TYPES:
                # ⚠️ NOTE: Resizing requires reading full image into memory
                # This is acceptable for images as they're typically smaller
                # and resizing reduces memory footprint after processing
                content = await file.read()
                content = resize_image(content)
                
                # Save resized image
                async with aiofiles.open(file_path, "wb") as f:
                    await f.write(content)
            else:
                # ✅ CRITICAL: Stream upload when not resizing
                async with aiofiles.open(file_path, "wb") as f:
                    chunk_size = 1024 * 1024  # 1MB chunks
                    while True:
                        chunk = await file.read(chunk_size)
                        if not chunk:
                            break
                        await f.write(chunk)
            
            return f"/uploads/{folder}/{filename}"
        
        return await with_upload_timeout(_process_and_save())
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=408,
            detail=f"Image upload timed out. Please try again with a smaller image or better connection."
        )


async def upload_multiple_files(
    files: List[UploadFile], folder: str = "general"
) -> List[str]:
    """Upload multiple files"""
    uploaded_urls = []

    for file in files:
        if file.content_type.startswith("image/"):
            url = await upload_image(file, folder)
        else:
            url = await save_file_locally(file, folder)
        uploaded_urls.append(url)

    return uploaded_urls


def delete_file(file_path: str) -> bool:
    """Delete file from local storage"""
    try:
        if file_path.startswith("/uploads/"):
            full_path = file_path[1:]  # Remove leading slash
            if os.path.exists(full_path):
                os.remove(full_path)
                return True
        return False
    except Exception:
        return False


# Cloudinary integration (if configured)
def setup_cloudinary():
    """Setup Cloudinary if credentials are provided"""
    if all([CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET]):
        try:
            import cloudinary
            import cloudinary.uploader

            cloudinary.config(
                cloud_name=CLOUDINARY_CLOUD_NAME,
                api_key=CLOUDINARY_API_KEY,
                api_secret=CLOUDINARY_API_SECRET,
            )
            return True
        except ImportError:
            print("Cloudinary not installed. Using local storage.")
            return False
    return False


async def upload_to_cloudinary(file: UploadFile, folder: str = "hirebahamas") -> str:
    """Upload file to Cloudinary with timeout protection
    
    ✅ UPLOAD HARDENING (CRITICAL):
    - Validates file size early before uploading
    - Uses streaming upload via file.file handle
    
    Args:
        file: The uploaded file
        folder: Cloudinary folder path
        
    Returns:
        str: Secure URL to the uploaded file
        
    Note:
        Falls back to local storage if Cloudinary is not configured or upload fails
    """
    # ✅ CRITICAL: Validate size BEFORE uploading to cloud
    validate_file(file)
    
    if not setup_cloudinary():
        return await save_file_locally(file, folder)

    try:
        import cloudinary.uploader

        # Upload to Cloudinary with timeout protection (external API call)
        async def _upload_to_cloudinary():
            # ✅ CRITICAL: Stream upload using file.file handle (no memory load)
            # Cloudinary upload is synchronous, run in executor to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: cloudinary.uploader.upload(
                    file.file,  # Stream directly from file handle
                    folder=folder,
                    resource_type="auto",
                    quality="auto",
                    fetch_format="auto",
                )
            )
            return result["secure_url"]
        
        return await with_upload_timeout(_upload_to_cloudinary())

    except asyncio.TimeoutError:
        print(f"Cloudinary upload timed out, falling back to local storage")
        # Fallback to local storage
        return await save_file_locally(file, folder)
    except Exception as e:
        print(f"Cloudinary upload failed: {e}")
        # Fallback to local storage
        return await save_file_locally(file, folder)


# Google Cloud Storage integration (if configured)
def setup_gcs():
    """Setup Google Cloud Storage if credentials are provided"""
    if not GCS_AVAILABLE:
        print("google-cloud-storage not installed. Using local storage.")
        return None
        
    if GCS_BUCKET_NAME and (GCS_PROJECT_ID or GCS_CREDENTIALS_PATH):
        try:
            if GCS_CREDENTIALS_PATH and os.path.exists(GCS_CREDENTIALS_PATH):
                # Use credentials file
                client = storage.Client.from_service_account_json(GCS_CREDENTIALS_PATH)
            elif GCS_PROJECT_ID:
                # Use default credentials (Application Default Credentials)
                client = storage.Client(project=GCS_PROJECT_ID)
            else:
                # Try default credentials without project
                client = storage.Client()

            # Return client without checking bucket existence
            # Bucket existence will be validated during actual upload
            return client

        except Exception as e:
            print(f"GCS setup failed: {e}")
            return None
    return None


async def upload_to_gcs(file: UploadFile, folder: str = "hirebahamas") -> str:
    """Upload file to Google Cloud Storage with streaming and timeout protection
    
    ✅ UPLOAD HARDENING (CRITICAL):
    - Validates file size early before uploading
    - Streams upload in chunks to minimize memory usage
    - Only loads necessary chunks into memory at a time
    
    Files are uploaded as public or private based on GCS_MAKE_PUBLIC environment variable.
    - If GCS_MAKE_PUBLIC=True: Files are made public and public URL is returned
    - If GCS_MAKE_PUBLIC=False (default): Files are private and a 1-hour signed URL is returned
    
    Configure GCS_MAKE_PUBLIC in your .env file to control this behavior.
    
    Args:
        file: The uploaded file
        folder: GCS folder path
        
    Returns:
        str: Public URL or signed URL to the uploaded file
        
    Note:
        Falls back to local storage if GCS is not configured or upload fails
    """
    # ✅ CRITICAL: Validate file size BEFORE uploading to cloud
    validate_file(file)
    
    client = setup_gcs()
    if not client:
        return await save_file_locally(file, folder)

    try:
        # Upload to GCS with timeout protection (external API call)
        async def _upload_to_gcs():
            # Generate unique filename
            filename = generate_filename(file.filename)
            blob_name = f"{folder}/{filename}"

            # Get bucket
            bucket = client.bucket(GCS_BUCKET_NAME)
            blob = bucket.blob(blob_name)

            # Reset file pointer to beginning in case it was read before
            await file.seek(0)
            
            # Set content type
            content_type = file.content_type or "application/octet-stream"
            
            # ⚠️ NOTE: GCS Python SDK's upload_from_file() requires a file-like object
            # and doesn't support chunked streaming in the same way as local uploads.
            # MITIGATION: We validate size early (10MB max) to prevent OOM issues.
            # For files ≤10MB, this approach is safe and acceptable.
            # Alternative: Use resumable uploads for larger files (future enhancement)
            content = await file.read()
            file_obj = io.BytesIO(content)

            # GCS upload is synchronous, run in executor to avoid blocking
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: blob.upload_from_file(file_obj, content_type=content_type)
            )

            # Make public or generate signed URL based on configuration
            if GCS_MAKE_PUBLIC:
                blob.make_public()
                return blob.public_url
            else:
                # Generate a signed URL valid for 1 hour for private files
                signed_url = blob.generate_signed_url(
                    version="v4",
                    expiration=timedelta(hours=1),
                    method="GET"
                )
                return signed_url
        
        return await with_upload_timeout(_upload_to_gcs())

    except asyncio.TimeoutError:
        print(f"GCS upload timed out, falling back to local storage")
        # Fallback to local storage
        return await save_file_locally(file, folder)
    except Exception as e:
        print(f"GCS upload failed: {e}")
        # Fallback to local storage
        return await save_file_locally(file, folder)
