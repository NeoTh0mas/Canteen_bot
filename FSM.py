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
    select_period = State()
    select_table = State()
    select_people = State()
    select_confirm = State()
    confirm = State()


class Registration(StatesGroup):
    course = State()
    group = State()
    name = State()
    password = State()


class BugReport(StatesGroup):
    description = State()
    photo = State()
    photo_agree = State()
    photo_send = State()
    send = State()
