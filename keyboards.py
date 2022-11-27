<<<<<<< HEAD
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup


# keyboard class
class Keyboard(ReplyKeyboardMarkup):
    def __init__(self, name, labels):
        ReplyKeyboardMarkup.__init__(self, resize_keyboard=True, row_width=2)
        self.name = name
        self.labels = labels


class Inline(InlineKeyboardButton):
    def __init__(self, name):
        self.name = name
        InlineKeyboardButton.__init__(self, name, callback_data=name)


class Inline_kb(InlineKeyboardMarkup):
    def __init__(self, labels):
        InlineKeyboardMarkup.__init__(self)
        self.labels = labels
        buttons = []
        for j in list(map(str, labels)):
            buttons.append(Inline(j))
        self.add(*buttons)


# keyboards
# initial keyboard
init_keyboard = Keyboard("Главное меню",
                         ["🛎 Забронировать стол", "🍛 Заказать еду", "⚙ Настройки", "👤 Профиль", "🖍 Сообщить об ошибке"])
settings_keyboard = Keyboard("Settings", ["🔄 Поменять язык"])
back_keyboard = Keyboard("Назад", [])


# menu keyboards
menu_keyboard = Keyboard("Меню", ["Гарниры🍛", "Мясо🍗", "Готовые блюда🍝", "Овощи🥦", "Салаты🥬", "Стартер паки🍱", "🛒Корзина"])
rice_keyboard = Keyboard("Гарниры", ["Рис🍚", "Гречка🥣", "Макароны🍜", "Пюре🥔", "Фасоль🍛"])
meat_keyboard = Keyboard("Мясо", ["Киевская котлета🥩", "Говяжая котлета🥩", "Стейк🥩", "Отбивная в кляре🥩", "Отбивная в сухарях🥩", "Отбивная с сыром🥩", "Голубцы🥩", "Стрипсы🥩", "Картошка с курицей🥩", "Картошка с курицей 0.7🥩"])
vegs_keyboard = Keyboard("Овощи", ["Морковь🥕", "Брокколи🥦"])
meals_keyboard = Keyboard("Готовые блюда", ["Плов🍲", "Жареный лагман🍲", "Окрошка🍲"])
salads_keyboard = Keyboard("Салаты", ["Оливье🥗", "Ачучук🥗", "Салат с баклажанами🥗", "Мужской каприз🥗", "Цезарь🥗"])
starter_pack_keyboard = Keyboard("Готовые блюда",
                                 ["🍛Рис + куринная котлета + компот", "🍛Пюре + Стейк + компот"])
full_cart_keyboard = Keyboard("Что делать дальше?", ["🛒Корзина", "Продолжить"])
order_keyboard = Keyboard("Оформить заказ?", ["Оформить заказ", "Редактировать корзину", "Вернуться в меню"])
payment_keyboard = Keyboard("Способ оплаты", ["Касса", "Click"])
confirm_keyboard = Keyboard("Подтвердить?", ["Подтвердить"])

course_kb = Inline_kb(["1 курс", "2 курс"])
groups1 = Inline_kb(["1ТН1", "1ТН2", "1ТН3", "1ТН4", "1СГ1", "1МТН1", "1МТН2", "1ВТН1", "1ВТН2"])
groups1.add(Inline("◀Назад"))
groups2 = Inline_kb(["2ТН1", "2ТН2", "2ТН3", "2ТН4", "2СГ1", "2МТН1", "2МТН2"])
groups2.add(Inline("◀Назад"))

# adding all the labels to the buttons
init_keyboard.add(*init_keyboard.labels)
menu_keyboard.add(*menu_keyboard.labels).add("◀Назад")
rice_keyboard.add(*rice_keyboard.labels).add("◀Назад")
meat_keyboard.add(*meat_keyboard.labels).add("◀Назад")
meals_keyboard.add(*meals_keyboard.labels).add("◀Назад")
vegs_keyboard.add(*vegs_keyboard.labels).add("◀Назад")
salads_keyboard.add(*salads_keyboard.labels).add("◀Назад")
starter_pack_keyboard.add(*starter_pack_keyboard.labels).add("◀Назад")
full_cart_keyboard.add(*full_cart_keyboard.labels)
order_keyboard.add(*order_keyboard.labels)
# tables.add(*create_kb(idle_tables))
back_keyboard.add(*back_keyboard.labels).add("◀Назад")
confirm_keyboard.add(*confirm_keyboard.labels).add("◀Назад")
payment_keyboard.add(*payment_keyboard.labels).add("◀Назад")
settings_keyboard.add(*settings_keyboard.labels).add("◀Назад")

order_keyboard.one_time_keyboard = True
=======
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup


# keyboard class
class Keyboard(ReplyKeyboardMarkup):
    def __init__(self, name, labels):
        ReplyKeyboardMarkup.__init__(self, resize_keyboard=True, row_width=2)
        self.name = name
        self.labels = labels


class Inline(InlineKeyboardButton):
    def __init__(self, name):
        self.name = name
        InlineKeyboardButton.__init__(self, name, callback_data=name)


class Inline_kb(InlineKeyboardMarkup):
    def __init__(self, labels):
        InlineKeyboardMarkup.__init__(self)
        self.labels = labels
        buttons = []
        for j in list(map(str, labels)):
            buttons.append(Inline(j))
        self.add(*buttons)


# keyboards
# initial keyboard
init_keyboard = Keyboard("Главное меню",
                         ["🛎 Забронировать стол", "🍛 Заказать еду", "⚙ Настройки", "👤 Профиль", "🖍 Сообщить об ошибке"])
settings_keyboard = Keyboard("Settings", ["🔄 Поменять язык"])
back_keyboard = Keyboard("Назад", [])


# menu keyboards
menu_keyboard = Keyboard("Меню", ["Гарниры🍛", "Мясо🍗", "Готовые блюда🍝", "Овощи🥦", "Салаты🥬", "Стартер паки🍱", "🛒Корзина"])
rice_keyboard = Keyboard("Гарниры", ["Рис🍚", "Гречка🥣", "Макароны🍜", "Пюре🥔", "Фасоль🍛"])
meat_keyboard = Keyboard("Мясо", ["Киевская котлета🥩", "Говяжая котлета🥩", "Стейк🥩", "Отбивная в кляре🥩", "Отбивная в сухарях🥩", "Отбивная с сыром🥩", "Голубцы🥩", "Стрипсы🥩", "Картошка с курицей🥩", "Картошка с курицей 0.7🥩"])
vegs_keyboard = Keyboard("Овощи", ["Морковь🥕", "Брокколи🥦"])
meals_keyboard = Keyboard("Готовые блюда", ["Плов🍲", "Жареный лагман🍲", "Окрошка🍲"])
salads_keyboard = Keyboard("Салаты", ["Оливье🥗", "Ачучук🥗", "Салат с баклажанами🥗", "Мужской каприз🥗", "Цезарь🥗"])
starter_pack_keyboard = Keyboard("Готовые блюда",
                                 ["🍛Рис + куринная котлета + компот", "🍛Пюре + Стейк + компот"])
full_cart_keyboard = Keyboard("Что делать дальше?", ["🛒Корзина", "Продолжить"])
order_keyboard = Keyboard("Оформить заказ?", ["Оформить заказ", "Редактировать корзину", "Вернуться в меню"])
payment_keyboard = Keyboard("Способ оплаты", ["Касса", "Click"])
confirm_keyboard = Keyboard("Подтвердить?", ["Подтвердить"])

course_kb = Inline_kb(["1 курс", "2 курс"])
groups1 = Inline_kb(["1ТН1", "1ТН2", "1ТН3", "1ТН4", "1СГ1", "1МТН1", "1МТН2", "1ВТН1", "1ВТН2"])
groups1.add(Inline("◀Назад"))
groups2 = Inline_kb(["2ТН1", "2ТН2", "2ТН3", "2ТН4", "2СГ1", "2МТН1", "2МТН2"])
groups2.add(Inline("◀Назад"))

# adding all the labels to the buttons
init_keyboard.add(*init_keyboard.labels)
menu_keyboard.add(*menu_keyboard.labels).add("◀Назад")
rice_keyboard.add(*rice_keyboard.labels).add("◀Назад")
meat_keyboard.add(*meat_keyboard.labels).add("◀Назад")
meals_keyboard.add(*meals_keyboard.labels).add("◀Назад")
vegs_keyboard.add(*vegs_keyboard.labels).add("◀Назад")
salads_keyboard.add(*salads_keyboard.labels).add("◀Назад")
starter_pack_keyboard.add(*starter_pack_keyboard.labels).add("◀Назад")
full_cart_keyboard.add(*full_cart_keyboard.labels)
order_keyboard.add(*order_keyboard.labels)
# tables.add(*create_kb(idle_tables))
back_keyboard.add(*back_keyboard.labels).add("◀Назад")
confirm_keyboard.add(*confirm_keyboard.labels).add("◀Назад")
payment_keyboard.add(*payment_keyboard.labels).add("◀Назад")
settings_keyboard.add(*settings_keyboard.labels).add("◀Назад")

order_keyboard.one_time_keyboard = True
>>>>>>> 2b4e0576a6bb5ad7557b0d37e51b800ea9e6a1f8
