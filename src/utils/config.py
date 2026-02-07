"""Configuration loader module.

Loads and validates configuration from YAML files and environment variables.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Default config file path
DEFAULT_CONFIG_PATH = Path(__file__).parent.parent.parent / "config" / "config.yaml"


class Config:
    """Application configuration manager.

    Loads configuration from a YAML file and merges with environment
    variables. Environment variables take precedence over file values.

    Args:
        config_path: Path to the YAML configuration file.

    Example:
        >>> config = Config()
        >>> model = config.get("llm.model")
        >>> api_key = config.get_env("OPENAI_API_KEY")
    """

    def __init__(self, config_path: Path | str = DEFAULT_CONFIG_PATH) -> None:
        self._config_path = Path(config_path)
        self._data: dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        """Load configuration from the YAML file."""
        if self._config_path.exists():
            with open(self._config_path) as f:
                self._data = yaml.safe_load(f) or {}
        else:
            self._data = {}

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value using dot notation.

        Args:
            key: Dot-separated key path (e.g., "llm.model").
            default: Default value if key is not found.

        Returns:
            The configuration value, or default if not found.

        Example:
            >>> config.get("llm.temperature")
            0.0
            >>> config.get("llm.nonexistent", "fallback")
            'fallback'
        """
        keys = key.split(".")
        value: Any = self._data
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
            if value is None:
                return default
        return value

    @staticmethod
    def get_env(key: str, default: str | None = None) -> str | None:
        """Get an environment variable.

        Args:
            key: Environment variable name.
            default: Default value if not set.

        Returns:
            The environment variable value, or default.
        """
        return os.getenv(key, default)

    @staticmethod
    def require_env(key: str) -> str:
        """Get a required environment variable.

        Args:
            key: Environment variable name.

        Returns:
            The environment variable value.

        Raises:
            EnvironmentError: If the variable is not set.
        """
        value = os.getenv(key)
        if value is None:
            raise EnvironmentError(f"Required environment variable '{key}' is not set")
        return value

    def reload(self) -> None:
        """Reload configuration from the file."""
        self._load()

    def as_dict(self) -> dict[str, Any]:
        """Return the full configuration as a dictionary."""
        return dict(self._data)
