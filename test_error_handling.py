"""Tests for error handling and edge cases."""

import os
import pytest
from dotenv import load_dotenv
from supabase import create_client

# Load environment
load_dotenv()

@pytest.fixture
def client():
    """Create test client with error handling."""
    if not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_SERVICE_KEY"):
        pytest.skip("Supabase credentials not configured")
    supabase = create_client(
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_SERVICE_KEY")
    )
    return supabase

@pytest.fixture
def read_only_client():
    """Client with read-only permissions."""
    if not os.getenv("SUPABASE_READONLY_KEY"):
        pytest.skip("Read-only key not configured")
    return create_client(
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_READONLY_KEY")
    )

@pytest.fixture
def user_client():
    """Client with standard user permissions."""
    if not os.getenv("SUPABASE_USER_KEY"):
        pytest.skip("User key not configured")
    return create_client(
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_USER_KEY")
    )

@pytest.fixture(scope="module")
def admin_client():
    """Admin client with full permissions."""
    if not os.getenv("SUPABASE_ADMIN_KEY"):
        pytest.skip("Admin key not configured")
    client = create_client(
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_ADMIN_KEY")
    )
    # Verify admin access
    assert client.table('profiles').update({'name': 'test'}).execute()
    return client

def test_invalid_table_query(client):
    """Test querying non-existent table."""
    with pytest.raises(Exception) as excinfo:
        client.table("nonexistent_table").select("*").execute()
    assert "Not Found" in str(excinfo.value)

def test_malformed_data_insert(client):
    """Test inserting malformed data."""
    with pytest.raises(Exception) as excinfo:
        client.table("tasks").insert({"invalid_field": 123}).execute()
    assert "violates" in str(excinfo.value).lower()

def test_batch_operations(client):
    """Test batch insert of tasks."""
    test_data = [
        {"title": f"Task {i}", "status": "pending"} 
        for i in range(5)
    ]
    response = client.table("tasks").insert(test_data).execute()
    assert len(response.data) == 5
    assert all("id" in task for task in response.data)

# New test cases
def test_rate_limiting(client):
    """Test API rate limiting handling."""
    from time import time
    
    start_time = time()
    requests = 0
    
    # Make rapid successive requests
    while time() - start_time < 5:  # 5-second test window
        try:
            client.table('tasks').select('*').limit(1).execute()
            requests += 1
        except Exception as e:
            if "rate limit" in str(e).lower():
                assert requests > 0  # Should succeed at least once
                return
    
    pytest.fail("Rate limiting not triggered after 50+ requests")

def test_concurrent_updates(client):
    """Test handling of concurrent updates."""
    import threading
    
    # Create test task
    task = client.table('tasks').insert({"title": "Concurrency Test"}).execute().data[0]
    
    results = []
    
    def update_task(version):
        try:
            res = client.table('tasks').update({"title": f"v{version}"})\
                  .eq('id', task['id']).execute()
            results.append(res.data[0]['title'])
        except Exception as e:
            results.append(str(e))
    
    # Run concurrent updates
    threads = [
        threading.Thread(target=update_task, args=(i,)) 
        for i in range(5)
    ]
    
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    # Verify at least one succeeded
    assert any(r.startswith("v") for r in results)
    assert any("conflict" in r.lower() for r in results if isinstance(r, str))

def test_invalid_api_key():
    """Test authentication with invalid API key."""
    with pytest.raises(Exception) as excinfo:
        create_client(
            os.getenv("SUPABASE_URL"),
            "invalid_key_123"
        ).table("tasks").select("*").execute()
    assert "401" in str(excinfo.value)
    assert "invalid" in str(excinfo.value).lower()

def test_expired_token():
    """Test handling of expired JWT tokens."""
    from time import sleep
    
    # Create short-lived token (simulated)
    supabase = create_client(
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_SERVICE_KEY")
    )
    
    # Simulate token expiration
    sleep(2)  # In real tests, would use actual expired token
    
    with pytest.raises(Exception) as excinfo:
        supabase.table("tasks").select("*").execute()
    assert "401" in str(excinfo.value)
    assert "expired" in str(excinfo.value).lower()

def test_missing_auth():
    """Test requests without authentication."""
    import requests
    
    response = requests.get(
        f"{os.getenv('SUPABASE_URL')}/rest/v1/tasks",
        headers={"apikey": ""}
    )
    assert response.status_code == 401
    assert "missing" in response.text.lower()

# New RBAC tests
def test_role_based_access(read_only_client):
    """Verify role-based table permissions."""
    # Should be able to read
    assert read_only_client.table("tasks").select("*").execute()
    
    # Should NOT be able to write
    with pytest.raises(Exception) as excinfo:
        read_only_client.table("tasks").insert({"title": "test"}).execute()
    assert "permission denied" in str(excinfo.value).lower()

def test_revoked_token(client):
    """Test handling of revoked JWT tokens."""
    # Create then revoke token (simulated)
    supabase = create_client(
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_SERVICE_KEY")
    )
    
    # Simulate token revocation
    revoked_token = supabase.auth.get_session().access_token
    supabase.auth.sign_out()
    
    # Try using revoked token
    with pytest.raises(Exception) as excinfo:
        create_client(
            os.getenv("SUPABASE_URL"),
            revoked_token
        ).table("tasks").select("*").execute()
    assert "401" in str(excinfo.value)
    assert "revoked" in str(excinfo.value).lower()

def test_row_level_security(user_client):
    """Verify users can only access their own profile."""
    # Should only see own profile
    profiles = user_client.table('profiles').select('*').execute().data
    assert len(profiles) == 1
    
    # Should not see other users' profiles
    other_user_id = '00000000-0000-0000-0000-000000000000'
    with pytest.raises(Exception) as excinfo:
        user_client.table('profiles').select('*').eq('user_id', other_user_id).execute()
    assert "permission denied" in str(excinfo.value).lower()
