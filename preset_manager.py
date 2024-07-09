from pathlib import Path
import json

class PresetManager:
    def __init__(self):
        self.config_filename = "summary.config.json"

    def save_preset(self, root_directory: Path, preset_data):
        config_path = root_directory / self.config_filename
        config_path.write_text(json.dumps(preset_data, indent=4))
        print(f"Preset saved to {config_path}")

    def load_preset(self, root_directory: Path):
        config_path = root_directory / self.config_filename
        if config_path.exists():
            # add debug log here
            print(f"Preset loaded from {config_path}")
            text = config_path.read_text()
            print(f"Loaded text: {text}")
            json_data = json.loads(text)
            print(f"Loaded JSON: {json_data}")
            return json.loads(config_path.read_text())
        else:
            print(f"Preset file not found at {config_path}")
            return None