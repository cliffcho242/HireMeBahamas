"""
Pagination utilities for mobile-optimized APIs.

Supports both pagination styles:
1. Offset-based: ?skip=0&limit=20 (traditional)
2. Page-based: ?page=1&limit=20 (mobile-friendly)

Mobile Optimization:
- Small, predictable page sizes (default: 20 items)
- Consistent pagination across all list endpoints
- Clear pagination metadata in responses
"""
from typing import Optional, TypeVar, Generic, List
from pydantic import BaseModel, Field
from fastapi import Query

T = TypeVar('T')


class PaginationParams:
    """
    Dependency class for pagination parameters.
    
    Supports two pagination styles:
    1. Page-based (mobile-friendly): ?page=1&limit=20
    2. Offset-based (traditional): ?skip=0&limit=20
    
    Page-based takes precedence if both are provided.
    """
    
    def __init__(
        self,
        page: Optional[int] = Query(None, ge=1, description="Page number (1-indexed)"),
        skip: int = Query(0, ge=0, description="Number of items to skip (offset)"),
        limit: int = Query(20, ge=1, le=100, description="Items per page (max 100)")
    ):
        """
        Initialize pagination parameters.
        
        Args:
            page: 1-indexed page number (mobile-friendly)
            skip: 0-indexed offset (traditional)
            limit: Items per page (default: 20, max: 100)
        """
        self.limit = limit
        
        # If page is provided, convert to skip (page takes precedence)
        if page is not None:
            self.skip = (page - 1) * limit
            self.page = page
        else:
            self.skip = skip
            # Calculate page number from skip for metadata
            self.page = (skip // limit) + 1 if limit > 0 else 1


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Standard paginated response format.
    
    Mobile Optimization:
    - Clear pagination metadata
    - Total count for UI progress indicators
    - Easy to parse and display
    """
    success: bool = Field(True, description="Request success status")
    data: List[T] = Field(description="List of items")
    pagination: dict = Field(description="Pagination metadata")
    
    @classmethod
    def create(
        cls,
        items: List[T],
        total: int,
        page: int,
        limit: int,
        skip: int = None
    ):
        """
        Create a paginated response with metadata.
        
        Args:
            items: List of items for current page
            total: Total number of items across all pages
            page: Current page number (1-indexed)
            limit: Items per page
            skip: Offset value (optional, for backward compatibility)
            
        Returns:
            PaginatedResponse with items and pagination metadata
        """
        total_pages = (total + limit - 1) // limit if limit > 0 else 0
        has_next = page < total_pages
        has_prev = page > 1
        
        pagination_meta = {
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": total_pages,
            "has_next": has_next,
            "has_prev": has_prev,
        }
        
        # Include skip for backward compatibility
        if skip is not None:
            pagination_meta["skip"] = skip
        
        return cls(
            success=True,
            data=items,
            pagination=pagination_meta
        )


def get_pagination_metadata(
    total: int,
    page: int = None,
    skip: int = None,
    limit: int = 20
) -> dict:
    """
    Generate pagination metadata dictionary.
    
    Args:
        total: Total number of items
        page: Current page number (1-indexed, optional)
        skip: Current offset (optional)
        limit: Items per page
        
    Returns:
        Dictionary with pagination metadata
    """
    # Calculate page if not provided
    if page is None and skip is not None:
        page = (skip // limit) + 1 if limit > 0 else 1
    elif page is None:
        page = 1
    
    # Calculate skip if not provided
    if skip is None:
        skip = (page - 1) * limit
    
    total_pages = (total + limit - 1) // limit if limit > 0 else 0
    has_next = page < total_pages
    has_prev = page > 1
    
    return {
        "page": page,
        "skip": skip,
        "limit": limit,
        "total": total,
        "total_pages": total_pages,
        "has_next": has_next,
        "has_prev": has_prev,
    }


# Example usage in routes:
"""
from app.core.pagination import PaginationParams, get_pagination_metadata

@router.get("/items")
async def get_items(
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db)
):
    # Query database with pagination
    query = select(Item).offset(pagination.skip).limit(pagination.limit)
    result = await db.execute(query)
    items = result.scalars().all()
    
    # Get total count
    count_result = await db.execute(select(func.count()).select_from(Item))
    total = count_result.scalar()
    
    # Return with metadata
    return {
        "success": True,
        "items": items,
        "pagination": get_pagination_metadata(
            total=total,
            page=pagination.page,
            skip=pagination.skip,
            limit=pagination.limit
        )
    }
"""
