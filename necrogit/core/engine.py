import os
from typing import Dict, Any, Optional, List
import httpx
from necrogit.telemetry import trace_span, record_breadcrumb

SUPPORTED_MODELS: Dict[str, str] = {
    "gemma2:9b": "Google Gemma 2 9B (recommended default for code archaeology & reasoning)",
    "gemma2:2b": "Google Gemma 2 2B (ultra-lightweight local model for quick audits)",
    "gemma2:27b": "Google Gemma 2 27B (high-capacity deep architectural analysis)",
    "llama3.2:3b": "Meta Llama 3.2 3B (edge-optimized compact code model)",
    "llama3.1:8b": "Meta Llama 3.1 8B (generalist code synthesis)",
}

class InferenceError(Exception):
    """Base exception for all AI inference failures."""
    pass

class InferenceConnectionError(InferenceError):
    """Cannot reach the local inference server."""
    pass

class InferenceEndpointNotFoundError(InferenceError):
    """The inference endpoint was not found (HTTP 404)."""
    pass

class InferenceModelNotFoundError(InferenceError):
    """The requested model is not downloaded or available on the server."""
    pass

class InferenceTimeoutError(InferenceError):
    """Inference timed out."""
    pass

class InferenceResponseError(InferenceError):
    """Received malformed or unparseable response from the server."""
    pass

class SeanceEngine:
    """Offline LLM integration targeting local open-weight models (Gemma 2 / Llama 3 via Ollama / vLLM)."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        model: str = "gemma2:9b",
        timeout: float = 60.0
    ):
        raw_url = base_url or os.getenv("NECROGIT_OLLAMA_URL") or os.getenv("OLLAMA_BASE_URL") or "http://localhost:11434/v1"
        self.base_url = raw_url.rstrip("/")
        self.model = model
        self.timeout = timeout

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

    def check_health(self) -> Dict[str, Any]:
        """Check connection to local inference server and model availability."""
        endpoints = []
        if self.base_url.endswith("/v1"):
            base = self.base_url[:-3]
            endpoints = [f"{self.base_url}/models", f"{base}/api/tags"]
        else:
            endpoints = [f"{self.base_url}/v1/models", f"{self.base_url}/api/tags"]

        try:
            with httpx.Client(timeout=5.0) as client:
                for ep in endpoints:
                    try:
                        resp = client.get(ep)
                        if resp.status_code == 200:
                            data = resp.json()
                            model_names: List[str] = []
                            if "data" in data and isinstance(data["data"], list):
                                model_names = [m.get("id", "") for m in data["data"]]
                            elif "models" in data and isinstance(data["models"], list):
                                model_names = [m.get("name", "") for m in data["models"]]

                            model_found = any(self.model in m or m.startswith(self.model.split(":")[0]) for m in model_names)
                            return {
                                "connected": True,
                                "endpoint": ep,
                                "model_configured": self.model,
                                "model_found": model_found,
                                "available_models": model_names
                            }
                    except httpx.HTTPStatusError:
                        continue
            return {
                "connected": False,
                "error": f"No model discovery endpoint responded on {self.base_url}."
            }
        except httpx.ConnectError:
            return {
                "connected": False,
                "error": f"Cannot reach local inference server at {self.base_url}."
            }
        except Exception as e:
            return {
                "connected": False,
                "error": str(e)
            }

    def _dispatch(self, payload: Dict[str, Any]) -> str:
        """Execute request to local open-weight inference endpoint with automatic Ollama fallback."""
        if self.base_url.endswith("/v1"):
            primary_url = f"{self.base_url}/chat/completions"
            fallback_url = f"{self.base_url[:-3]}/api/chat"
        elif self.base_url.endswith("/api"):
            primary_url = f"{self.base_url}/chat"
            fallback_url = f"{self.base_url[:-4]}/v1/chat/completions"
        else:
            primary_url = f"{self.base_url}/v1/chat/completions"
            fallback_url = f"{self.base_url}/api/chat"

        try:
            with httpx.Client(timeout=self.timeout) as client:
                # 1. Try primary OpenAI-compatible endpoint
                try:
                    response = client.post(primary_url, json=payload)
                except httpx.ConnectError:
                    return (
                        f"💀 [Séance Severed]: Cannot reach local model at {self.base_url}.\n"
                        f"Ensure Ollama/vLLM is running locally: `ollama run {self.model}`"
                    )

                # 2. Check for 404 (endpoint not found or model not found)
                if response.status_code == 404:
                    err_text = response.text.lower()
                    if "model" in err_text and ("not found" in err_text or "does not exist" in err_text):
                        return (
                            f"💀 [Model Absent (404)]: Model '{self.model}' was not found in your local Ollama library.\n"
                            f"Run `ollama pull {self.model}` to download the model weights."
                        )

                    # Try native Ollama endpoint fallback
                    try:
                        ollama_payload = {
                            "model": payload["model"],
                            "messages": payload["messages"],
                            "stream": False,
                            "options": {"temperature": payload.get("temperature", 0.2)}
                        }
                        fallback_resp = client.post(fallback_url, json=ollama_payload)
                        if fallback_resp.status_code == 200:
                            fb_data = fallback_resp.json()
                            if "message" in fb_data and "content" in fb_data["message"]:
                                return fb_data["message"]["content"].strip()
                        elif fallback_resp.status_code == 404 and "model" in fallback_resp.text.lower():
                            return (
                                f"💀 [Model Absent (404)]: Model '{self.model}' was not found in your local Ollama library.\n"
                                f"Run `ollama pull {self.model}` to download the model weights."
                            )
                    except Exception:
                        pass

                    return (
                        f"💀 [Séance Severed (404 Not Found)]: Endpoint {primary_url} returned HTTP 404.\n"
                        f"Ensure Ollama is running and supports /v1/chat/completions or /api/chat. Check your --base-url parameter."
                    )

                response.raise_for_status()

                # Parse JSON response
                try:
                    data = response.json()
                except Exception:
                    return "💀 [Inference Error (Malformed Response)]: Invalid JSON returned from inference server."

                if "choices" in data and len(data["choices"]) > 0:
                    choice = data["choices"][0]
                    if "message" in choice and "content" in choice["message"]:
                        return choice["message"]["content"].strip()

                if "message" in data and "content" in data["message"]:
                    return data["message"]["content"].strip()

                return "💀 [Inference Error (Malformed Response)]: Response missing standard choices or message structure."

        except httpx.ConnectError:
            return (
                f"💀 [Séance Severed]: Cannot reach local model at {self.base_url}.\n"
                f"Ensure Ollama/vLLM is running locally: `ollama run {self.model}`"
            )
        except httpx.TimeoutException:
            return (
                f"💀 [Séance Severed (Timeout)]: Inference timed out after {self.timeout}s.\n"
                f"Try a more compact model: `necrogit patch --model gemma2:2b` or check local GPU/CPU load."
            )
        except httpx.HTTPStatusError as e:
            return f"💀 [Inference Error (HTTP {e.response.status_code})]: {e.response.text or str(e)}"
        except Exception as e:
            return f"💀 [Inference Error]: {str(e)}"
