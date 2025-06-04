# MCP Server from OpenAPI

A MCP server implementation from OpenAPI specifications, supporting both SSE (Server-Sent Events) and streaming responses.

## Prerequisites

- Python 3.x
- pip (Python package manager)

## Installation

1. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Server Setup

The server can be run in two modes:

### SSE Mode
```bash
python server/mcp_server_sse.py --spec server/httpbin_openapi.yaml --name httpbin --base-url https://httpbin.org
```

### Streaming Mode
```bash
python server/mcp_server_stream.py --spec server/httpbin_openapi.yaml --name httpbin --base-url https://httpbin.org
```

## Client Setup

### MCP Clients

1. Create a `.env` file in the project root and add your Anthropic API key:
```
ANTHROPIC_API_KEY=your_api_key_here
```

2. Run the client of your choice:
   - For SSE client:
   ```bash
   python client/sse_client.py
   ```
   - For streaming client:
   ```bash
   python client/stream_client.py
   ```

Example usage with SSE client:
```
MCP Client Started!
Type your queries or 'quit' to exit.

Query: Get Headers

I'll help you get the headers using the api_call function.
[Calling tool api_call with args {'kwargs': '{"action": "get_headers"}'}]
Here are the headers from the response:

```json
{
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate",
    "Content-Type": "application/json",
    "Host": "httpbin.org",
    "User-Agent": "python-httpx/0.28.1",
    "X-Amzn-Trace-Id": "Root=1-683fecc4-674af7e9323b027c4b9bc740"
}
```

### ADK Agents

1. Navigate to the Clients directory
2. Configure the environment:
   - Add the following to `.env` file in both `httpb_sse_agent` and `httpbin_stream_agent` directories:
   ```
   GOOGLE_GENAI_USE_VERTEXAI="False"
   GOOGLE_API_KEY="your_google_api_key_here"
   ```
3. Start the ADK web interface:
```bash
adk web
```

## Features

- OpenAPI specification-based endpoint generation
- Support for both SSE and streaming responses
- Multiple client implementations (MCP and ADK)
- Easy configuration through environment variables

## License

This project is licensed under the Apache 2.0 License.