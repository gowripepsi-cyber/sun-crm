import os
import json
from pathlib import Path

DEFAULT_SETTINGS = {
    "company_name": "SUN CRM Enterprise",
    "company_address": "123 Business Road, Corporate Suite",
    "company_phone": "+91 98765 43210",
    "company_email": "contact@suncrm.com",
    "company_logo": "",
    "db_location": "data/suncrm.db",
    "documents_folder": "data/documents",
    "backup_folder": "data/backups",
    "theme": "Dark",  # "Dark" or "Light"
    "password_enabled": False,
    "password_hash": "",  # SHA-256 hash of password
    "auto_backup": True,
    "auto_backup_on_exit": True,
    "auto_backup_count": 5,
    "use_gdrive": False,
    "gdrive_credentials_path": "credentials.json"
}

class SettingsManager:
    def __init__(self, config_filename="settings.json"):
        self.workspace_dir = Path(__file__).parent.resolve()
        self.config_path = self.workspace_dir / config_filename
        self.settings = DEFAULT_SETTINGS.copy()
        self.load_settings()

    def get_default_path(self, key):
        """Resolves default path relative to workspace if needed."""
        default_val = DEFAULT_SETTINGS.get(key, "")
        if default_val and not os.path.isabs(default_val):
            return str(self.workspace_dir / default_val)
        return default_val

    def load_settings(self):
        try:
            if self.config_path.exists():
                with open(self.config_path, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    # Merge defaults for backward compatibility
                    for k, v in DEFAULT_SETTINGS.items():
                        if k not in loaded:
                            loaded[k] = v
                    self.settings = loaded
            else:
                self.save_settings()
        except Exception as e:
            print(f"Error loading settings: {e}")
            self.settings = DEFAULT_SETTINGS.copy()
        
        # Ensure directory structures exist for key paths
        self.ensure_directories()

    def save_settings(self):
        try:
            # Ensure folder containing settings file exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def get(self, key, default=None):
        val = self.settings.get(key, default)
        
        # If it is a path key and it is relative, make it absolute
        path_keys = ["db_location", "documents_folder", "backup_folder"]
        if key in path_keys and val:
            if not os.path.isabs(val):
                return str((self.workspace_dir / val).resolve())
        return val

    def set(self, key, value):
        self.settings[key] = value
        self.save_settings()
        if key in ["db_location", "documents_folder", "backup_folder"]:
            self.ensure_directories()

    def ensure_directories(self):
        """Ensures that DB, document, and backup folders exist."""
        for key in ["db_location", "documents_folder", "backup_folder"]:
            val = self.get(key)
            if val:
                path = Path(val)
                if key == "db_location":
                    path.parent.mkdir(parents=True, exist_ok=True)
                else:
                    path.mkdir(parents=True, exist_ok=True)

# Global settings instance
settings_mgr = SettingsManager()
