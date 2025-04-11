"""Test suite for Supabase user management."""

import os
import pytest
import pytest_asyncio
from dotenv import load_dotenv
from postgrest import AsyncPostgrestClient
from tools import read_paginated, read_paginated_with_filter

# Load environment variables
load_dotenv()

# Get Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

@pytest_asyncio.fixture
async def client():
    """Create a Supabase client for testing."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        pytest.skip("Supabase credentials not found in environment")
    
    rest_url = f"{SUPABASE_URL}/rest/v1"
    return AsyncPostgrestClient(
        rest_url,
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}"
        }
    )

@pytest.mark.asyncio
async def test_read_tasks(client):
    """Test reading from the tasks table."""
    try:
        # Test with default parameters
        result = await read_paginated(client, "tasks")
        assert isinstance(result, dict)
        assert "data" in result
        assert "metadata" in result
        assert isinstance(result["data"], list)
        
        metadata = result["metadata"]
        assert "total_count" in metadata
        assert "page" in metadata
        assert "page_size" in metadata
        assert "total_pages" in metadata
        assert "has_more" in metadata
        
        # Verify task data structure
        if result["data"]:
            task = result["data"][0]
            assert "id" in task
            assert "status" in task
            
        # Test with custom page size
        result = await read_paginated(client, "tasks", page_size=5)
        assert len(result["data"]) <= 5
        
        # Test with specific page
        result = await read_paginated(client, "tasks", page=2, page_size=5)
        assert result["metadata"]["page"] == 2
        
    except Exception as e:
        pytest.fail(f"Test failed: {str(e)}")

@pytest.mark.asyncio
async def test_filter_tasks(client):
    """Test filtering tasks."""
    try:
        # Test filtering by status
        filters = {"status": "pending"}
        result = await read_paginated_with_filter(
            client,
            "tasks",
            filters=filters
        )
        
        assert isinstance(result, dict)
        assert "data" in result
        assert "metadata" in result
        
        # Verify all returned tasks match the filter
        for task in result["data"]:
            assert task["status"] == "pending"
            
        # Test filtering by multiple statuses
        filters = {"status": ["pending", "completed"]}
        result = await read_paginated_with_filter(
            client,
            "tasks",
            filters=filters
        )
        
        # Verify all returned tasks match the filter
        for task in result["data"]:
            assert task["status"] in ["pending", "completed"]
            
    except Exception as e:
        pytest.fail(f"Test failed: {str(e)}")

@pytest.mark.asyncio
async def test_task_search(client):
    """Test searching tasks."""
    try:
        # Get all tasks to check available data
        result = await client.from_("tasks").select("*").execute()
        assert isinstance(result.data, list)
        
        if result.data:
            # Print sample data for inspection
            print("\nSample task data:")
            for task in result.data[:3]:
                print(task)
            
    except Exception as e:
        pytest.fail(f"Test failed: {str(e)}")

@pytest.mark.asyncio
async def test_edge_cases(client):
    """Test edge cases for task operations."""
    try:
        # Test invalid table name
        with pytest.raises(RuntimeError):
            await read_paginated(client, "nonexistent_table")
            
        # Test invalid page number
        result = await read_paginated(client, "tasks", page=0)
        assert result["metadata"]["page"] == 1  # Should adjust to page 1
            
        # Test invalid page size
        with pytest.raises(ValueError):
            await read_paginated(client, "tasks", page_size=0)
            
        # Test empty result set
        filters = {"status": "nonexistent_status"}
        result = await read_paginated_with_filter(
            client,
            "tasks",
            filters=filters
        )
        assert len(result["data"]) == 0
        assert result["metadata"]["total_count"] == 0
        assert result["metadata"]["total_pages"] == 0
        assert not result["metadata"]["has_more"]
            
    except Exception as e:
        pytest.fail(f"Test failed: {str(e)}")
