from oscpy.server import OSCThreadServer
from loguru import logger

from ..utils.config import Config


class OscHighway:
    config = Config(local=True, module="OscHighway")

    def __init__(self, name: str):
        if name not in ["wallpaper", "menu"]:
            raise ValueError("Invalid name for OSC instance")
        logger.debug(f"Init OSC for {name}")
        self.server = OSCThreadServer()
        self.sections = ["wallpaper", "menu"]
        self.name = name

    def getaddress(self):
        return self.server.getaddress()

    def start(self):
        self.server.listen(default=True)
        if self.config.config.sections() != self.sections:
            self.config.config.setdefaults(
                "menu",
                {
                    "port": self.server.getaddress()[1],
                },
            )
            self.config.config.setdefaults(
                "wallpaper",
                {
                    "port": -1,
                },
            )
        logger.debug(f"OSC-{self.name} : server up on {self.server.getaddress()}")
        self.save_to_config()

    def stop(self):
        logger.debug("Stopping Server ")
        self.server.stop_all()

    def send_message(
        self, osc_address: bytes, msg: [list, int, float, bytes], log=True
    ):
        if log:
            logger.debug(
                f"sending {osc_address.decode('utf-8')}, {msg}, {self.get_other_port()}"
            )

        if type(msg) == list:
            self.server.send_message(
                osc_address, msg, "localhost", self.get_other_port()
            )
        else:
            self.server.send_message(
                osc_address, [msg], "localhost", self.get_other_port()
            )

    def save_to_config(self):
        self.config.config.set(f"{self.name}", "port", self.server.getaddress()[1])
        self.config.write()

    def get_other_port(self):
        self.config.reload()
        if self.name == "wallpaper":
            return int(self.config.config.get("menu", "port"))
        return int(self.config.config.get("wallpaper", "port"))
