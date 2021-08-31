import logging

from colorama import Fore, Style
from kivy.logger import LOG_LEVELS


class LoggerClass:

    def __init__(self):
        self.prefix = "WE"
        self.section_color = Fore.RED
        self.logger = logging.getLogger(__name__)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter(f"%(message)s")
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)
        self.logger.info(f"{Fore.GREEN}INFO {self.section_color}{self.prefix}-logger{Style.RESET_ALL}: setting up")

    def debug(self, msg: str) -> None:
        """Passes msg to kv_logger."""
        msg = msg.split(":", maxsplit=1)
        if len(msg) == 1:
            self.logger.debug(f"{Fore.CYAN}DEBUG {self.section_color}{self.prefix}{Style.RESET_ALL}: {''.join(msg)}")
        else:
            self.logger.debug(f"{Fore.CYAN}DEBUG {self.section_color}{self.prefix}-{msg[0]}{Style.RESET_ALL}: {msg[1]}")

    def info(self, msg: str) -> None:
        """Passes msg to kv_logger."""
        msg = msg.split(":", maxsplit=1)
        if len(msg) == 1:
            self.logger.info(f"{Fore.GREEN}INFO {self.section_color}{self.prefix}{Style.RESET_ALL}: {''.join(msg)}")
        else:
            self.logger.info(f"{Fore.GREEN}INFO {self.section_color}{self.prefix}-{msg[0]}{Style.RESET_ALL}: {msg[1]}")

    def set_level(self, level: int):
        """set level for logger."""
        self.logger.setLevel(level)


Logger = LoggerClass()
