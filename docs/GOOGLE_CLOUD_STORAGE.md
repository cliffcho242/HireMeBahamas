# Google Cloud Storage Integration

This document explains how to set up and use Google Cloud Storage (GCS) for file uploads in HireMeBahamas.

## Overview

HireMeBahamas now supports Google Cloud Storage as a cloud storage option for uploaded files (avatars, portfolio images, documents, etc.). When configured, files will be automatically uploaded to your GCS bucket instead of local storage.

## Prerequisites

1. A Google Cloud Platform (GCP) account
2. A GCS bucket created for your application
3. Service account credentials with storage permissions

## Setup Instructions

### 1. Create a GCS Bucket

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to Cloud Storage > Buckets
3. Click "Create Bucket"
4. Choose a unique bucket name (e.g., `hiremebahamas-uploads`)
5. Select your preferred location
6. Choose storage class (Standard is recommended for frequently accessed files)
7. Set access control to "Uniform" for simplicity
8. Click "Create"

### 2. Create Service Account Credentials

1. In Google Cloud Console, go to IAM & Admin > Service Accounts
2. Click "Create Service Account"
3. Give it a name (e.g., `hiremebahamas-storage`)
4. Grant it the "Storage Object Admin" role for your bucket
5. Click "Done"
6. Click on the created service account
7. Go to the "Keys" tab
8. Click "Add Key" > "Create new key"
9. Choose JSON format
10. Download the JSON key file and store it securely

### 3. Configure Environment Variables

Add the following environment variables to your `.env` file or deployment environment:

```bash
# Google Cloud Storage Configuration
GCS_BUCKET_NAME=your-bucket-name
GCS_PROJECT_ID=your-project-id
GCS_CREDENTIALS_PATH=/path/to/credentials.json
```

**Notes:**
- `GCS_BUCKET_NAME`: The name of your GCS bucket (required)
- `GCS_PROJECT_ID`: Your GCP project ID (optional if using credentials file)
- `GCS_CREDENTIALS_PATH`: Path to your service account JSON key file (optional if using Application Default Credentials)

### 4. Alternative: Application Default Credentials

If running on Google Cloud Platform (App Engine, Cloud Run, Compute Engine, etc.), you can use Application Default Credentials instead of a service account key file:

```bash
GCS_BUCKET_NAME=your-bucket-name
GCS_PROJECT_ID=your-project-id
# No need for GCS_CREDENTIALS_PATH
```

## Usage

### API Endpoints

Once configured, you can use the following endpoints:

#### Upload Document to GCS
```
POST /api/upload/document-gcs
```

This endpoint specifically uploads files to Google Cloud Storage. If GCS is not configured, it will fall back to local storage.

#### Regular Document Upload
```
POST /api/upload/document
```

This endpoint uses Cloudinary if configured, otherwise falls back to local storage. To make it use GCS by default, you can modify the endpoint to use `upload_to_gcs` instead.

### Example Usage in Code

```python
from app.core.upload import upload_to_gcs

# Upload a file to GCS
file_url = await upload_to_gcs(file, folder="documents")
```

## Security Considerations

1. **Keep credentials secure**: Never commit your service account JSON key to version control
2. **Use environment variables**: Store credentials path in environment variables
3. **Least privilege**: Grant only necessary permissions to the service account
4. **Bucket permissions**: Configure bucket access controls appropriately
5. **HTTPS only**: GCS URLs use HTTPS by default for secure file transfer

## Bucket Permissions

For public file access, you can make objects publicly readable:

```python
# In upload.py, uncomment this line after uploading:
blob.make_public()
```

Or configure bucket-level IAM policy to allow public read access.

## Monitoring and Costs

- Monitor your GCS usage in the [Google Cloud Console](https://console.cloud.google.com/storage)
- Check pricing at [GCS Pricing](https://cloud.google.com/storage/pricing)
- Standard storage costs approximately $0.020 per GB per month
- Consider setting up lifecycle rules to automatically delete or archive old files

## Troubleshooting

### "GCS bucket does not exist" error
- Verify the bucket name is correct
- Ensure the service account has access to the bucket
- Check that the project ID matches the bucket's project

### "Permission denied" error
- Verify the service account has "Storage Object Admin" role
- Check that the credentials file is valid and not expired
- Ensure the credentials file path is correct

### Files not appearing after upload
- Check if `blob.make_public()` is uncommented if you need public access
- Verify bucket IAM policies allow public read access if needed
- Check the returned URL is correct

## Integration with Existing Code

The GCS integration is designed to work alongside existing storage options:

1. **Local Storage**: Default fallback if no cloud storage is configured
2. **Cloudinary**: Can be used via `upload_to_cloudinary()`
3. **Google Cloud Storage**: Can be used via `upload_to_gcs()`

Each method automatically falls back to local storage if not properly configured.

## Dependencies

The integration requires the following Python package:

```
google-cloud-storage==3.6.0
```

This is already included in `requirements.txt`.
