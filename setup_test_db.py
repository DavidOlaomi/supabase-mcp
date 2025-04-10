"""Set up test database for Supabase MCP tools."""

import os
import asyncio
from postgrest import AsyncPostgrestClient

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Get Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

async def setup_test_data():
    """Create test table and insert sample data."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("Supabase credentials not found in environment")
    
    rest_url = f"{SUPABASE_URL}/rest/v1"
    client = AsyncPostgrestClient(
        rest_url,
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Prefer": "return=representation"
        }
    )
    
    # Sample tasks data
    tasks = [
        {"title": "Task 1", "status": "pending", "priority": "high"},
        {"title": "Task 2", "status": "completed", "priority": "medium"},
        {"title": "Task 3", "status": "pending", "priority": "low"},
        {"title": "Task 4", "status": "completed", "priority": "high"},
        {"title": "Task 5", "status": "pending", "priority": "medium"},
        {"title": "Task 6", "status": "in_progress", "priority": "high"},
        {"title": "Task 7", "status": "pending", "priority": "low"},
        {"title": "Task 8", "status": "completed", "priority": "medium"},
        {"title": "Task 9", "status": "pending", "priority": "high"},
        {"title": "Task 10", "status": "in_progress", "priority": "low"}
    ]
    
    try:
        # Try to insert tasks (this will fail if table doesn't exist)
        result = await client.from_("tasks").insert(tasks).execute()
        print("Successfully inserted test data")
    except Exception as e:
        print(f"Error: {str(e)}")
        print("Please create the 'tasks' table in your Supabase dashboard with the following columns:")
        print("- id: SERIAL PRIMARY KEY")
        print("- title: TEXT NOT NULL")
        print("- status: TEXT NOT NULL")
        print("- priority: TEXT NOT NULL")
        print("- created_at: TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW())")

if __name__ == "__main__":
    asyncio.run(setup_test_data())
