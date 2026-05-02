"""Cross-Device AI Integration Module for Cursor and VS Code.

This module provides a unified interface for AI-powered features across
Cursor IDE and Visual Studio Code using the local bridge server and Ollama models.

Key Features:
- Bridge server communication (validate, analyze, suggest, ollama)
- Ollama model management
- Cross-IDE configuration synchronization
- Shared AI context and prompt templates
"""

from .bridge_client import BridgeClient, CrossDeviceConfig

__version__ = "0.1.0"
__all__ = ["BridgeClient", "CrossDeviceConfig"]