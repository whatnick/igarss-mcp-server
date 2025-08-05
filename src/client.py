import asyncio
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from mcp_use import MCPAgent, MCPClient
# Create a basic fastapi app with htmx to run the MCP Client
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

def create_agent():
    # Load environment variables
    load_dotenv()

    # Create configuration dictionary
    config = {
      "mcpServers": {
        "igarss": {
            "command": "uv",
            "args": [
                "run",
                "--with",
                "mcp",
                "mcp",
                "run",
                "src/server.py"
            ],
            "env": {
                "HOME": "/home/whatnick",
                "LOGNAME": "whatnick",
                "PATH": "/home/whatnick/.npm/_npx/5a9d879542beca3a/node_modules/.bin:/home/whatnick/wsl_dev/igarss-mcp-server/node_modules/.bin:/home/whatnick/wsl_dev/node_modules/.bin:/home/whatnick/node_modules/.bin:/home/node_modules/.bin:/node_modules/.bin:/home/whatnick/.nvm/versions/node/v22.14.0/lib/node_modules/npm/node_modules/@npmcli/run-script/lib/node-gyp-bin:/home/whatnick/wsl_dev/igarss-mcp-server/.venv/bin:/home/whatnick/.local/bin:/home/whatnick/.local/bin:/home/whatnick/.nvm/versions/node/v22.14.0/bin:/home/whatnick/.krew/bin:/home/whatnick/.cargo/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/usr/lib/wsl/lib:/mnt/c/WINDOWS/system32:/mnt/c/WINDOWS:/mnt/c/WINDOWS/System32/Wbem:/mnt/c/WINDOWS/System32/WindowsPowerShell/v1.0/:/mnt/c/WINDOWS/System32/OpenSSH/:/mnt/c/Program Files/Git/cmd:/mnt/c/Program Files/dotnet/:/mnt/c/Program Files/Pandoc/:/mnt/c/ProgramData/chocolatey/bin:/mnt/c/Program Files/nodejs/:/mnt/c/Program Files/Go/bin:/mnt/c/Program Files/Amazon/AWSCLIV2/:/Docker/host/bin:/mnt/c/Program Files/starship/bin/:/mnt/c/WINDOWS/system32/config/systemprofile/AppData/Local/Microsoft/WindowsApps:/mnt/c/Users/tisha/AppData/Local/Programs/Microsoft VS Code/bin:/mnt/c/Users/tisha/AppData/Roaming/npm:/mnt/c/WINDOWS/system32/config/systemprofile/go/bin:/mnt/c/WINDOWS/system32/config/systemprofile/.krew/bin:/mnt/c/Program Files/Lens/resources/cli/bin:/mnt/c/Users/tisha/AppData/Local/Microsoft/WindowsApps:/mnt/c/tools/dart-sdk/bin:/mnt/c/Users/tisha/AppData/Local/Pub/Cache/bin:/usr/local/go/bin:/usr/local/bin",
                "SHELL": "/bin/bash",
                "TERM": "xterm-256color",
                "USER": "whatnick"
            }
        }
      }
    }

    

    # Create MCPClient from configuration dictionary
    client = MCPClient.from_dict(config)

    # Create LLM
    llm = ChatOpenAI(model="gpt-4o")

    # Create agent with the client
    agent = MCPAgent(llm=llm, client=client, max_steps=30)

    return agent

agent = create_agent()

@app.get("/", response_class=HTMLResponse)
async def index():
    return """
    <html>
        <head>
            <title>IGARSS MCP Search</title>
            <link rel="stylesheet" href="/static/style.css">
            <script src="https://unpkg.com/htmx.org"></script>
        </head>
        <body>
            <h1>IGARSS MCP Search</h1>
            <p>Use the button below to run a query.</p>
            <p>Example query: "Find papers in IGARSS 2025 with keywords 'segmentation' on Wednesday morning"</p>
            <textarea id="query" name="query" placeholder="Enter your query here" rows="3" style="width: 100%; resize: vertical;"></textarea>
            <button 
                hx-get="/run-query"
                hx-target="#result"
                hx-trigger="click"
                hx-vals='js:{"query": document.getElementById("query").value}'
            >Run Query</button>
            <div id="result"></div>
        </body>
    </html>
    """

@app.get("/run-query", response_class=HTMLResponse)
async def run_query(query: str):
    result = await agent.run(query)
    return f"<div>{result}</div>"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)