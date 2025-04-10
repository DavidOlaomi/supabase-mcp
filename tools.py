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
    try:
        # Validate input
        if page < 1:
            raise ValueError("Page number must be greater than 0")
        if page_size < 1:
            raise ValueError("Page size must be greater than 0")
            
        # Calculate offset for pagination
        offset = (page - 1) * page_size
        
        # Get total count first
        count_result = await client.from_(table_name).select("*", count='exact').execute()
        total_count = count_result.count if count_result.count is not None else 0
        
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
        
        # Get paginated data using headers for pagination
        query = client.from_(table_name).select(select)
        query.headers = {
            "Range-Unit": "items",
            "Range": f"{offset}-{offset + page_size - 1}"
        }
        result = await query.execute()
        
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
    try:
        # Start with base query
        query = client.from_(table_name)
        
        # Apply filters if provided
        if filters:
            # Build filter string
            filter_conditions = []
            for column, value in filters.items():
                if isinstance(value, (list, tuple)):
                    # Handle IN operations
                    values_str = ','.join(str(v) for v in value)
                    filter_conditions.append(f"{column}=in.({values_str})")
                else:
                    # Handle exact match
                    filter_conditions.append(f"{column}=eq.{value}")
            
            # Apply filters using headers
            if filter_conditions:
                query.headers = {"Prefer": f"return=representation"}
                for condition in filter_conditions:
                    query.headers[condition] = "true"
        
        # Calculate offset for pagination
        offset = (page - 1) * page_size
        
        # Get total count with filters
        count_result = await query.select("*", count='exact').execute()
        total_count = count_result.count if count_result.count is not None else 0
        
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
        
        # Get paginated data with filters
        query = query.select(select)
        query.headers.update({
            "Range-Unit": "items",
            "Range": f"{offset}-{offset + page_size - 1}"
        })
        result = await query.execute()
        
        # Calculate metadata
        total_pages = (total_count + page_size - 1) // page_size
        
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
