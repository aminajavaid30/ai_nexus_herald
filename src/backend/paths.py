import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ENV_FPATH = os.path.join(ROOT_DIR, ".env")

CODE_DIR = os.path.join(ROOT_DIR, "src")

APP_CONFIG_FPATH = os.path.join(ROOT_DIR, "backend", "config", "config.yaml")
PROMPT_CONFIG_FPATH = os.path.join(ROOT_DIR, "backend", "config", "prompt_config.yaml")
RSS_CONFIG_FPATH = os.path.join(ROOT_DIR, "backend", "config", "rss_config.yaml")

OUTPUTS_DIR = os.path.join(ROOT_DIR, "outputs")