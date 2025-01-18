import importlib
import pkgutil

from tol.interface import BaseBot, BaseInitBotModule, BaseBotModule


class MyBot(BaseBot):

    def start(self):
        print("Bot started")
        self.all_modules["/login"].callback("Что то")
        self.all_modules["/auth"].callback("Что то тут")
        self.all_modules["/outlog"].callback("Oleg")
        self.all_modules["/auth"].callback("Привет ааААаааААА")


    @staticmethod
    def initialize_modules(folder_path: str, package_name: str):
        for _, module_name, _ in pkgutil.iter_modules([folder_path]):
            full_module_name = f"{package_name}.{module_name}"
            importlib.import_module(full_module_name)

class MyModule(BaseInitBotModule):



    def __init__(self) -> BaseBotModule:
        super().__init__()
        self.module_id = "/auth"
        self.callback = lambda x: print(x)
        self.state("/login", self.login)
        self.state("/outlog", lambda x: print(f"вышел из аккаунта {x}"))
        self.regex(r"\bПривет\b", lambda x: print(f"Привет пользователь {x}!"))
        self.regex(r"\bПривет\b", lambda x, y: Action(y).dd(x))


    @staticmethod
    def login(query):
        print("oleg")

class Action:

    def __init__(self, res):
        self.reg = res

    def dd(self, query: str):
        print(f"{self.reg} JK {query}")


if __name__ == "__main__":
    bot = MyBot()
    bot.start()