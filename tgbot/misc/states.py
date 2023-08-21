from aiogram.dispatcher.filters.state import State, StatesGroup


class Start(StatesGroup):
    get_name = State()
    get_number = State()


class Menu(StatesGroup):
    get_menu = State()


class Bonus(StatesGroup):
    get_code = State()


class Settings(StatesGroup):
    get_type = State()
    get_phone = State()


class Comment(StatesGroup):
    get_comment = State()


class News(StatesGroup):
    get_news = State()


class Prods(StatesGroup):
    get_prod = State()
    get_mm = State()
    get_count = State()
    get_conf = State()
