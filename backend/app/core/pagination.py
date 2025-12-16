"""
Mobile-Optimized Pagination System

Implements dual pagination strategies:
1. Offset-based pagination (for web/traditional APIs)
2. Cursor-based pagination (for mobile infinite scroll)

Features:
- Efficient cursor-based pagination using last record ID
- Backward compatible offset/limit support
- Rich metadata (has_next, has_previous, total_count)
- Optimized for large datasets
"""
import base64
import json
from typing import Any, Dict, List, Optional, TypeVar, Generic
from datetime import datetime
from pydantic import BaseModel
from sqlalchemy import desc, asc, select, func
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar('T')


class PaginationMetadata(BaseModel):
    """Pagination metadata for responses."""
    total: Optional[int] = None
    page: Optional[int] = None
    per_page: Optional[int] = None
    has_next: bool = False
    has_previous: bool = False
    next_cursor: Optional[str] = None
    previous_cursor: Optional[str] = None


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response."""
    success: bool = True
    data: List[T]
    pagination: PaginationMetadata


def encode_cursor(record_id: int, created_at: Optional[datetime] = None) -> str:
    """
    Encode cursor from record ID and optional timestamp.
    
    Cursor format: base64(json({id: int, ts: iso8601}))
    """
    cursor_data = {"id": record_id}
    if created_at:
        cursor_data["ts"] = created_at.isoformat()
    
    cursor_json = json.dumps(cursor_data)
    cursor_bytes = cursor_json.encode('utf-8')
    return base64.urlsafe_b64encode(cursor_bytes).decode('utf-8')


def decode_cursor(cursor: str) -> Dict[str, Any]:
    """
    Decode cursor to get record ID and timestamp.
    
    Returns: {"id": int, "ts": Optional[str]}
    """
    try:
        cursor_bytes = base64.urlsafe_b64decode(cursor.encode('utf-8'))
        cursor_json = cursor_bytes.decode('utf-8')
        return json.loads(cursor_json)
    except (ValueError, KeyError, json.JSONDecodeError):
        raise ValueError("Invalid cursor format")


async def paginate_with_cursor(
    db: AsyncSession,
    query,
    model_class,
    cursor: Optional[str] = None,
    limit: int = 20,
    max_limit: int = 100,
    direction: str = "next",
    order_by_field: str = "created_at",
    order_direction: str = "desc",
) -> tuple[List[Any], PaginationMetadata]:
    """
    Cursor-based pagination for mobile apps.
    
    More efficient than offset pagination for large datasets and infinite scroll.
    
    Args:
        db: Database session
        query: Base SQLAlchemy query (with filters applied)
        model_class: SQLAlchemy model class
        cursor: Base64-encoded cursor string
        limit: Number of records to return (default 20)
        max_limit: Maximum allowed limit (default 100)
        direction: "next" or "previous"
        order_by_field: Field to order by (default "created_at")
        order_direction: "asc" or "desc" (default "desc")
    
    Returns:
        Tuple of (records, pagination_metadata)
    """
    # Enforce max limit
    limit = min(limit, max_limit)
    
    # Get the order field from model
    order_field = getattr(model_class, order_by_field)
    id_field = getattr(model_class, "id")
    
    # Apply ordering
    if order_direction == "desc":
        query = query.order_by(desc(order_field), desc(id_field))
    else:
        query = query.order_by(asc(order_field), asc(id_field))
    
    # Apply cursor filter if provided
    if cursor:
        try:
            cursor_data = decode_cursor(cursor)
            cursor_id = cursor_data["id"]
            
            if direction == "next":
                # Get records after cursor
                if order_direction == "desc":
                    query = query.where(id_field < cursor_id)
                else:
                    query = query.where(id_field > cursor_id)
            else:
                # Get records before cursor (for previous page)
                if order_direction == "desc":
                    query = query.where(id_field > cursor_id)
                else:
                    query = query.where(id_field < cursor_id)
        except ValueError:
            # Invalid cursor, ignore and start from beginning
            pass
    
    # Fetch limit + 1 to check if there are more records
    fetch_query = query.limit(limit + 1)
    result = await db.execute(fetch_query)
    records = list(result.scalars().all())
    
    # Check if there are more records
    has_more = len(records) > limit
    if has_more:
        records = records[:limit]  # Remove the extra record
    
    # Build pagination metadata
    metadata = PaginationMetadata()
    
    if direction == "next":
        metadata.has_next = has_more
        metadata.has_previous = cursor is not None
    else:
        metadata.has_previous = has_more
        metadata.has_next = cursor is not None
    
    # Generate cursors for next/previous
    if records:
        first_record = records[0]
        last_record = records[-1]
        
        first_created = getattr(first_record, order_by_field, None)
        last_created = getattr(last_record, order_by_field, None)
        
        metadata.next_cursor = encode_cursor(last_record.id, last_created)
        metadata.previous_cursor = encode_cursor(first_record.id, first_created)
    
    return records, metadata


async def paginate_with_offset(
    db: AsyncSession,
    query,
    skip: int = 0,
    limit: int = 20,
    max_limit: int = 100,
    count_total: bool = True,
) -> tuple[List[Any], PaginationMetadata]:
    """
    Traditional offset-based pagination.
    
    Good for web apps with page numbers, but less efficient for large datasets.
    
    Args:
        db: Database session
        query: Base SQLAlchemy query (with filters and ordering applied)
        skip: Number of records to skip
        limit: Number of records to return
        max_limit: Maximum allowed limit
        count_total: Whether to count total records (expensive for large datasets)
    
    Returns:
        Tuple of (records, pagination_metadata)
    """
    # Enforce max limit
    limit = min(limit, max_limit)
    
    # Get total count if requested (can be expensive)
    total = None
    if count_total:
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await db.execute(count_query)
        total = count_result.scalar() or 0
    
    # Apply pagination
    paginated_query = query.offset(skip).limit(limit + 1)  # +1 to check has_next
    result = await db.execute(paginated_query)
    records = list(result.scalars().all())
    
    # Check if there are more records
    has_next = len(records) > limit
    if has_next:
        records = records[:limit]  # Remove the extra record
    
    # Calculate page number
    page = (skip // limit) + 1 if limit > 0 else 1
    
    # Build metadata
    metadata = PaginationMetadata(
        total=total,
        page=page,
        per_page=limit,
        has_next=has_next,
        has_previous=skip > 0,
    )
    
    return records, metadata


async def paginate_auto(
    db: AsyncSession,
    query,
    model_class,
    # Cursor-based params
    cursor: Optional[str] = None,
    direction: str = "next",
    # Offset-based params
    skip: Optional[int] = None,
    page: Optional[int] = None,
    # Common params
    limit: int = 20,
    max_limit: int = 100,
    order_by_field: str = "created_at",
    order_direction: str = "desc",
    count_total: bool = False,
) -> tuple[List[Any], PaginationMetadata]:
    """
    Auto-detect pagination mode based on parameters.
    
    - If cursor is provided, use cursor-based pagination
    - If skip or page is provided, use offset-based pagination
    - Default to cursor-based pagination (better for mobile)
    
    Args:
        db: Database session
        query: Base SQLAlchemy query
        model_class: SQLAlchemy model class
        cursor: Cursor string for cursor-based pagination
        direction: "next" or "previous" (cursor-based)
        skip: Records to skip (offset-based)
        page: Page number (offset-based, converted to skip)
        limit: Records per page
        max_limit: Maximum allowed limit
        order_by_field: Field to order by
        order_direction: "asc" or "desc"
        count_total: Whether to count total (offset-based only)
    
    Returns:
        Tuple of (records, pagination_metadata)
    """
    # Convert page to skip if provided
    if page is not None and skip is None:
        skip = (page - 1) * limit if page > 0 else 0
    
    # Decide pagination mode
    if cursor:
        # Use cursor-based pagination
        return await paginate_with_cursor(
            db=db,
            query=query,
            model_class=model_class,
            cursor=cursor,
            limit=limit,
            max_limit=max_limit,
            direction=direction,
            order_by_field=order_by_field,
            order_direction=order_direction,
        )
    elif skip is not None:
        # Use offset-based pagination
        return await paginate_with_offset(
            db=db,
            query=query,
            skip=skip,
            limit=limit,
            max_limit=max_limit,
            count_total=count_total,
        )
    else:
        # Default to cursor-based (better for mobile)
        return await paginate_with_cursor(
            db=db,
            query=query,
            model_class=model_class,
            cursor=None,
            limit=limit,
            max_limit=max_limit,
            direction=direction,
            order_by_field=order_by_field,
            order_direction=order_direction,
        )


# Helper function for easy response formatting
def format_paginated_response(
    data: List[Any],
    pagination: PaginationMetadata,
    success: bool = True,
) -> Dict[str, Any]:
    """Format paginated response as dictionary."""
    return {
        "success": success,
        "data": data,
        "pagination": pagination.model_dump(exclude_none=True),
    }
