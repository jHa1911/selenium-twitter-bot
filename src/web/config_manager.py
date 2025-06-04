import json
import os
from typing import Dict, Any

class ConfigManager:
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.default_config = {
            "bot_settings": {
                "SEARCH_QUERY": "latest news",
                "MAX_REPLIES_PER_DAY": 50,
                "MAX_REPLIES_PER_HOUR": 10,
                "MIN_DELAY_SECONDS": 60,
                "MAX_DELAY_SECONDS": 180,
                "ENABLE_AUTO_FOLLOW_BACK": True,
                "ENABLE_AUTO_LIKE_FOLLOWING": True,
                "MAX_FOLLOWS_PER_DAY": 20,
                "MAX_LIKES_PER_DAY": 100,
                "MAX_LIKES_PER_HOUR": 15
            },
            "bot_status": "stopped"
        }
        self.config = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    merged_config = self._merge_with_defaults(loaded_config)
                    return merged_config
            except (json.JSONDecodeError, Exception) as e:
                print(f"Error loading config: {e}")
                return self.default_config.copy()
        else:
            # Create default config file if it doesn't exist
            self.save_config(self.default_config)
            return self.default_config.copy()

    def _merge_with_defaults(self, loaded_config: Dict[str, Any]) -> Dict[str, Any]:
        """Merge loaded config with defaults to ensure all required keys exist"""
        merged = self.default_config.copy()

        # Deep merge bot_settings
        if 'bot_settings' in loaded_config:
            merged['bot_settings'].update(loaded_config['bot_settings'])

        # Update other top-level keys
        for key, value in loaded_config.items():
            if key != 'bot_settings':
                merged[key] = value

        return merged

    def save_config(self, config: Dict[str, Any]) -> bool:
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            # Update in-memory config after successful save
            self.config = config.copy()
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False

    def get_config(self) -> Dict[str, Any]:
        """Get current configuration"""
        return self.config.copy()

    def update_config(self, new_config: Dict[str, Any]) -> bool:
        """Update configuration with new values"""
        try:
            # Update in-memory config first
            updated_config = self.config.copy()

            # Deep update for nested dictionaries
            for key, value in new_config.items():
                if key in updated_config and isinstance(updated_config[key], dict) and isinstance(value, dict):
                    updated_config[key].update(value)
                else:
                    updated_config[key] = value

            # Save to file and update memory
            if self.save_config(updated_config):
                return True
            else:
                return False
        except Exception as e:
            print(f"Error updating config: {e}")
            return False

    def get_bot_settings(self) -> Dict[str, Any]:
        """Get only bot settings"""
        return self.config.get('bot_settings', {}).copy()

    def update_bot_settings(self, new_settings: Dict[str, Any]) -> bool:
        """Update only bot settings"""
        return self.update_config({'bot_settings': new_settings})

    def get_bot_status(self) -> str:
        """Get current bot status"""
        return self.config.get('bot_status', 'stopped')

    def set_bot_status(self, status: str) -> bool:
        """Set bot status"""
        return self.update_config({'bot_status': status})
