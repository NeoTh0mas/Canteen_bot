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
