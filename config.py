"""
LLM backend configuration.

AutoGen (and AG2) are orchestration layers, not models themselves — every
agent in agents.py is bound to one of the configs below. Fill in whichever
backend you actually have access to; the rest of the code does not change.
"""

import os

# ---------------------------------------------------------------------------
# OPTION 1 — OpenAI API
# ---------------------------------------------------------------------------
OPENAI_CONFIG = {
    "config_list": [
        {
            "model": "gpt-4o-mini",          # swap for any OpenAI chat model
            "api_key": os.environ.get("OPENAI_API_KEY", "PASTE_YOUR_KEY_HERE"),
        }
    ],
    "temperature": 0.2,
}

# ---------------------------------------------------------------------------
# OPTION 2 — Azure OpenAI
# ---------------------------------------------------------------------------
AZURE_CONFIG = {
    "config_list": [
        {
            "model": "gpt-4o-mini",                      # your deployment name
            "api_type": "azure",
            "api_key": os.environ.get("AZURE_OPENAI_API_KEY", "PASTE_YOUR_KEY_HERE"),
            "base_url": "https://YOUR-RESOURCE.openai.azure.com/",
            "api_version": "2024-06-01",
        }
    ],
    "temperature": 0.2,
}

# ---------------------------------------------------------------------------
# OPTION 3 — Local / open-source model via Ollama (no API key needed)
# ---------------------------------------------------------------------------
OLLAMA_CONFIG = {
    "config_list": [
        {
            "model": "llama3.1",              # any model you've pulled in Ollama
            "base_url": "http://localhost:11434/v1",
            "api_key": "ollama",              # Ollama ignores this but the field is required
        }
    ],
    "temperature": 0.2,
}

# ---------------------------------------------------------------------------
# Pick whichever one you've configured and import LLM_CONFIG elsewhere.
# ---------------------------------------------------------------------------
LLM_CONFIG = OLLAMA_CONFIG
