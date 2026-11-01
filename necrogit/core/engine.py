from typing import Dict, Any
import httpx
from necrogit.telemetry import trace_span

class SeanceEngine:
    """Offline LLM integration targeting local open-weight models (Ollama / vLLM / llama.cpp)."""

    def __init__(self, base_url: str = "http://localhost:11434/v1", model: str = "gemma2:9b"):
        self.base_url = base_url.rstrip("/")
        self.model = model

    def consult_ghost(self, persona: Dict[str, Any], snippet: str, context: str) -> str:
        """Channel the maintainer spirit through local LLM inference to draft a resurrective diff."""
        with trace_span("necrogit.llm", "consult_ghost"):
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
