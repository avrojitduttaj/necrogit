from typing import Dict, Any, Optional
import httpx
from necrogit.telemetry import trace_span, record_breadcrumb

SUPPORTED_MODELS = {
    "gemma2:9b": "Google Gemma 2 9B (recommended default for code archaeology & reasoning)",
    "gemma2:2b": "Google Gemma 2 2B (ultra-lightweight local model for quick audits)",
    "gemma2:27b": "Google Gemma 2 27B (high-capacity deep architectural analysis)",
    "llama3.2:3b": "Meta Llama 3.2 3B (edge-optimized compact code model)",
    "llama3.1:8b": "Meta Llama 3.1 8B (generalist code synthesis)",
}

class SeanceEngine:
    """Offline LLM integration targeting local open-weight models (Gemma 2 / Llama 3 via Ollama / vLLM)."""

    def __init__(self, base_url: str = "http://localhost:11434/v1", model: str = "gemma2:9b"):
        self.base_url = base_url.rstrip("/")
        self.model = model

    def consult_ghost(self, persona: Dict[str, Any], snippet: str, context: str) -> str:
        """Channel the maintainer spirit through local LLM inference to draft a resurrective diff."""
        with trace_span("necrogit.llm", "consult_ghost", {
            "gen_ai.system": "ollama",
            "gen_ai.request.model": self.model,
            "maintainer": persona.get("maintainer", "unknown"),
        }):
            record_breadcrumb("llm", f"Channelling patch with {self.model}", data={"maintainer": persona.get("maintainer")})

            maintainer_name = persona.get("maintainer", "an open-source hacker")
            last_active = persona.get("last_active", "Time immemorial")
            brevity = persona.get("brevity", "laconic")

            system_prompt = (
                f"You are the digital ghost of {maintainer_name}. "
                f"Your last verified commit was on {last_active}. "
                f"Your natural communication style is {brevity}.\n\n"
                "Task: Modernize and repair the deprecated or broken Python code provided below. "
                "Channel your original coding personality: strictly preserve your legacy naming conventions, "
                "variable casing, and comment cadence while upgrading to modern standard Python equivalents. "
                "Output ONLY a valid unified diff (starting with `---` and `+++`) without preamble or conversational filler."
            )

            user_prompt = (
                f"Legacy Code Snippet:\n```python\n{snippet}\n```\n\n"
                f"Detected Bitrot Context:\n{context}\n\n"
                "Produce the unified diff to resurrect this file:"
            )

            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.2
            }

            return self._dispatch(payload)

    def explain_design(self, persona: Dict[str, Any], snippet: str, symbol_query: Optional[str] = None) -> str:
        """Channel the maintainer to explain obscure historical design choices and legacy architecture."""
        with trace_span("necrogit.llm", "explain_design", {
            "gen_ai.system": "ollama",
            "gen_ai.request.model": self.model,
            "symbol": symbol_query or "file",
        }):
            record_breadcrumb("llm", f"Explaining historical design with {self.model}", data={"symbol": symbol_query})

            maintainer_name = persona.get("maintainer", "the original architect")
            last_active = persona.get("last_active", "Time immemorial")
            brevity = persona.get("brevity", "balanced")

            system_prompt = (
                f"You are the original software architect and maintainer {maintainer_name}. "
                f"Your primary active development era culminated around {last_active}. "
                f"Your voice is {brevity}, authoritative, and deeply knowledgeable about the historical "
                "constraints of earlier Python versions, operating systems, and vintage hardware limits.\n\n"
                "Task: Unpack and explain the obscure historical design choices, idiosyncrasies, "
                "and architectural trade-offs in the code snippet provided below. "
                "Explain WHY it was written this way at the time (e.g. pre-PEP standards, thread model quirks, "
                "C-extension bridges, or Python 2/3 transitions) and provide your ghostly blessing for how to modernize it."
            )

            symbol_spec = f"Focus particularly on `{symbol_query}`." if symbol_query else "Analyze the module architecture."
            user_prompt = (
                f"Historic Code Artifact:\n```python\n{snippet}\n```\n\n"
                f"{symbol_spec}\n"
                "Explain the historical rationale and modern refactoring guidance:"
            )

            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.3
            }

            return self._dispatch(payload)

    def _dispatch(self, payload: Dict[str, Any]) -> str:
        """Execute post request to local open-weight inference endpoint."""
        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(f"{self.base_url}/chat/completions", json=payload)
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"].strip()
        except httpx.ConnectError:
            return (
                f"💀 [Séance Severed]: Cannot reach local model at {self.base_url}.\n"
                f"Ensure Ollama/vLLM is running locally: `ollama run {self.model}`"
            )
        except Exception as e:
            return f"💀 [Inference Error]: {str(e)}"
