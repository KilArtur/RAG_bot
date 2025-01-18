# from typing import ClassVar, Tuple
#
#
# class BaseBotModule:
#     subclasses: dict[str, ClassVar] = ()
#
#     def __init__(self, status_name):
#         self.status_name = status_name
#
#     def __init_subclass__(cls, **kwargs):
#         super().__init_subclass__(**kwargs)
#         BaseBotModule.subclasses = BaseBotModule.subclasses + (cls,)
#
#
#
#
from typing import ClassVar, Type, Dict, Any


# Базовый класс для модулей
class BaseBotModule:
    subclasses: Dict[str, Type["BaseBotModule"]] = {}

    def __init__(self, status_name: str, user_data: Dict[str, Any], chat_data: Dict[str, Any]):
        self.status_name = status_name
        self.user_data = user_data
        self.chat_data = chat_data

    def handle(self):
        """Основная логика обработки (переопределяется в подклассах)"""
        raise NotImplementedError("Этот метод должен быть переопределён в подклассах")

    @classmethod
    def __init_subclass__(cls, **kwargs):
        """Регистрация подклассов в словаре subclasses"""
        super().__init_subclass__(**kwargs)
        if hasattr(cls, "status_name") and isinstance(cls.status_name, str):
            BaseBotModule.subclasses[cls.status_name] = cls


# Пример подклассов
class GreetingModule(BaseBotModule):
    status_name = "greeting"

    def handle(self):
        return f"Привет, {self.user_data.get('name', 'гость')}! Это приветственное сообщение."


class FarewellModule(BaseBotModule):
    status_name = "farewell"

    def handle(self):
        return f"До свидания, {self.user_data.get('name', 'гость')}! Надеюсь, увидимся снова."


# Класс для управления ботом
class BotClass:
    def __init__(self, db: Dict[int, Dict[str, Any]]):
        """Инициализация бота с передачей базы данных"""
        self.db = db

    def create_user_module(self, user_id: int, chat_id: int, user_state: str):
        """Создание модуля для пользователя"""
        user_data = self.db.get(user_id, {})
        chat_data = {"chat_id": chat_id}

        module_class = BaseBotModule.subclasses.get(user_state)
        if not module_class:
            raise ValueError(f"Модуль для состояния '{user_state}' не найден.")

        return module_class(user_state, user_data, chat_data)


# Пример использования
if __name__ == "__main__":
    # Пример базы данных
    db = {
        1: {"name": "Алексей", "age": 30},
        2: {"name": "Мария", "age": 25},
    }

    bot = BotClass(db=db)

    # Создаём модуль для пользователя с состоянием "greeting"
    user_module = bot.create_user_module(user_id=1, chat_id=123, user_state="greeting")
    print(user_module.handle())  # Привет, Алексей! Это приветственное сообщение.

    # Создаём модуль для пользователя с состоянием "farewell"
    user_module = bot.create_user_module(user_id=2, chat_id=456, user_state="farewell")
    print(user_module.handle())  # До свидания, Мария! Надеюсь, увидимся снова.



