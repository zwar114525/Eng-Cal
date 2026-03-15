"""Tests for configuration manager"""

import pytest
import json
import os
from pathlib import Path
from config.manager import ConfigManager


class TestConfigManager:
    def test_default_config(self):
        config = ConfigManager(config_path="data/test_config.json")
        assert config.get_llm_provider() == "openai"
        assert config.get_llm_model() == "gpt-4o-mini"
    
    def test_set_llm_config(self, tmp_path):
        config_path = tmp_path / "config.json"
        config = ConfigManager(config_path=str(config_path))
        
        config.set_llm_config("openai", "https://api.openrouter.ai/v1", "test-key-123", "gpt-4o")
        
        assert config.get_llm_provider() == "openai"
        assert config.get_llm_base_url() == "https://api.openrouter.ai/v1"
        assert config.get_llm_api_key() == "test-key-123"
    
    def test_masked_config(self, tmp_path):
        config_path = tmp_path / "config.json"
        config = ConfigManager(config_path=str(config_path))
        
        config.set_llm_config("openai", "", "1234567890", "gpt-4o")
        
        masked = config.get_masked_config()
        assert "****" in masked["llm"]["api_key"]
