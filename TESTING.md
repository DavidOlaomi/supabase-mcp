# Test Setup Guide

## 1. Test User Configuration

Create these roles in Supabase SQL:
```sql
CREATE ROLE test_readonly NOINHERIT;
GRANT SELECT ON ALL TABLES TO test_readonly;

CREATE ROLE test_user NOINHERIT;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES TO test_user;
```

## 2. Environment Setup

```bash
# Generate test tokens
python tools/generate_test_tokens.py

# Run tests
pytest supabase-mcp/ -v
```

## 3. Test Hierarchy

- `test_connection.py`: Basic connectivity
- `test_tools.py`: Database utilities
- `test_error_handling.py`: Edge cases & security
- `test_user_management.py`: CRUD operations
