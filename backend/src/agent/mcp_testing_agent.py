import os
from dotenv import load_dotenv
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_anthropic import ChatAnthropic
from langchain_ollama import ChatOllama

from .prompts import agent_system_prompt
from .extended_mcp_client import ExtendedMCPClient

load_dotenv(".env")

recursion_limit = int(os.getenv("GRAPH_RECURSION_LIMIT", "25"))
mcp_url = os.getenv("DOREMUS_MCP_URL", "https://Doremus.fastmcp.app/mcp")
mcp_transport = os.getenv("DOREMUS_MCP_TRANSPORT", "streamable_http")


def _create_openai(model_name: str):
    return ChatOpenAI(model=model_name, temperature=0)

def _create_ollama_compat(model_name: str):
    # OLLAMA_API_URL serves the OpenAI-compatible API (vLLM), not the native Ollama protocol
    return ChatOpenAI(
        model=model_name,
        temperature=0,
        base_url=os.getenv("OLLAMA_API_URL", "https://llm.tools.eurecom.fr/v1"),
        api_key=os.getenv("OLLAMA_API_KEY"),
    )

def _create_ollama_native(model_name: str):
    return ChatOllama(
        base_url=os.getenv("OLLAMA_API_URL", "https://mcp-kg-ollama.tools.eurecom.fr"),
        model=model_name,
        client_kwargs={"headers": {"Authorization": f"Basic {os.getenv('OLLAMA_API_KEY')}"}},
        stream=True,
        temperature=0
    )

def _create_cloud(model_name: str):
    return ChatOllama(
        base_url="https://ollama.com",
        model=model_name,
        client_kwargs={"headers": {"Authorization": f"Bearer {os.getenv('CLOUD_OLLAMA_API_KEY')}"}},
        temperature=0
    )

PROVIDERS = {
    "openai": {
        "label": "openai",
        "api_key_env": "OPENAI_API_KEY",
        "models_env": "OPENAI_MODELS",
        "create": _create_openai,
    },
    "ollama": {
        "label": "ollama",
        "api_key_env": "OLLAMA_API_KEY",
        "models_env": "OLLAMA_MODELS",
        "create": _create_ollama_compat,
    },
    # Legacy providers, ready to re-enable by adding an entry (models come from the MODELS env var):
    # "ollama_native": {"label": "ollama", "api_key_env": "OLLAMA_API_KEY", "models_env": "OLLAMA_NATIVE_MODELS", "create": _create_ollama_native},
    # "cloud": {"label": "cloud", "api_key_env": "CLOUD_OLLAMA_API_KEY", "models_env": "CLOUD_OLLAMA_MODELS", "create": _create_cloud},
}

connections = {
        "DOREMUS_MCP": {
            "transport": mcp_transport,
            "url": mcp_url
    }
}

client = ExtendedMCPClient(
    connections=connections
)

def _listed_models(provider: dict) -> list[str]:
    raw = os.getenv(provider["models_env"], "")
    return [m.strip() for m in raw.split(",") if m.strip()]

def _provider_of(model_name: str) -> str | None:
    return next(
        (name for name, provider in PROVIDERS.items() if model_name in _listed_models(provider)),
        None,
    )

def available_models() -> list[dict]:
    models = []
    for provider_name, provider in PROVIDERS.items():
        if not os.getenv(provider["api_key_env"]):
            continue
        for model_name in _listed_models(provider):
            models.append({
                "id": model_name,
                "label": f"{provider['label']} - {model_name}",
                "provider": provider_name,
            })
    return models

def create_model(model_name: str):
    provider_name = _provider_of(model_name)
    if provider_name is None:
        raise ValueError(f"Unknown model: {model_name}")
    return PROVIDERS[provider_name]["create"](model_name)

def default_model() -> str | None:
    """Resolve DEFAULT_MODEL to an available model, falling back to the first one."""
    requested = os.getenv("DEFAULT_MODEL", "").strip()
    models = available_models()
    if requested and any(m["id"] == requested for m in models):
        return requested
    return models[0]["id"] if models else None

async def initialize_agent(model_name: str):
    tools = await client.get_tools()
    llm = create_model(model_name)
    provider = _provider_of(model_name)

    print("DOREMUS Assistant configuration:")
    print(f"  provider: {provider}")
    print(f"  selected_model: {model_name}")
    print(f"  recursion_limit: {recursion_limit}")
    print(f"  MCP server: {mcp_url}, transport type: {mcp_transport}\n")

    agent = create_react_agent(
        llm,
        tools=tools,
        state_modifier=agent_system_prompt
    )
    return agent.with_config({"recursion_limit": recursion_limit})
