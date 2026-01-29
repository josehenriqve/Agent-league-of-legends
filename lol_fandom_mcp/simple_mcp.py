import asyncio
import json
import sys
import logging
from typing import Callable, Dict, Any, Awaitable, List

# Configure logging to write to stderr so it doesn't interfere with stdout JSON-RPC
logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("SimpleMCP")

class SimpleMCP:
    def __init__(self, name: str, version: str = "1.0.0"):
        self.name = name
        self.version = version
        self.tools: Dict[str, Callable[..., Awaitable[Any]]] = {}
        self.resources: Dict[str, Callable[..., Awaitable[Any]]] = {}
        self.tool_schemas: List[Dict[str, Any]] = []
        self.resource_templates: List[Dict[str, Any]] = []

    def tool(self, name: str = None, description: str = None):
        def decorator(func):
            tool_name = name or func.__name__
            tool_desc = description or func.__doc__ or ""
            
            # Simple schema generation (manual reflection for arguments is complex, 
            # so we'll just require schema to be passed or infer basic string args if not)
            # For this specific project, I'll hardcode schemas in the server usage 
            # or rely on manual schema definition if needed.
            # But to keep it simple, I'll store the function.
            self.tools[tool_name] = func
            return func
        return decorator

    def add_tool(self, func, name: str, description: str, input_schema: Dict[str, Any]):
        self.tools[name] = func
        self.tool_schemas.append({
            "name": name,
            "description": description,
            "inputSchema": input_schema
        })

    def add_resource(self, func, uri_template: str, name: str, description: str = None, mime_type: str = "text/plain"):
        # Very basic resource matching
        self.resources[uri_template] = func
        self.resource_templates.append({
            "uriTemplate": uri_template,
            "name": name,
            "description": description,
            "mimeType": mime_type
        })

    async def run(self):
        logger.info(f"Starting SimpleMCP server: {self.name}")
        
        # Buffer for reading lines
        loop = asyncio.get_event_loop()
        
        # Read from stdin line by line
        # Note: In Windows asyncio, reading from stdin can be tricky.
        # We'll use a thread executor for reading stdin to avoid blocking the loop
        
        while True:
            try:
                line = await loop.run_in_executor(None, sys.stdin.readline)
                if not line:
                    break
                
                line = line.strip()
                if not line:
                    continue
                    
                request = json.loads(line)
                await self.handle_request(request)
            except json.JSONDecodeError:
                logger.error("Failed to decode JSON")
            except Exception as e:
                logger.error(f"Error handling request: {e}")

    async def handle_request(self, request: Dict[str, Any]):
        req_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})
        
        logger.info(f"Received request: {method}")

        result = None
        error = None

        try:
            if method == "initialize":
                result = {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {},
                        "resources": {}
                    },
                    "serverInfo": {
                        "name": self.name,
                        "version": self.version
                    }
                }
            elif method == "notifications/initialized":
                # client acknowledging initialization
                return 
            elif method == "tools/list":
                result = {
                    "tools": self.tool_schemas
                }
            elif method == "tools/call":
                tool_name = params.get("name")
                args = params.get("arguments", {})
                if tool_name in self.tools:
                    func = self.tools[tool_name]
                    # We expect func to be async and accept arguments
                    tool_result = await func(**args)
                    result = {
                        "content": [{
                            "type": "text",
                            "text": str(tool_result)
                        }]
                    }
                else:
                    error = {"code": -32601, "message": f"Tool '{tool_name}' not found"}
            
            elif method == "resources/list":
                result = {
                    "resources": self.resource_templates
                }
            
            elif method == "resources/read":
                uri = params.get("uri")
                # Simple matching for verification (only supporting exact match or single arg in this mock)
                # In a real impl we'd parse the template. 
                # For now checking if we have a handler.
                
                # Check for direct match or prefix match
                content = None
                for template, func in self.resources.items():
                    # Very hacky template matching for "lol-fandom://{title}" -> simple check
                    if template == "lol-fandom://{title}" and uri.startswith("lol-fandom://"):
                        title = uri.replace("lol-fandom://", "")
                        content = await func(title)
                        break
                
                if content is not None:
                     result = {
                        "contents": [{
                            "uri": uri,
                            "mimeType": "text/plain",
                            "text": str(content)
                        }]
                    }
                else:
                    error = {"code": -32602, "message": "Resource not found"}

            elif method == "ping":
                result = {}
                
            else:
                 pass # Ignore unsupported methods or notifications
                 
        except Exception as e:
            logger.exception(f"Exception during request handling: {method}")
            error = {"code": -32603, "message": str(e)}

        if req_id is not None:
            response = {
                "jsonrpc": "2.0",
                "id": req_id
            }
            if error:
                response["error"] = error
            else:
                response["result"] = result
            
            print(json.dumps(response), flush=True)

