
import os
import json

class PresetManager:
    def __init__(self):
        self.config_filename = "summary.config.json"

    def save_preset(self, root_directory, preset_data):
        config_path = os.path.join(root_directory, self.config_filename)
        with open(config_path, 'w') as f:
            json.dump(preset_data, f, indent=4)
        print(f"Preset saved to {config_path}")

    def load_preset(self, root_directory):
        config_path = os.path.join(root_directory, self.config_filename)
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
        else:
            print(f"Preset file not found at {config_path}")
            return None