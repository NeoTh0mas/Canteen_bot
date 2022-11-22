<<<<<<< HEAD
from aiogram.dispatcher.filters.state import State, StatesGroup


class GeneralStates(StatesGroup):
    settings = State()
    select_lang = State()


class OrderFood(StatesGroup):
    init = State()
    on_menu = State()
    waiting_for_food = State()
    confirm = State()
    continue_or_order = State()
    order_food = State()
    payment = State()
    edit_cart = State()


class ReserveTable(StatesGroup):
    select_table = State()


class Registration(StatesGroup):
    course = State()
    group = State()
    name = State()
    password = State()
=======
from aiogram.dispatcher.filters.state import State, StatesGroup


class GeneralStates(StatesGroup):
    settings = State()
    select_lang = State()


class OrderFood(StatesGroup):
    init = State()
    on_menu = State()
    waiting_for_food = State()
    confirm = State()
    continue_or_order = State()
    order_food = State()
    payment = State()
    edit_cart = State()


class ReserveTable(StatesGroup):
    select_table = State()


class Registration(StatesGroup):
    course = State()
    group = State()
    name = State()
    password = State()
>>>>>>> 2b4e0576a6bb5ad7557b0d37e51b800ea9e6a1f8
