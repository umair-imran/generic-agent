from typing import Any
from pathlib import Path
import yaml

def load_yaml(path: str) -> dict[str, Any]:
    file_path = Path(path)
    if not file_path.is_file():
        raise FileNotFoundError(f"The YAML file at {path} was not found.")

    with open(file_path, "r") as file:
        data = yaml.safe_load(file)
        
    return data or {}