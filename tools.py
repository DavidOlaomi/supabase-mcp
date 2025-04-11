"""Tools for interacting with Supabase MCP."""

from typing import Dict, Any, Optional, List, Tuple
from postgrest import AsyncPostgrestClient
from postgrest.exceptions import APIError

async def read_paginated(
    client: AsyncPostgrestClient,
    table_name: str,
    page: int = 1,
    page_size: int = 10,
    select: str = "*"
) -> Dict[str, Any]:
    """
    Read data from a Supabase table with pagination support.
    
    Args:
        client: Supabase Postgrest client
        table_name: Name of the table to read from
        page: Page number (1-based indexing)
        page_size: Number of items per page
        select: Columns to select (default "*" for all columns)
        
    Returns:
        Dict containing:
        - data: List of records for the current page
        - metadata:
            - total_count: Total number of records
            - page: Current page number
            - page_size: Number of items per page
            - total_pages: Total number of pages
            - has_more: Whether there are more pages
    """
    # Validate page size first
    if not isinstance(page_size, int) or page_size < 1:
        raise ValueError("Page size must be greater than 0")
        
    try:
        # Validate and adjust page number
        page = max(1, page)  # Adjust invalid page to 1
            
        # Calculate offset for pagination
        offset = (page - 1) * page_size
        
        # Get total count first
        count_result = await client.from_(table_name).select("id").execute()
        total_count = len(count_result.data)
        
        if total_count == 0:
            return {
                "data": [],
                "metadata": {
                    "total_count": 0,
                    "page": page,
                    "page_size": page_size,
                    "total_pages": 0,
                    "has_more": False
                }
            }
            
        # Calculate total pages
        total_pages = (total_count + page_size - 1) // page_size
        
        # Adjust page if it exceeds total pages
        if page > total_pages:
            page = total_pages
            offset = (page - 1) * page_size
        
        # Get paginated data
        result = await (
            client.from_(table_name)
            .select(select)
            .order("id")  # Ensure consistent ordering
            .range(offset, offset + page_size - 1)
            .execute()
        )
        
        return {
            "data": result.data,
            "metadata": {
                "total_count": total_count,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages,
                "has_more": page < total_pages
            }
        }
        
    except APIError as e:
        raise RuntimeError(f"Supabase API error: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Error reading paginated data: {str(e)}")

async def read_paginated_with_filter(
    client: AsyncPostgrestClient,
    table_name: str,
    filters: Optional[Dict[str, Any]] = None,
    page: int = 1,
    page_size: int = 10,
    select: str = "*"
) -> Dict[str, Any]:
    """
    Read data from a Supabase table with pagination and filtering support.
    
    Args:
        client: Supabase Postgrest client
        table_name: Name of the table to read from
        filters: Dictionary of column-value pairs to filter by
        page: Page number (1-based indexing)
        page_size: Number of items per page
        select: Columns to select (default "*" for all columns)
        
    Returns:
        Same as read_paginated, but with filtered data
    """
    # Validate page size first
    if not isinstance(page_size, int) or page_size < 1:
        raise ValueError("Page size must be greater than 0")
        
    try:
        # Validate and adjust page number
        page = max(1, page)  # Adjust invalid page to 1
            
        # Start with base query
        query = client.from_(table_name).select(select)
        
        # Apply filters if provided
        if filters:
            for column, value in filters.items():
                if isinstance(value, (list, tuple)):
                    # Handle IN operations
                    query = query.in_(column, value)
                else:
                    # Handle exact match
                    query = query.eq(column, value)
        
        # Calculate offset for pagination
        offset = (page - 1) * page_size
        
        # Get total count with filters
        count_query = client.from_(table_name).select("id")
        if filters:
            for column, value in filters.items():
                if isinstance(value, (list, tuple)):
                    count_query = count_query.in_(column, value)
                else:
                    count_query = count_query.eq(column, value)
                    
        count_result = await count_query.execute()
        total_count = len(count_result.data)
        
        if total_count == 0:
            return {
                "data": [],
                "metadata": {
                    "total_count": 0,
                    "page": page,
                    "page_size": page_size,
                    "total_pages": 0,
                    "has_more": False
                }
            }
        
        # Calculate total pages
        total_pages = (total_count + page_size - 1) // page_size
        
        # Adjust page if it exceeds total pages
        if page > total_pages:
            page = total_pages
            offset = (page - 1) * page_size
        
        # Get paginated data with filters
        result = await (
            query
            .order("id")  # Ensure consistent ordering
            .range(offset, offset + page_size - 1)
            .execute()
        )
        
        return {
            "data": result.data,
            "metadata": {
                "total_count": total_count,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages,
                "has_more": page < total_pages
            }
        }
        
    except APIError as e:
        raise RuntimeError(f"Supabase API error: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Error reading paginated data: {str(e)}")
