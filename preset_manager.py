from pathlib import Path
import json
from logging_config import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)

class PresetManager:
    def __init__(self):
        self.config_filename = "summary.config.json"

    def save_preset(self, root_directory: Path, preset_data):
        config_path = root_directory / self.config_filename
        config_path.write_text(json.dumps(preset_data, indent=4))
        logger.info(f"Preset saved to {config_path}")

    def load_preset(self, root_directory: Path):
        config_path = root_directory / self.config_filename
        if config_path.exists():
            return json.loads(config_path.read_text())
        else:
            logger.info(f"Preset file not found at {config_path}")
            return None