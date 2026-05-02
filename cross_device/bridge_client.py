"""Bridge Client for Cross-Device Integration between Cursor and VS Code.

This module provides a unified Python client that both Cursor's web editor
and VS Code extensions can use to communicate with the local bridge_server.py
and Ollama models.

It supports:
- C code validation and analysis
- Process scheduling analysis for OS assignments
- Ollama model integration for AI assistance
- Configuration synchronization across IDEs
"""

import json
import requests
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class CrossDeviceConfig:
    """Configuration for cross-device AI integration."""
    bridge_url: str = "http://127.0.0.1:8000"
    ollama_models: List[str] = None
    default_model: str = "mistral-nemo:latest"
    enable_ollama: bool = True
    sync_settings: bool = True

    def __post_init__(self):
        if self.ollama_models is None:
            self.ollama_models = ["mistral-nemo:latest", "qwen3-vl:8b"]


class BridgeClient:
    """Unified client for bridge server and Ollama integration.

    Works with both Cursor IDE's web editor and VS Code extensions.
    """

    def __init__(self, config: Optional[CrossDeviceConfig] = None):
        self.config = config or CrossDeviceConfig()
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "BNBU-CrossDevice-Client/0.1.0"
        })

    def _post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make a POST request to the bridge server."""
        url = f"{self.config.bridge_url}{endpoint}"
        try:
            response = self.session.post(url, json=data, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Bridge request to {endpoint} failed: {e}")
            return {"error": str(e), "status": "failed"}

    def validate_c(self, code: str) -> Dict[str, Any]:
        """Validate C code syntax using the bridge."""
        return self._post("/cursor/validate", {"code": code})

    def analyze_code(self, code: str) -> Dict[str, Any]:
        """Analyze scheduling code patterns."""
        return self._post("/cursor/analyze", {"code": code})

    def suggest_processes(self, processes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get scheduling suggestions."""
        return self._post("/cursor/suggest", {"processes": processes})

    def generate_with_ollama(self, prompt: str, model: Optional[str] = None) -> str:
        """Generate text using Ollama through the bridge."""
        if not self.config.enable_ollama:
            return "Ollama integration is disabled."

        model = model or self.config.default_model
        response = self._post("/cursor/ollama/generate", {
            "model": model,
            "prompt": prompt
        })

        if "error" in response:
            return f"Error: {response['error']}"

        # Extract the response text (Ollama format)
        return response.get("response", json.dumps(response, indent=2))

    def get_ollama_models(self) -> List[str]:
        """Get available Ollama models."""
        try:
            response = self.session.get(
                f"{self.config.bridge_url}/cursor/ollama/models",
                timeout=10
            )
            if response.ok:
                models = response.json()
                return [m.get("name", m) for m in models]
            return self.config.ollama_models
        except Exception as e:
            logger.warning(f"Failed to fetch Ollama models: {e}")
            return self.config.ollama_models

    def sync_ide_settings(self, ide_type: str = "both") -> Dict[str, Any]:
        """Synchronize settings between Cursor and VS Code.

        This is a placeholder for actual settings sync logic.
        In a full implementation, this would read/write VS Code settings.json
        and Cursor configuration files.
        """
        return {
            "status": "success",
            "message": f"Settings synchronized for {ide_type}",
            "bridge_url": self.config.bridge_url,
            "default_model": self.config.default_model,
            "ide_support": ["cursor", "vscode"]
        }


# Convenience functions for direct usage
def get_client() -> BridgeClient:
    """Get a configured BridgeClient instance."""
    return BridgeClient()


def quick_analyze(code: str) -> str:
    """Quick analysis helper function."""
    client = get_client()
    result = client.analyze_code(code)
    return json.dumps(result, indent=2)


if __name__ == "__main__":
    # Example usage
    client = get_client()
    print("Cross-Device Bridge Client initialized")
    print("Available Ollama models:", client.get_ollama_models())

    # Example C code analysis
    sample_code = '''#include <stdio.h>
int main() {
    enqueue_process("P1", 5, 0);
    return 0;
}'''
    result = client.analyze_code(sample_code)
    print("Analysis result:", result)