import importlib
import pkgutil

from tol.interface import BaseBot, BaseInitBotModule, BaseBotModule


class MyBot(BaseBot):

    def start(self):
        print("Bot started")
        self.all_modules["/login"].callback("")

    @staticmethod
    def initialize_modules(folder_path: str, package_name: str):
        for _, module_name, _ in pkgutil.iter_modules([folder_path]):
            full_module_name = f"{package_name}.{module_name}"
            importlib.import_module(full_module_name)



class MyModule(BaseInitBotModule):
    def __init__(self) -> BaseBotModule:
        super().__init__()

        self.bot_modules.append(BaseBotModule(module_id="/login", callback=self.login))

    @staticmethod
    def login(query):
        print("oleg")


if __name__ == "__main__":
    bot = MyBot()
    bot.start()