from pathlib import Path

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def load_params(path: str = "params.yaml") -> dict:
    params_path = PROJECT_ROOT / path

    with open(params_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def get_project_root() -> Path:
    return PROJECT_ROOT