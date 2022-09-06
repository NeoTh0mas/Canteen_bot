from aiogram import Dispatcher

from FSM import ReserveTable, OrderFood
from create_bot import bot
from keyboards import init_keyboard
from db_handlers import profile_find, table_update


# table reservation
async def reserve(call):
    # some backend to reserve a table (post request to db deleting the table from idle list)
    await OrderFood.init.set()
    profile = profile_find(call.from_user.id)
    table_update(int(call.data), profile["name"], profile["surname"], profile["group"])
    await call.message.answer(f"✅Стол номер {call.data} был успешно забронирован на ваше имя", reply_markup=init_keyboard)

    await bot.send_message(266212760, f"🛎 Стол номер {call.data} был забронирован на имя *{profile['name']}* *{profile['surname']}* и группу *{profile['group']}*!", parse_mode="Markdown")

    await call.answer(f"Вы забронировали стол № {call.data}", show_alert=True)
    await bot.delete_message(call.from_user.id, call.message.message_id - 1)
    await bot.delete_message(call.from_user.id, call.message.message_id)


# register handlers
def register_reserve_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(reserve, lambda call: True, state=ReserveTable.select_table)
