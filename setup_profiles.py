"""Setup profiles table in Supabase."""

import os
import json
import asyncio
import httpx
from dotenv import load_dotenv
from postgrest import AsyncPostgrestClient

# Load environment variables
load_dotenv()

# Get Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

async def setup_profiles():
    """Create profiles table and insert test data."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("Error: Supabase credentials not found in environment")
        return
        
    # Create profiles table using the REST API
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS profiles (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        username TEXT UNIQUE NOT NULL,
        status TEXT DEFAULT 'active',
        metadata JSONB DEFAULT '{}',
        updated_at TIMESTAMPTZ DEFAULT NOW(),
        created_at TIMESTAMPTZ DEFAULT NOW()
    );
    """
    
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            # Execute SQL to create table
            response = await client.post(
                f"{SUPABASE_URL}/rest/v1/rpc/exec",
                headers=headers,
                json={"sql": create_table_sql}
            )
            
            if response.status_code == 200:
                print("Successfully created profiles table")
                
                rest_url = f"{SUPABASE_URL}/rest/v1"
                postgrest_client = AsyncPostgrestClient(
                    rest_url,
                    headers={
                        "apikey": SUPABASE_KEY,
                        "Authorization": f"Bearer {SUPABASE_KEY}"
                    }
                )
                
                try:
                    # Try to insert test data
                    test_profiles = [
                        {
                            "username": "test_user1",
                            "status": "active",
                            "metadata": {"role": "admin"}
                        },
                        {
                            "username": "test_user2",
                            "status": "inactive",
                            "metadata": {"role": "user"}
                        }
                    ]
                    
                    for profile in test_profiles:
                        try:
                            result = await postgrest_client.from_("profiles").insert(profile).execute()
                            print(f"Created profile: {profile['username']}")
                        except Exception as e:
                            if "duplicate key value" in str(e):
                                print(f"Profile {profile['username']} already exists")
                            else:
                                print(f"Error creating profile {profile['username']}: {e}")
                                
                except Exception as e:
                    print(f"Error: {str(e)}")
                    
            else:
                print(f"Error creating table: {response.text}")
                
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(setup_profiles())
