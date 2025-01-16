from typing import List, Callable, Type
from abc import ABC, abstractmethod

class BaseBotModule(ABC):
    _registry: List[Type['BaseBotModule']] = []

    def __init_subclass__(cls, **kwargs):
        """Автоматически регистрируем всех наследников"""
        super().__init_subclass__(**kwargs)
        BaseBotModule._registry.append(cls)

    def __init__(self, base_reaction, actions: List[Callable]):
        self.module_id: str
        self.state: List[Callable] = actions
        self.reaction = base_reaction

    @abstractmethod
    def default(self, *args):
        pass

    @classmethod
    def initialize_all(cls):
        """Проходит по всем зарегистрированным наследникам и вызывает их конструктор"""
        instances = []
        for module in cls._registry:
            # Конструктор вызывается с параметрами, заданными наследником
            instance = module()
            instances.append(instance)
        return instances

# Пример наследника
class ExampleBotModule(BaseBotModule):
    module_id = "example"

    def __init__(self):
        super().__init__(base_reaction="ExampleReaction", actions=[self.default])

    def default(self, *args):
        print("Default action executed")

# Второй пример наследника
class AnotherBotModule(BaseBotModule):
    module_id = "another"

    def __init__(self):
        super().__init__(base_reaction="AnotherReaction", actions=[self.default])

    def default(self, *args):
        print("Another action executed")

# Инициализация всех модулей
instances = BaseBotModule.initialize_all()
print(f"Инициализированные модули: {[type(instance).__name__ for instance in instances]}")