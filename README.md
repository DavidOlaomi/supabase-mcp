# Supabase MCP Server


## Features

- **Read Table Rows**: Query data from Supabase tables with optional filtering, pagination, and column selection
- **Create Table Records**: Insert new records into Supabase tables
- **Update Table Records**: Modify existing records in Supabase tables based on filters
- **Delete Table Records**: Remove records from Supabase tables based on filters

## Prerequisites

- Docker or Docker Desktop
- Supabase account and project

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/coleam00/supabase-mcp.git
   cd supabase-mcp
   ```

### Docker Setup

1. Build the Docker image:
   ```bash
   docker build -t mcp/supabase .
   ```

## Usage

### Running as an MCP Server with Docker

The Supabase MCP server can be integrated with AI assistants using the Model Context Protocol.

1. Include the below configuration in your MCP config (in Claude Desktop, Windsurf, etc.)

Be sure to build the container with the installation steps first!

```json
{
  "mcpServers": {
    "supabase": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-e", "SUPABASE_URL", "-e", "SUPABASE_SERVICE_KEY", "mcp/supabase"],
      "env": {
        "SUPABASE_URL": "YOUR-SUPABASE-URL",
        "SUPABASE_SERVICE_KEY": "YOUR-SUPABASE-SERVICE-ROLE-KEY"
      }
    }
  }
}
```

2. Replace `YOUR-SUPABASE-URL` and `YOUR-SUPABASE-SERVICE-ROLE-KEY` with your actual Supabase credentials.

3. The AI assistant can now access the Supabase database through the MCP server using the provided tools.

For more information on the Model Context Protocol, visit [modelcontextprotocol.io](https://modelcontextprotocol.io).

### Available Tools

#### Read Table Rows

```python
read_table_rows(
    table_name: str,
    columns: Optional[List[str]] = None,
    filters: Optional[Dict[str, Any]] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None
)
```

Example:
```python
# Read active users
read_table_rows(
    table_name="users",
    columns=["id", "name", "email"],
    filters={"is_active": True},
    limit=10,
    offset=0
)
```

#### Create Table Records

```python
create_table_records(
    table_name: str,
    records: Union[Dict[str, Any], List[Dict[str, Any]]]
)
```

Example:
```python
# Create a new user
create_table_records(
    table_name="users",
    records={
        "name": "John Doe",
        "email": "john@example.com",
        "is_active": True
    }
)
```

#### Update Table Records

```python
update_table_records(
    table_name: str,
    updates: Dict[str, Any],
    filters: Dict[str, Any]
)
```

Example:
```python
# Update user status
update_table_records(
    table_name="users",
    updates={"status": "premium"},
    filters={"is_active": True}
)
```

#### Delete Table Records

```python
delete_table_records(
    table_name: str,
    filters: Dict[str, Any]
)
```

Example:
```python
# Delete inactive users
delete_table_records(
    table_name="users",
    filters={"is_active": False}
)
```

## Development

### Project Structure

```
supabase-mcp/
├── supabase_mcp/
│   ├── __init__.py
│   ├── server.py              # Main MCP server implementation
│   └── tests/                 # Unit tests
├── Dockerfile                 # Docker configuration for MCP server
├── example_mcp_config.json    # Example MCP configuration
├── requirements.txt           # Python dependencies
├── .env.example               # Example environment variables
├── README.md                  # Project documentation
├── PLANNING.md                # Project planning
└── TASKS.md                   # Task tracking
```

### Running Tests

```bash
pytest supabase_mcp/tests/
```

## Model Context Protocol Integration

The Supabase MCP server implements the [Model Context Protocol](https://modelcontextprotocol.io), which allows AI assistants to interact with Supabase databases in a standardized way.

### How It Works

1. The MCP server exposes tools for database operations (read, create, update, delete)
2. AI assistants connect to the MCP server using the stdio transport
3. The AI assistant can invoke the tools to perform database operations
4. The MCP server handles the communication with Supabase and returns the results

### MCP Configuration

The `example_mcp_config.json` file shows how to configure an AI assistant to use the Supabase MCP server:

```json
{
  "mcpServers": {
    "supabase": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-e", "SUPABASE_URL", "-e", "SUPABASE_SERVICE_KEY", "mcp/supabase"],
      "env": {
        "SUPABASE_URL": "YOUR-SUPABASE-URL",
        "SUPABASE_SERVICE_KEY": "YOUR-SUPABASE-SERVICE-ROLE-KEY"
      }
    }
  }
}
```

This configuration tells the AI assistant:
- To use Docker to run the MCP server
- To pass the Supabase credentials as environment variables
- To use the `mcp/supabase` Docker image

### Using with AI Assistants

AI assistants that support the Model Context Protocol can use this server to:

1. Query data from Supabase tables
2. Insert new records into tables
3. Update existing records
4. Delete records

The assistant will have access to the tools documented in the "Available Tools" section above.

## Environment Variables

| Variable | Description |
|----------|-------------|
| `SUPABASE_URL` | URL of your Supabase project |
| `SUPABASE_SERVICE_KEY` | Service role key for Supabase authentication |

## License

This project is licensed under the MIT License - see the LICENSE file for details.
