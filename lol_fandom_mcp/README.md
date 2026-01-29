# LOL Fandom MCP Server

A Model Context Protocol (MCP) server for the League of Legends Fandom Wiki.

## Features

- **Search Wiki**: Search for pages by title.
- **Read Page**: Get the raw content (wikitext) of a page.
- **Resources**: Access pages directly via `lol-fandom://<title>` URIs.

## Installation

1.  Ensure you have Python 3.8+ installed.
2.  Install dependencies:
    ```bash
    pip install httpx
    ```

## Usage

Run the server using Python module syntax:

```bash
python -m lol_fandom_mcp.server
```

This will start the server on `stdio`, ready to accept JSON-RPC messages from an MCP client (like Claude Desktop, mcp-inspector, or another agent).

## API

### Tools

- `search_wiki(query: str, limit: int = 10)`
- `read_page(title: str)`

### Resources

- `lol-fandom://{title}`
