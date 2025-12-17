"""
Example usage of request timeout utilities.

This module demonstrates how to use timeout guards for:
- External API calls
- File uploads
- Heavy database queries
"""

import asyncio
from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.query_timeout import with_query_timeout
from app.core.request_timeout import (
    with_timeout,
    with_upload_timeout,
    with_api_timeout,
    with_heavy_query_timeout,
)
from app.database import get_db
from app.models import User, Post

app = FastAPI()


# Example 1: File Upload with Timeout
@app.post("/upload/example")
async def upload_file_example(file: UploadFile = File(...)):
    """
    Example endpoint showing how to use timeout for file uploads.
    """
    try:
        # Wrap the upload operation with timeout protection
        async def process_upload():
            # Read file content
            content = await file.read()
            
            # Process file (e.g., save to storage, resize image, etc.)
            # This is where your actual upload logic would go
            await asyncio.sleep(0.5)  # Simulate processing
            
            return {"filename": file.filename, "size": len(content)}
        
        # Apply timeout guard (10 seconds for uploads)
        result = await with_upload_timeout(process_upload())
        return {"message": "Upload successful", "file": result}
        
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=408,
            detail="Upload timed out. Please try again with a smaller file."
        )


# Example 2: External API Call with Timeout
@app.get("/external-data/example")
async def fetch_external_data_example():
    """
    Example endpoint showing how to use timeout for external API calls.
    
    Note: For real external API calls, use httpx or aiohttp.
    """
    try:
        # Simulate external API call
        async def fetch_from_api():
            # In production, you would use httpx or aiohttp here:
            # async with httpx.AsyncClient() as client:
            #     response = await client.get("https://api.example.com/data")
            #     return response.json()
            
            # Simulated API call
            await asyncio.sleep(1)  # Simulate network delay
            return {"data": "external_data", "status": "ok"}
        
        # Apply timeout guard (8 seconds for external APIs)
        result = await with_api_timeout(fetch_from_api())
        return result
        
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=504,
            detail="External API call timed out. Please try again later."
        )


# Example 3: Heavy Database Query with Timeout
@app.get("/analytics/example")
async def get_analytics_example(db: AsyncSession = Depends(get_db)):
    """
    Example endpoint showing how to use timeout for heavy database queries.
    
    Note: This complements the query_timeout.py module which provides
    PostgreSQL-level timeouts. Use both for comprehensive protection.
    """
    try:
        # Wrap heavy query with timeout protection
        async def compute_analytics():
            # Example: Complex aggregation query
            result = await db.execute(
                select(
                    func.count(Post.id).label('total_posts'),
                    func.count(func.distinct(Post.user_id)).label('unique_users'),
                    func.avg(Post.likes).label('avg_likes'),
                ).select_from(Post)
            )
            return result.first()
        
        # Apply timeout guard (15 seconds for heavy queries)
        stats = await with_heavy_query_timeout(compute_analytics())
        
        return {
            "total_posts": stats.total_posts,
            "unique_users": stats.unique_users,
            "avg_likes": float(stats.avg_likes or 0),
        }
        
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=504,
            detail="Analytics query timed out. Try narrowing the date range."
        )


# Example 4: Custom Timeout for Specific Operation
@app.post("/process/example")
async def process_with_custom_timeout():
    """
    Example endpoint showing how to use custom timeout values.
    """
    try:
        async def custom_operation():
            # Your custom operation here
            await asyncio.sleep(2)
            return "processed"
        
        # Use custom timeout (3 seconds)
        result = await with_timeout(custom_operation(), timeout=3)
        return {"status": "success", "result": result}
        
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=504,
            detail="Processing timed out. Please try again."
        )


# Example 5: Multiple Operations with Different Timeouts
@app.post("/batch/example")
async def batch_operations_example(
    files: list[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Example showing how to handle multiple operations with different timeouts.
    """
    results = []
    
    for file in files:
        try:
            # Each file upload gets its own timeout
            async def upload_single():
                content = await file.read()
                # Process file
                await asyncio.sleep(0.3)
                return {"filename": file.filename, "size": len(content)}
            
            result = await with_upload_timeout(upload_single())
            results.append({"success": True, "file": result})
            
        except asyncio.TimeoutError:
            results.append({
                "success": False,
                "filename": file.filename,
                "error": "Upload timed out"
            })
    
    return {
        "total": len(files),
        "successful": sum(1 for r in results if r["success"]),
        "results": results
    }


# Example 6: Combining Request Timeout with Query Timeout
@app.get("/users/search/example")
async def search_users_example(query: str, db: AsyncSession = Depends(get_db)):
    """
    Example showing how to combine request timeout with database query timeout.
    
    Best practice: Use both for comprehensive protection:
    - Request timeout (Python asyncio level) - this module
    - Query timeout (PostgreSQL level) - query_timeout.py
    """
    try:
        async def search_operation():
            # Apply both request-level and query-level timeouts
            async with with_query_timeout(db, timeout_ms=5000):
                result = await db.execute(
                    select(User)
                    .where(User.username.ilike(f"%{query}%"))
                    .limit(50)
                )
                users = result.scalars().all()
                return [{"id": u.id, "username": u.username} for u in users]
        
        # Apply request-level timeout
        users = await with_timeout(search_operation(), timeout=8)
        return {"users": users, "count": len(users)}
        
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=504,
            detail="Search timed out. Try a more specific query."
        )


# Example 7: Graceful Degradation with Timeout
@app.get("/dashboard/example")
async def dashboard_example(db: AsyncSession = Depends(get_db)):
    """
    Example showing graceful degradation when operations timeout.
    
    Instead of failing the entire request, we return partial data.
    """
    dashboard_data = {
        "user_count": None,
        "post_count": None,
        "recent_activity": None,
    }
    
    # Try to get user count (with timeout)
    try:
        async def get_user_count():
            result = await db.execute(select(func.count(User.id)))
            return result.scalar()
        
        dashboard_data["user_count"] = await with_timeout(
            get_user_count(), 
            timeout=2
        )
    except asyncio.TimeoutError:
        dashboard_data["user_count"] = "unavailable"
    
    # Try to get post count (with timeout)
    try:
        async def get_post_count():
            result = await db.execute(select(func.count(Post.id)))
            return result.scalar()
        
        dashboard_data["post_count"] = await with_timeout(
            get_post_count(), 
            timeout=2
        )
    except asyncio.TimeoutError:
        dashboard_data["post_count"] = "unavailable"
    
    # Try to get recent activity (with timeout)
    try:
        async def get_recent_activity():
            result = await db.execute(
                select(Post)
                .order_by(Post.created_at.desc())
                .limit(10)
            )
            return [{"id": p.id, "content": p.content} for p in result.scalars()]
        
        dashboard_data["recent_activity"] = await with_timeout(
            get_recent_activity(), 
            timeout=3
        )
    except asyncio.TimeoutError:
        dashboard_data["recent_activity"] = "unavailable"
    
    return dashboard_data


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
