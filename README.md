## AI Search Assistant (Backend)

<img width="1126" height="665" alt="Screen Shot 2025-10-02 at 9 47 13 PM" src="https://github.com/user-attachments/assets/44081236-0dae-442d-b71f-53f04ba17f10" />

Demo: https://claudia-teng.github.io/ai-search-frontend/

Frontend: https://github.com/Claudia-teng/ai-search-frontend

![Screen Recording 2025-10-02 at 9 48 12 PM mov](https://github.com/user-attachments/assets/0d0d81b8-0e07-46df-a2b4-c9a12295e257)

### 📝 Description
This project is a real-time, Perplexity-style AI search platform that uses a multi-agent system over WebSockets to instantly generate comprehensive summaries from external sources.

### 🏷 Overview
- FastAPI app that launches an AutoGen-based chat agent and a WebSocket server for streaming messages.
- A simple frontend is served at `/frontend` for local testing.

### 🌎 Environment variables
- `OPENAI_API_KEY`: OpenAI API key
- `OPENAI_MODEL`: Model name (e.g., gpt-4)
- `SERPAPI_KEY`: SerpAPI key used by the web search tool

### ▶️ Quick start (local, with uv)
```bash
# 1. Install deps
uv sync

# 2. Run (auto-reload)
uv run uvicorn main:app --reload
```

### 🐳 Docker
```bash
# Build image
docker build -t ai-search-backend .

# Run image
docker run --rm -p 8000:8000 -p 8080:8080 --env-file .env ai-search-backend
```

### 🔧 Architecture

<img width="655" height="453" alt="Screen Shot 2025-10-02 at 8 40 48 PM" src="https://github.com/user-attachments/assets/1423e12b-b5ec-43a4-88b8-d57253a5654a" />

- FastAPI app (`main.py`):
  - Defines `app = FastAPI(...)` with a lifespan that starts a standalone websocket server:
  - Serves a minimal HTML test page at `/frontend`.
- WebSocket handler (`on_connect` in `main.py`):
  - Reads the initial client message and triggers the agent workflow.
- Agent setup (AutoGen):
  - `ConversableAgent` named `chatbot` that must use the `perform_web_search` tool to answer.
  - `UserProxyAgent` receives query from the client and initiates the chat.
- Tool (`search_function.py`):
  - Calls SerpAPI using `SERPAPI_KEY` and returns a structured JSON payload with URLs.

### 🕵 Agent responsibilities
- Chatbot (ConversableAgent):
  - Call the registered tool (`perform_web_search`) and summarizes findings.
- UserProxyAgent:
  - Initiates the chat with the agent, limits the number of rounds, and handles termination conditions.
- Tool (`perform_web_search`):
  - Performs the external web search via SerpAPI and formats results.

### 🌐 Deployment
<img width="729" height="528" alt="Screen Shot 2025-10-02 at 8 42 27 PM" src="https://github.com/user-attachments/assets/8402de49-5823-4329-87b5-534377ddc1a7" />

This project is deployed on Railway through Dockerfile.

### 📒 Reference
https://docs.ag2.ai/latest/docs/use-cases/notebooks/notebooks/agentchat_websockets/

The application achieves real-time responsiveness by implementing WebSockets for agent communication, directly following the non-blocking I/O pattern demonstrated in the official Autogen documentation. This ensures immediate streaming of research results from the multi-agent system to the user interface.

