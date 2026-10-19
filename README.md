# DOREMUS Chatbot - MCP Integration

A chatbot application that integrates with the **DOREMUS Knowledge Graph** through the **Model Context Protocol (MCP)**, enabling intelligent querying of classical music metadata.

## 🎵 Overview

This project combines a **React frontend** with a **FastAPI backend** to provide an interactive interface for querying the DOREMUS Knowledge Graph—a comprehensive database of classical music information including works, composers, performances, recordings, and instrumentation.

The application uses:

- **LangGraph** for building agentic workflows
- **LangChain** for LLM integration with tool binding
- **Model Context Protocol (MCP)** for structured access to the DOREMUS Knowledge Graph
- **Multiple LLM providers** (OpenAI, Ollama)

## 📁 Project Structure

```
ChatbotMCP/
├── backend/                    # Python FastAPI backend
│   ├── src/
│   │   ├── server.py          # FastAPI application & HTTP endpoints
│   │   ├── .env               # Environment variables & API keys
│   │   └── agent/
│   │       ├── mcp_testing_agent.py       # Agent initialization & LLM setup
│   │       ├── extended_mcp_client.py     # Custom MCP client wrapper
│   │       ├── prompts.py                 # System prompts & agent instructions
│   │       └── __init__.py
│   ├── pyproject.toml         # Poetry project configuration
│   └── requirements.txt        # Python dependencies
│
├── frontend/                   # React + Vite frontend
│   ├── src/
│   │   ├── App.jsx            # Main React component
│   │   ├── App.css            # Application styles (Tailwind CSS)
│   │   ├── main.jsx           # React entry point
│   │   └── assets/            # Static assets
│   ├── index.html             # HTML template
│   ├── vite.config.js         # Vite configuration
│   ├── tailwind.config.js     # Tailwind CSS configuration
│   ├── package.json           # Node.js dependencies
│   └── public/                # Public static files
│
└── README.md                  # This file
```

## 🚀 How to Setup the server

### Clone the Repo

```bash
git clone https://github.com/d4darius/ChatbotMCP.git
cd ChatbotMCP
```

### Setup the .env variables

Create the file

```bash
nano .env
```

Edit `.env` with your API keys:

```dotenv
OPENAI_API_KEY=sk-...
OPENAI_MODELS=gpt-5.6
LANGSMITH_API_KEY=lsv2_...
OLLAMA_API_URL=https://llm.tools.eurecom.fr/v1
OLLAMA_API_KEY=sk-...
OLLAMA_MODELS=...
```

4. **Build the docker container:**

   ```bash
   docker build -t mcp-chatbot-app .
   ```

Then launch it

```bash
   docker run -d \
  --name my-chatbot \
  --restart always \
  -p 8001:8001 \
  --env-file .env \
  mcp-chatbot-app
```

## 🔌 API Endpoints

### `POST /chat`

Send a message to the chatbot and receive streaming responses.

**Request:**

```json
{
  "message": "Find all compositions by Beethoven in the knowledge graph",
  "model": "gpt-5.6"
}
```

**Response:** Server-Sent Events (SSE) stream with:

- `type: "token"` - Streamed text response from the LLM
- `type: "tool"` - Tool calls (e.g., SPARQL queries generated)

**Query Parameters:**

- `model`: Model name, as listed by `GET /models` (e.g. `gpt-5.6`)

### `GET /models`

Returns the models that can be selected. A model is listed only when its provider's API key is present in `.env`.

**Response:**

```json
{
  "models": [
    { "id": "gpt-5.6", "label": "openai - gpt-5.6" },
    { "id": "<model>", "label": "ollama - <model>" }
  ],
  "default": "gpt-5.6"
}
```

### `GET /`

Returns a welcome message and server status.

## 🤖 How It Works

```mermaid
graph LR
    A[User Message] -->|React Frontend| B[FastAPI Backend]
    B -->|HTTP Request| C[Agent Initialization]
    C -->|MCP Client| D[DOREMUS Knowledge Graph]
    D -->|SPARQL Results| E[LLM Processing]
    E -->|Streaming Response| B
    B -->|Server-Sent Events| A
```

### Agent Workflow

1. **User Input**: User sends a natural language query via the React frontend
2. **Agent Init**: Backend initializes a LangGraph React agent with:
   - Selected LLM (OpenAI or Ollama)
   - MCP tools from DOREMUS Knowledge Graph
   - System prompt with DOREMUS ontology knowledge
3. **Tool Binding**: LLM can call MCP tools to:
   - Explore the DOREMUS ontology
   - Find entity URIs
   - Retrieve entity properties
   - Execute SPARQL queries
4. **Response**: Formatted results returned as a stream to the frontend

## 🛠️ Key Technologies

### Backend

| Technology                 | Purpose                                 |
| -------------------------- | --------------------------------------- |
| **FastAPI**                | REST API framework                      |
| **uvicorn**                | ASGI server                             |
| **LangChain**              | LLM orchestration & tool integration    |
| **LangGraph**              | Agentic workflows (ReAct agent pattern) |
| **langchain-mcp-adapters** | MCP ↔ LangChain compatibility           |
| **mcp**                    | Model Context Protocol implementation   |

### Frontend

| Technology       | Purpose                     |
| ---------------- | --------------------------- |
| **React 19**     | UI framework                |
| **Vite**         | Fast bundler & dev server   |
| **Tailwind CSS** | Utility-first CSS framework |
| **Lucide React** | Icon library                |

## 📊 DOREMUS Knowledge Graph

**DOREMUS** is a comprehensive ontology for classical music metadata based on **CIDOC-CRM** with **FRBR** (Work-Expression-Manifestation-Item) extensions.

### Data Model

- **Work**: Conceptual musical idea (e.g., "Beethoven's 9th Symphony")
- **Expression**: Musical realization with notation, title, composer
- **Manifestation**: Physical recording or publication
- **Item**: Specific instance of a manifestation
- **Event**: Performance or recording event

### Vocabularies

- Musical keys
- Modes
- Genres
- Media of performance
- Thematic catalogs
- Derivation types
- Functions

## 🔑 Environment Variables

| Variable                | Description               | Example                           |
| ----------------------- | ------------------------- | --------------------------------- |
| `OPENAI_API_KEY`        | OpenAI API key            | `sk-...`                          |
| `OPENAI_MODELS`         | Comma-separated OpenAI model list | `gpt-5.6`                 |
| `LANGSMITH_API_KEY`     | LangSmith tracing API key | `lsv2_...`                        |
| `LANGSMITH_PROJECT`     | LangSmith project name    | `rdfMCP_tester`                   |
| `OLLAMA_API_URL`        | OpenAI-compatible endpoint for Ollama-hosted models | `https://llm.tools.eurecom.fr/v1` |
| `OLLAMA_API_KEY`        | Bearer key for `OLLAMA_API_URL` | `sk-...`                     |
| `OLLAMA_MODELS`         | Comma-separated Ollama model list | `...`                     |
| `DEFAULT_MODEL`         | Model preselected in the UI, falls back to the first available | `...` |
| `GRAPH_RECURSION_LIMIT` | Agent recursion depth     | `25`                              |
| `DOREMUS_MCP_URL`       | MCP server endpoint       | `https://Doremus.fastmcp.app/mcp` |
| `DOREMUS_MCP_TRANSPORT` | MCP transport protocol    | `streamable_http`                 |

## 🧪 Available LLM Models

Models are configured per provider through environment variables. `GET /models` offers a model only when its provider's API key is also set.

| Provider | Models variable | API key variable | Endpoint                          |
| -------- | --------------- | ---------------- | --------------------------------- |
| OpenAI   | `OPENAI_MODELS` | `OPENAI_API_KEY` | OpenAI API                        |
| Ollama   | `OLLAMA_MODELS` | `OLLAMA_API_KEY` | `OLLAMA_API_URL` (OpenAI-compatible, e.g. vLLM) |

Model lists are comma-separated, e.g. `OPENAI_MODELS=gpt-5.6,gpt-5.2`. Set `DEFAULT_MODEL` to preselect one of them in the UI. Legacy providers (native Ollama, cloud Ollama) are kept in the backend, ready to re-enable in `PROVIDERS`.

## 📝 Example Queries

- "Find all compositions by Beethoven"
- "What are the different genres in classical music?"
- "Show me recordings of Mozart symphonies"
- "Explore the relationship between works and their performances"

## 📦 Dependencies

### Backend

See [pyproject.toml](backend/pyproject.toml) for complete list:

- Core: `fastapi`, `uvicorn`, `python-dotenv`
- LLM: `langchain`, `langchain-openai`, `langchain-groq`, `langchain-anthropic`, `langchain-ollama`
- Graph: `langgraph`, `langsmith`, `langchain-mcp-adapters`
- LLMs: `openai`, `groq`, `ollama`

### Frontend

See [package.json](frontend/package.json) for complete list:

- Core: `react@19`, `react-dom@19`
- Build: `vite@7`, `autoprefixer`, `postcss`
- Styling: `tailwindcss@3`
- Icons: `lucide-react`

## 📚 Learn More

- [LangChain Documentation](https://python.langchain.com/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [DOREMUS Project](http://www.doremus.org/)
- [CIDOC-CRM Ontology](http://cidoc-crm.org/)

## 👥 Authors

- **Dario Gosmar** - dario.gosmar@eurecom.fr
- **Simone Fassio** - simone.fassio@eurecom.fr

## 📄 License

This project is part of the DOREMUS initiative. See project repository for license information.

---

**Happy querying! 🎼**
