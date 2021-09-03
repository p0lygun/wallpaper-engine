import logging
import sys

from colorama import Fore, Style


class LoggerClass:
    logger = None
    main = None
    prefix = "WE"
    section_color = Fore.RED
    app_color = Fore.LIGHTRED_EX

    def __init__(self, name: str, module: str = ""):
        if LoggerClass.logger is None:
            LoggerClass.logger = logging.getLogger(name)
            ch = logging.StreamHandler(sys.stdout)
            ch.setLevel(logging.DEBUG)
            formatter = logging.Formatter(
                f"{Fore.LIGHTBLACK_EX}{LoggerClass.prefix}{Style.RESET_ALL} %(message)s"
            )
            ch.setFormatter(formatter)
            LoggerClass.logger.addHandler(ch)
            LoggerClass.logger.setLevel(10)
            LoggerClass.logger.info(
                f"{Fore.GREEN}INFO {self.section_color}{LoggerClass.prefix}-logger{Style.RESET_ALL}: setting up"
            )
        self.module = module + ("-" if module else "")

    def debug(self, msg: str) -> None:
        """Passes msg to kv_logger."""
        msg = msg.split(":", maxsplit=1)
        if len(msg) == 1:
            self.logger.debug(
                f"{Fore.CYAN}DEBUG {self.app_color}{self.module}{Style.RESET_ALL} : {''.join(msg)}"
            )
        else:
            self.logger.debug(
                f"{Fore.CYAN}DEBUG {self.app_color}{self.module}{msg[0]}{Style.RESET_ALL}: {msg[1]}"
            )

    def info(self, msg: str) -> None:
        """Passes msg to kv_logger."""
        msg = msg.split(":", maxsplit=1)
        if len(msg) == 1:
            self.logger.info(
                f"{Fore.GREEN}INFO {self.app_color}{self.module}{Style.RESET_ALL} : {''.join(msg)}"
            )
        else:
            self.logger.info(
                f"{Fore.GREEN}INFO {self.app_color}{self.module}{msg[0]}{Style.RESET_ALL}: {msg[1]}"
            )

    def set_level(self, level: int):
        """set level for logger."""
        self.logger.setLevel(level)
