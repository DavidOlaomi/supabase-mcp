import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Get Supabase credentials
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_KEY")

if not supabase_url or not supabase_key:
    print("Error: Missing Supabase credentials in .env file")
    exit(1)

# Initialize Supabase client
supabase: Client = create_client(supabase_url, supabase_key)
def test_connection():
    try:
        # Query tasks table
        response = supabase.table('tasks').select("*").limit(5).execute()
        
        if hasattr(response, 'error') and response.error:
            print("Connection test failed:", response.error)
            return
            
        print("Successfully connected to Supabase!")
        print("Tasks from database:", response.data)
        
    except Exception as err:
        print("Error testing connection:", str(err))

if __name__ == "__main__":
    test_connection()
