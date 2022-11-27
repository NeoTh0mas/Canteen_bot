<<<<<<< HEAD
from aiogram import Dispatcher

from FSM import ReserveTable, OrderFood
from create_bot import bot
from keyboards import init_keyboard, Inline_kb, Inline
from db_handlers import profile_find, table_update, table_check, table_find, table_find_idle


# table reservation
async def reserve(call):
    if call.data == "Забронированные столы":
        reserved_tables = [x for x in table_find_idle() if x not in [i for i in range(25)]]
        tables = Inline_kb(reserved_tables)
        await bot.edit_message_text("Удалите ненужное:", call.from_user.id, call.message.message_id, reply_markup=tables)
    else:
        profile = profile_find(call.from_user.id)
        if table_check(profile["group"]):
            # some backend to reserve a table (post request to db deleting the table from idle list)
            await OrderFood.init.set()
            table_update(int(call.data), profile["name"], profile["surname"], profile["group"])
            await call.message.answer(f"✅Стол номер {call.data} был успешно забронирован на ваше имя", reply_markup=init_keyboard)

            await bot.send_message(266212760, f"🛎 Стол номер {call.data} был забронирован на имя *{profile['name']}* *{profile['surname']}* и группу *{profile['group']}*!", parse_mode="Markdown")

            await call.answer(f"Вы забронировали стол № {call.data}", show_alert=True)
            await bot.delete_message(call.from_user.id, call.message.message_id - 1)
            await bot.delete_message(call.from_user.id, call.message.message_id)
        else:
            await call.message.answer("Количество забронированных столов на группу достигло лимита, оставьте места другим)", reply_markup=init_keyboard)
            await call.answer()
            await bot.delete_message(call.from_user.id, call.message.message_id - 1)
            await bot.delete_message(call.from_user.id, call.message.message_id)
            await OrderFood.init.set()


# register handlers
def register_reserve_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(reserve, lambda call: True, state=ReserveTable.select_table)
=======
from aiogram import Dispatcher

from FSM import ReserveTable, OrderFood
from create_bot import bot
from keyboards import init_keyboard, Inline_kb, Inline
from db_handlers import profile_find, table_update, table_check, table_find, table_find_idle


# table reservation
async def reserve(call):
    if call.data == "Забронированные столы":
        reserved_tables = [x for x in table_find_idle() if x not in [i for i in range(25)]]
        tables = Inline_kb(reserved_tables)
        await bot.edit_message_text("Удалите ненужное:", call.from_user.id, call.message.message_id, reply_markup=tables)
    else:
        profile = profile_find(call.from_user.id)
        if table_check(profile["group"]):
            # some backend to reserve a table (post request to db deleting the table from idle list)
            await OrderFood.init.set()
            table_update(int(call.data), profile["name"], profile["surname"], profile["group"])
            await call.message.answer(f"✅Стол номер {call.data} был успешно забронирован на ваше имя", reply_markup=init_keyboard)

            await bot.send_message(266212760, f"🛎 Стол номер {call.data} был забронирован на имя *{profile['name']}* *{profile['surname']}* и группу *{profile['group']}*!", parse_mode="Markdown")

            await call.answer(f"Вы забронировали стол № {call.data}", show_alert=True)
            await bot.delete_message(call.from_user.id, call.message.message_id - 1)
            await bot.delete_message(call.from_user.id, call.message.message_id)
        else:
            await call.message.answer("Количество забронированных столов на группу достигло лимита, оставьте места другим)", reply_markup=init_keyboard)
            await call.answer()
            await bot.delete_message(call.from_user.id, call.message.message_id - 1)
            await bot.delete_message(call.from_user.id, call.message.message_id)
            await OrderFood.init.set()


# register handlers
def register_reserve_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(reserve, lambda call: True, state=ReserveTable.select_table)
>>>>>>> 2b4e0576a6bb5ad7557b0d37e51b800ea9e6a1f8
