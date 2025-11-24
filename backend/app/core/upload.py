import io
import os
import uuid
from typing import List

import aiofiles
from decouple import config
from fastapi import HTTPException, UploadFile
from PIL import Image

# Upload configuration
UPLOAD_DIR = "uploads"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
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

# Ensure upload directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(f"{UPLOAD_DIR}/avatars", exist_ok=True)
os.makedirs(f"{UPLOAD_DIR}/portfolio", exist_ok=True)
os.makedirs(f"{UPLOAD_DIR}/documents", exist_ok=True)


def validate_file(file: UploadFile, allowed_types: set = None) -> None:
    """Validate uploaded file"""
    if allowed_types is None:
        allowed_types = ALLOWED_FILE_TYPES

    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400, detail=f"File type {file.content_type} not allowed"
        )

    if file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB",
        )


def generate_filename(original_filename: str) -> str:
    """Generate unique filename"""
    ext = os.path.splitext(original_filename)[1]
    return f"{uuid.uuid4()}{ext}"


async def save_file_locally(file: UploadFile, folder: str = "general") -> str:
    """Save file to local storage"""
    validate_file(file)

    filename = generate_filename(file.filename)
    file_path = os.path.join(UPLOAD_DIR, folder, filename)

    # Ensure folder exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Save file
    async with aiofiles.open(file_path, "wb") as f:
        content = await file.read()
        await f.write(content)

    return f"/uploads/{folder}/{filename}"


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
    """Upload and optionally resize image"""
    validate_file(file, ALLOWED_IMAGE_TYPES)

    # Read file content
    content = await file.read()

    # Resize if requested
    if resize and file.content_type in ALLOWED_IMAGE_TYPES:
        content = resize_image(content)

    # Generate filename
    filename = generate_filename(file.filename)
    file_path = os.path.join(UPLOAD_DIR, folder, filename)

    # Ensure folder exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Save file
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    return f"/uploads/{folder}/{filename}"


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
    """Upload file to Cloudinary"""
    if not setup_cloudinary():
        return await save_file_locally(file, folder)

    try:
        import cloudinary.uploader

        # Upload to Cloudinary
        result = cloudinary.uploader.upload(
            file.file,
            folder=folder,
            resource_type="auto",
            quality="auto",
            fetch_format="auto",
        )

        return result["secure_url"]

    except Exception as e:
        print(f"Cloudinary upload failed: {e}")
        # Fallback to local storage
        return await save_file_locally(file, folder)


# Google Cloud Storage integration (if configured)
def setup_gcs():
    """Setup Google Cloud Storage if credentials are provided"""
    if GCS_BUCKET_NAME and (GCS_PROJECT_ID or GCS_CREDENTIALS_PATH):
        try:
            from google.cloud import storage

            if GCS_CREDENTIALS_PATH and os.path.exists(GCS_CREDENTIALS_PATH):
                # Use credentials file
                client = storage.Client.from_service_account_json(GCS_CREDENTIALS_PATH)
            elif GCS_PROJECT_ID:
                # Use default credentials (Application Default Credentials)
                client = storage.Client(project=GCS_PROJECT_ID)
            else:
                # Try default credentials without project
                client = storage.Client()

            # Verify bucket exists
            bucket = client.bucket(GCS_BUCKET_NAME)
            if bucket.exists():
                return client
            else:
                print(f"GCS bucket '{GCS_BUCKET_NAME}' does not exist.")
                return None

        except ImportError:
            print("google-cloud-storage not installed. Using local storage.")
            return None
        except Exception as e:
            print(f"GCS setup failed: {e}")
            return None
    return None


async def upload_to_gcs(file: UploadFile, folder: str = "hirebahamas") -> str:
    """Upload file to Google Cloud Storage"""
    client = setup_gcs()
    if not client:
        return await save_file_locally(file, folder)

    try:
        from google.cloud import storage

        # Generate unique filename
        filename = generate_filename(file.filename)
        blob_name = f"{folder}/{filename}"

        # Get bucket
        bucket = client.bucket(GCS_BUCKET_NAME)
        blob = bucket.blob(blob_name)

        # Read file content
        content = await file.read()

        # Set content type
        content_type = file.content_type or "application/octet-stream"

        # Upload to GCS
        blob.upload_from_string(content, content_type=content_type)

        # Make the blob publicly accessible (optional)
        # blob.make_public()

        # Return the public URL
        return blob.public_url

    except Exception as e:
        print(f"GCS upload failed: {e}")
        # Fallback to local storage
        return await save_file_locally(file, folder)
