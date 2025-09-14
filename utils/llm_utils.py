"""
LLM utility functions for DeepCode project.

This module provides common LLM-related utilities to avoid circular imports
and reduce code duplication across the project.
"""

import os
import yaml
from typing import Any, Type, Dict, Tuple

# Import LLM classes
from mcp_agent.workflows.llm.augmented_llm_anthropic import AnthropicAugmentedLLM
from mcp_agent.workflows.llm.augmented_llm_openai import OpenAIAugmentedLLM
from mcp_agent.workflows.llm.augmented_llm_gemini import GeminiAugmentedLLM


def get_preferred_llm_class(config_path: str = "mcp_agent.secrets.yaml") -> Type[Any]:
    """
    Automatically select the LLM class based on API key availability in configuration.

    Reads from YAML config file and returns AnthropicAugmentedLLM if anthropic.api_key
    is available, otherwise returns OpenAIAugmentedLLM.

    Args:
        config_path: Path to the YAML configuration file

    Returns:
        class: The preferred LLM class
    """
    try:
        # Try to read the configuration file
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)

            # Check for gemini API key first
            gemini_config = config.get("gemini", {})
            gemini_key = gemini_config.get("api_key", "")

            if gemini_key and gemini_key.strip() and not gemini_key == "":
                return GeminiAugmentedLLM

            # Check for anthropic API key in config
            anthropic_config = config.get("anthropic", {})
            anthropic_key = anthropic_config.get("api_key", "")

            if anthropic_key and anthropic_key.strip() and not anthropic_key == "":
                # print("🤖 Using AnthropicAugmentedLLM (Anthropic API key found in config)")
                return AnthropicAugmentedLLM
            else:
                # print("🤖 Using OpenAIAugmentedLLM (Anthropic API key not configured)")
                return OpenAIAugmentedLLM
        else:
            print(f"🤖 Config file {config_path} not found, using OpenAIAugmentedLLM")
            return OpenAIAugmentedLLM

    except Exception as e:
        print(f"🤖 Error reading config file {config_path}: {e}")
        print("🤖 Falling back to OpenAIAugmentedLLM")
        return OpenAIAugmentedLLM


def get_default_models(config_path: str = "mcp_agent.config.yaml"):
    """
    Get default models from configuration file.

    Args:
        config_path: Path to the configuration file

    Returns:
        dict: Dictionary with 'anthropic' and 'openai' default models
    """
    try:
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)

            # Handle null values in config sections
            anthropic_config = config.get("anthropic") or {}
            openai_config = config.get("openai") or {}
            gemini_config = config.get("gemini") or {}

            anthropic_model = anthropic_config.get(
                "default_model", "claude-sonnet-4-20250514"
            )
            openai_model = openai_config.get("default_model", "o3-mini")
            gemini_model = gemini_config.get("default_model", "gemini-1.5-pro")

            return {"anthropic": anthropic_model, "openai": openai_model, "gemini": gemini_model}
        else:
            print(f"Config file {config_path} not found, using default models")
            return {"anthropic": "claude-sonnet-4-20250514", "openai": "o3-mini", "gemini": "gemini-1.5-pro"}

    except Exception as e:
        print(f"❌Error reading config file {config_path}: {e}")
        return {"anthropic": "claude-sonnet-4-20250514", "openai": "o3-mini", "gemini": "gemini-1.5-pro"}


def get_document_segmentation_config(
    config_path: str = "mcp_agent.config.yaml",
) -> Dict[str, Any]:
    """
    Get document segmentation configuration from config file.

    Args:
    ...