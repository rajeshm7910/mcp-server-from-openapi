"""OpenAPI to MCP Tools Converter

This module provides functionality to convert any OpenAPI specification into MCP tools.
It parses the OpenAPI spec and creates corresponding MCP tool functions for each endpoint.
"""

import json
from typing import Any, Dict, Optional
import httpx
from mcp.server.fastmcp import FastMCP
import yaml
from pathlib import Path

class OpenAPIMCP:
    """Converts OpenAPI spec to MCP tools and provides functionality to make API calls."""
    
    def __init__(self, name: str, openapi_spec_path: str, base_url: Optional[str] = None):
        """Initialize the OpenAPI MCP converter.
        
        Args:
            name: Name for the MCP server
            openapi_spec_path: Path to the OpenAPI specification file (JSON or YAML)
            base_url: Base URL for the API (if not specified in the OpenAPI spec)
        """
        self.mcp = FastMCP(name=name, json_response=False, stateless_http=False)
        self.base_url = base_url
        self.spec = self._load_spec(openapi_spec_path)
        self.base_url = base_url or self.spec.get('servers', [{}])[0].get('url', '')
        self._create_tools()
        
    def _load_spec(self, spec_path: str) -> Dict[str, Any]:
        """Load OpenAPI specification from file."""
        path = Path(spec_path)
        with open(path) as f:
            if path.suffix.lower() == '.json':
                return json.load(f)
            elif path.suffix.lower() in ['.yaml', '.yml']:
                return yaml.safe_load(f)
            else:
                raise ValueError("OpenAPI spec must be in JSON or YAML format")
    
    def _create_tools(self):
        """Create MCP tools from OpenAPI paths."""
        for path, path_item in self.spec.get('paths', {}).items():
            for method, operation in path_item.items():
                if method.lower() in ['get', 'post', 'put', 'delete', 'patch']:
                    self._create_tool(path, method, operation)
    
    def _create_tool(self, path: str, method: str, operation: Dict[str, Any]):
        """Create a single MCP tool for an API endpoint."""
        
        # Get operation details
        operation_id = operation.get('operationId', f"{method}_{path.replace('/', '_')}")
        summary = operation.get('summary', '')
        description = operation.get('description', '')
        
        # Get parameters
        parameters = operation.get('parameters', [])
        request_body = operation.get('requestBody', {})
        
        # Create parameter schema
        param_schema = {}
        for param in parameters:
            param_schema[param['name']] = {
                'type': param.get('schema', {}).get('type', 'string'),
                'description': param.get('description', ''),
                'required': param.get('required', False)
            }
            
        if request_body:
            content = request_body.get('content', {})
            if 'application/json' in content:
                schema = content['application/json'].get('schema', {})
                if 'properties' in schema:
                    for prop_name, prop_schema in schema['properties'].items():
                        param_schema[prop_name] = {
                            'type': prop_schema.get('type', 'string'),
                            'description': prop_schema.get('description', ''),
                            'required': prop_name in schema.get('required', [])
                        }
        
        # Create the tool function
        async def api_call(**kwargs):
            """Make API call to the endpoint."""
            url = f"{self.base_url}{path}"
            
            # Handle path parameters
            for param in parameters:
                if param['in'] == 'path' and param['name'] in kwargs:
                    url = url.replace(f"{{{param['name']}}}", str(kwargs[param['name']]))
            
            # Prepare request
            headers = {'Content-Type': 'application/json'}
            params = {}
            data = {}
            
            # Handle query parameters
            for param in parameters:
                if param['in'] == 'query' and param['name'] in kwargs:
                    params[param['name']] = kwargs[param['name']]
            
            # Handle request body
            if request_body and 'application/json' in request_body.get('content', {}):
                data = {k: v for k, v in kwargs.items() if k not in params}
            
            # Make the request
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.request(
                        method=method.upper(),
                        url=url,
                        params=params,
                        json=data if data else None,
                        headers=headers
                    )
                    response.raise_for_status()
                    return response.json()
                except Exception as e:
                    return f"Error making API call: {str(e)}"
        
        # Register the tool with MCP
        self.mcp.tool()(api_call)
        api_call.__name__ = operation_id
        api_call.__doc__ = f"{summary}\n\n{description}\n\nParameters:\n" + \
                          "\n".join(f"- {name}: {schema['description']}" 
                                  for name, schema in param_schema.items())
    
    def get_app(self):
        """Get the FastAPI application."""
        return self.mcp.streamable_http_app

if __name__ == "__main__":
    import argparse
    import uvicorn
    
    parser = argparse.ArgumentParser(description="Run MCP server with OpenAPI tools")
    parser.add_argument("--spec", required=True, help="Path to OpenAPI specification file")
    parser.add_argument("--name", default="openapi", help="Name for the MCP server")
    parser.add_argument("--base-url", help="Base URL for the API")
    parser.add_argument("--port", type=int, default=8123, help="Port to run the server on")
    args = parser.parse_args()
    
    # Create OpenAPI MCP server
    openapi_mcp = OpenAPIMCP(args.name, args.spec, args.base_url)
    
    # Run the server
    uvicorn.run(openapi_mcp.get_app(), host="localhost", port=args.port) 