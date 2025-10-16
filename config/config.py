from typing import Optional
from pathlib import Path

from pydantic_settings import BaseSettings
from pydantic import BaseModel, model_validator

from utils.logger import LOGGER
from utils import load_yaml

def load():    
    LOGGER.info("Attempting to load from .env.{PROD | LOCAL} file")
    # 1. Try local .env
    env_file_prod = Path(".env.prod")
    env_file_local = Path(".env.local")
    if env_file_prod.exists() | env_file_local.exists():
        return

    raise Exception('Unable to load secrets')

class OpenAISettings(BaseSettings):
    OPENAI_API_KEY: str
    class Config:
        env_file = '.env.prod', '.env.local'
        extra = "ignore"

    @classmethod
    def load(cls) -> "OpenAISettings":
        secrets = load()
        if secrets:
            return cls(**secrets)
        else:
            return cls()

class LLMSettings(BaseModel):
    model: str
    temperature: float
    __settings: Optional[OpenAISettings] = None
    verbose: bool = True

    @model_validator(mode="after")
    def check_keys(self):
        if not self.API_KEY:
            raise ValueError("OPENAI_API_KEY is required!")
        return self

    @property
    def API_KEY(self):
        if not self.__settings:
            self.__settings = OpenAISettings.load()
        return self.__settings.OPENAI_API_KEY

    

class ApplicationSettings(BaseModel):
    llm: LLMSettings

    @classmethod
    def from_cfg(cls, cfg: str | dict) -> "ApplicationSettings":
        if isinstance(cfg, str):
            cfg = load_yaml(cfg)
        return cls(**cfg)