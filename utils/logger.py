import os
import logging
from threading import Lock
from typing import Optional
from rich.logging import RichHandler


class LoggerSingleton:
    __instance: Optional["LoggerSingleton"] = None
    __lock = Lock()
    DEFAULT_LOGGER_NAME = "DefaultLogger"

    def __new__(cls, *args, **kwargs) -> "LoggerSingleton":
        name = kwargs.pop("name", cls.DEFAULT_LOGGER_NAME)
        env = kwargs.pop("env", 'DEV')
        log_level = kwargs.pop("log_level", logging.INFO if env=="PROD" else logging.DEBUG)
        filename = kwargs.pop("filename", "app-prod.log" if env=="PROD" else "app-dev.log")
        with cls.__lock:
            if cls.__instance is None:
                cls.__instance = super().__new__(cls)
                cls.__instance.__setup_logger(name, log_level, filename, env)
            else:
                if name != cls.DEFAULT_LOGGER_NAME or log_level != logging.DEBUG:
                    cls.__instance.logger.warning("Logger already initialized. Ignoring new parameters.")
            return cls.__instance

    def __setup_logger(self, name: str, log_level: int, filename: str, env:  str) -> None:
        print("Setting up Logger...")
        print(f"env: {env}")
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level)
        if filename:
            logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                                filename=filename, encoding='utf-8', level=log_level)

        if not self.logger.handlers:  # Avoid duplicate handlers
            self.logger.addHandler(RichHandler(rich_tracebacks=True))

    def __getattr__(self, name: str):
        """Delegate attribute access to the underlying logger."""
        return getattr(self.logger, name)

    def info(self, msg: str, *args) -> None:
        self.logger.info(msg=msg, *args)

    def error(self, msg: str, *args) -> None:
        self.logger.error(msg=msg, *args)

    def debug(self, msg: str, *args) -> None:
        self.logger.debug(msg=msg, *args)

    def warning(self, msg: str, *args) -> None:
        self.logger.warning(msg=msg, *args)
        
LOGGER = LoggerSingleton(name="App-Logger", env=os.getenv('ENV', "DEV"))
