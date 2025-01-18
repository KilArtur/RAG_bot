import importlib
import pkgutil
import re
from abc import ABC, abstractmethod
from typing import Type, Any, Callable, List, Dict

from sqlalchemy.util import ellipses_string
from telegram import Update
from telegram.ext import CallbackContext


class BaseBot(ABC):

    def __init__(self):
        self.all_modules = BaseInitBotModule._registry

    @abstractmethod
    def start(self):
        pass


class RequestContext(ABC):
    def __init__(self):
        self.chat_client_id: str
        self.state_registry: Dict[str, Type[Any]]
        self.action_registry: Dict[str, Type[Any]]
        self.update: Update
        self.context: CallbackContext


class BaseReaction(ABC):
    def __init__(self, request_context: RequestContext):
        self.request_context: RequestContext = request_context

    @abstractmethod
    def answer(self, answer: str, button: list):
        pass

    @abstractmethod
    def state(self, state: str):
        pass

    @abstractmethod
    def go(self):
        """Перейти в класс, сменить state"""
        pass


class BaseBotModule(ABC):
    def __init__(self, module_id: str, default_function: Callable, actions: List[Callable[[str], bool]] = None):
        self.module_id: str = module_id
        self.actions: List[Callable[[str], bool]] = actions if actions is not None else []
        self.default_function: Callable[[str], None] = default_function

    def callback(self, query: str):
        if any(action(query) for action in self.actions):
            return
        self.default_function(query)

class BaseInitBotModule(ABC):
    _registry = {}

    def __init_subclass__(cls, **kwargs):
        """Автоматически регистрируем всех наследников"""
        super().__init_subclass__(**kwargs)
        bot_class_module = cls()
        if bot_class_module.main_module is None:
            bot_class_module.create_main_module()
        BaseInitBotModule._registry[bot_class_module.main_module.module_id] = bot_class_module.main_module
        bot_modules = bot_class_module.get_modules()
        for module in bot_modules:
            BaseInitBotModule._registry[module.module_id] = module

    def __init__(self):
        self.callback = None
        self.module_id = None
        self.main_module = None
        self.bot_modules = []

    def get_modules(self)-> list[BaseBotModule]:
        if not self.bot_modules:
            raise "Init bot_modules"
        return self.bot_modules

    def create_main_module(self):
        if self.module_id is None:
            raise "Init module_id"
        if self.callback is None:
            raise "Init main callback"
        self.main_module = BaseBotModule(self.module_id, self.callback)


    def state(self, state: str, callback: Callable):
        self.bot_modules.append(BaseBotModule(state, callback))

    def regex(self, pattern: str, callback: Callable):
        def wrapper(query: str):
            if re.match(pattern, query):
                callback(query)
                return True
            return False
        if self.module_id is not None:
            self.create_main_module()
        self.main_module.actions.append(wrapper)