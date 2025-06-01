import json
import os
from typing import Dict, Any

class ConfigManager:
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.default_config = {
            "bot_settings": {
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
        self.load_config()

    def load_config(self) -> Dict[str, Any]:
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return self.default_config
        else:
            self.save_config(self.default_config)
            return self.default_config

    def save_config(self, config: Dict[str, Any]) -> bool:
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False

    def get_config(self) -> Dict[str, Any]:
        return self.load_config()

    def update_config(self, new_config: Dict[str, Any]) -> bool:
        current_config = self.load_config()
        current_config.update(new_config)
        return self.save_config(current_config)
