"""
Configuration Manager for the Engineering Freelance AI Agent.
"""

import json
import os
import urllib.request
import urllib.error
from pathlib import Path
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class ConfigManager:
    """
    Manages configuration for the engineering intake system.
    Loads from JSON config file with environment variable fallback.
    """
    
    DEFAULT_CONFIG = {
        "llm": {
            "provider": "openai",
            "base_url": "",
            "api_key": "",
            "model": "gpt-4o-mini"
        },
        "engineering": {
            "default_safety_factor": 2.5,
            "default_concrete_grade": "M25",
            "default_steel_grade": "Fe415"
        },
        "compliance": {
            "require_audit_log": True,
            "require_human_approval": True,
            "engineer_name": "",
            "engineer_license": ""
        },
        "code_resolver": {
            "confidence_threshold": 0.7
        }
    }
    
    def __init__(self, config_path: str = "data/config.json"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file with defaults"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    user_config = json.load(f)
                return self._merge_with_defaults(user_config)
            except (json.JSONDecodeError, IOError):
                pass
        return self.DEFAULT_CONFIG.copy()
    
    def _merge_with_defaults(self, user_config: Dict[str, Any]) -> Dict[str, Any]:
        """Merge user config with defaults"""
        merged = self.DEFAULT_CONFIG.copy()
        for key, value in user_config.items():
            if isinstance(value, dict) and key in merged:
                merged[key] = {**merged[key], **value}
            else:
                merged[key] = value
        return merged
    
    def save_config(self) -> None:
        """Save current configuration to file"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    # LLM Configuration
    
    def get_llm_provider(self) -> str:
        """Get LLM provider"""
        return os.getenv("LLM_PROVIDER", self.config.get("llm", {}).get("provider", "openai"))
    
    def get_llm_base_url(self) -> str:
        """Get LLM base URL (for OpenRouter/custom endpoints)"""
        return os.getenv("LLM_BASE_URL", self.config.get("llm", {}).get("base_url", ""))
    
    def get_llm_api_key(self) -> str:
        """Get LLM API key"""
        return os.getenv("LLM_API_KEY", self.config.get("llm", {}).get("api_key", ""))
    
    def get_llm_model(self) -> str:
        """Get LLM model name"""
        return os.getenv("LLM_MODEL", self.config.get("llm", {}).get("model", "gpt-4o-mini"))
    
    def set_llm_config(self, provider: str, base_url: str, api_key: str, model: str) -> None:
        """Set LLM configuration"""
        if "llm" not in self.config:
            self.config["llm"] = {}
        self.config["llm"]["provider"] = provider
        self.config["llm"]["base_url"] = base_url
        self.config["llm"]["api_key"] = api_key
        self.config["llm"]["model"] = model
        self.save_config()
    
    @staticmethod
    def fetch_models_from_base_url(base_url: str, api_key: str) -> List[str]:
        """
        Fetch list of model ids from an OpenAI-compatible /models endpoint
        (e.g. OpenRouter GET https://openrouter.ai/api/v1/models).
        Returns list of model id strings, or empty list on error.
        """
        if not base_url or not api_key:
            return []
        url = base_url.rstrip("/") + "/models"
        req = urllib.request.Request(
            url,
            headers={"Authorization": f"Bearer {api_key}"},
            method="GET",
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode())
        except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, OSError):
            return []
        items = data.get("data") if isinstance(data, dict) else None
        if not isinstance(items, list):
            return []
        ids = []
        for m in items:
            if isinstance(m, dict) and m.get("id"):
                ids.append(str(m["id"]))
        return ids

    def is_llm_configured(self) -> bool:
        """Check if LLM is properly configured"""
        api_key = self.get_llm_api_key()
        return bool(api_key and api_key != "your_api_key_here")
    
    # Engineering Configuration
    
    def get_safety_factor(self) -> float:
        """Get default safety factor"""
        return float(os.getenv("DEFAULT_SAFETY_FACTOR", 
                              self.config.get("engineering", {}).get("default_safety_factor", 2.5)))
    
    def get_concrete_grade(self) -> str:
        """Get default concrete grade"""
        return os.getenv("DEFAULT_CONCRETE_GRADE", 
                         self.config.get("engineering", {}).get("default_concrete_grade", "M25"))
    
    def get_steel_grade(self) -> str:
        """Get default steel grade"""
        return os.getenv("DEFAULT_STEEL_GRADE", 
                         self.config.get("engineering", {}).get("default_steel_grade", "Fe415"))
    
    # Compliance Configuration
    
    def get_engineer_name(self) -> str:
        """Get engineer name"""
        return os.getenv("ENGINEER_NAME", 
                         self.config.get("compliance", {}).get("engineer_name", ""))
    
    def get_engineer_license(self) -> str:
        """Get engineer license number"""
        return os.getenv("ENGINEER_LICENSE", 
                         self.config.get("compliance", {}).get("engineer_license", ""))
    
    def require_audit_log(self) -> bool:
        """Check if audit logging is required"""
        env_val = os.getenv("REQUIRE_AUDIT_LOG")
        if env_val:
            return env_val.lower() in ("true", "1", "yes")
        return self.config.get("compliance", {}).get("require_audit_log", True)
    
    def require_human_approval(self) -> bool:
        """Check if human approval is required"""
        env_val = os.getenv("REQUIRE_HUMAN_APPROVAL")
        if env_val:
            return env_val.lower() in ("true", "1", "yes")
        return self.config.get("compliance", {}).get("require_human_approval", True)
    
    # Code Resolver Configuration
    
    def get_confidence_threshold(self) -> float:
        """Get code confidence threshold"""
        return float(os.getenv("CODE_CONFIDENCE_THRESHOLD", 
                              self.config.get("code_resolver", {}).get("confidence_threshold", 0.7)))
    
    # Create LLM Client
    
    def create_llm_client(self):
        """Create and return an LLM client based on current configuration"""
        provider = self.get_llm_provider()
        api_key = self.get_llm_api_key()
        base_url = self.get_llm_base_url()
        
        if not api_key or api_key == "your_api_key_here":
            return None
        
        try:
            if provider == "openai":
                from openai import OpenAI
                client_kwargs = {"api_key": api_key}
                if base_url:
                    client_kwargs["base_url"] = base_url
                return OpenAI(**client_kwargs)
            
            elif provider == "anthropic":
                import anthropic
                return anthropic.Anthropic(api_key=api_key)
            
            elif provider == "custom" and base_url:
                # For OpenRouter or other compatible APIs
                from openai import OpenAI
                return OpenAI(base_url=base_url, api_key=api_key)
        
        except ImportError:
            return None
        except Exception:
            return None
        
        return None
    
    # Full config access
    
    def get_all_config(self) -> Dict[str, Any]:
        """Get all configuration"""
        return self.config.copy()
    
    def get_masked_config(self) -> Dict[str, Any]:
        """Get configuration with sensitive data masked"""
        config = self.get_all_config()
        if "llm" in config and "api_key" in config["llm"]:
            api_key = config["llm"]["api_key"]
            if api_key:
                config["llm"]["api_key"] = api_key[:4] + "****" + api_key[-4:] if len(api_key) > 8 else "****"
        return config


# Global instance
_config_manager = None

def get_config_manager(config_path: str = "data/config.json") -> ConfigManager:
    """Get or create the global configuration manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager(config_path)
    return _config_manager
