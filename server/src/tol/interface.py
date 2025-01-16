import importlib
import pkgutil
from abc import ABC, abstractmethod
from typing import Type, Any, Callable, List, Dict
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
    def __init__(self, module_id, callback: Callable, action: list[Callable[[str], bool]] = None):
        self.module_id: str = module_id
        self.callback: Callable = callback
        self.action = action

class BaseInitBotModule(ABC):
    _registry = {}

    def __init__(self):
        self.bot_modules = []

    def __init_subclass__(cls, **kwargs):
        """Автоматически регистрируем всех наследников"""
        super().__init_subclass__(**kwargs)
        bot_modules: BaseBotModule = cls().get_module()
        for module in bot_modules:
            BaseInitBotModule._registry[module.module_id] = module

    def get_module(self)-> list[BaseBotModule]:
        if not self.bot_modules:
            raise "Init bot_modules"
        return self.bot_modules

    # @property
    # def registry(self):
    #     return self._registry