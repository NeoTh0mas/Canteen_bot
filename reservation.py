from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext

from FSM import ReserveTable, OrderFood
from create_bot import bot, service
from keyboards import init_keyboard, Inline_kb, Inline, period_kb, Inline_kb_vartical, confirm_inline_kb
from db_handlers import profile_find, table_update, table_check, table_find_idle, people_find, add_person, get_seats, remove_person, table_reset


async def back_to_add(call, t, p):
    table = get_seats(t, p)
    seats_kb = Inline_kb([])
    for person in [f"❌ {x}" for x in table[1]] + ["➕ Добавить" for _ in range(table[0] - (len(table[1]) + 1))]:
        seats_kb.add(Inline(person))
    seats_kb.add(Inline("🔁 Отменить бронь"))
    await bot.edit_message_text("Хотите добавить людей, которые будут сидеть рядом?", call.from_user.id,
                                call.message.message_id,
                                reply_markup=seats_kb)
    await ReserveTable.select_people.set()


# table reservation
async def reserve(call, state=FSMContext):
    # if callback_data["label"] == "Забронированные столы":
    #     reserved_tables = [x for x in [i for i in range(1, 25)] if x not in table_find_idle(callback_data["period"])]
    #     tables = Inline_kb(reserved_tables)
    #     await bot.edit_message_text(f"Забронированные столы: {', '.join(list(map(str, reserved_tables)))[:-2]}", call.from_user.id, call.message.message_id, reply_markup=tables)
    if call.data == "◀Назад":
        await bot.edit_message_text("Выберите период на который хотите забронировать стол: ", call.from_user.id,
                                    call.message.message_id, reply_markup=period_kb)
        await ReserveTable.select_period.set()
    else:
        data = await state.get_data()
        # callback_data = json.loads(call.data)
        profile = profile_find(call.from_user.id)
        if table_check(profile["group"]):
            # some backend to reserve a table (post request to db deleting the table from idle list)

            await call.answer(f"Вы забронировали стол № {call.data}", show_alert=True)
            await bot.delete_message(call.from_user.id, call.message.message_id - 1)
            await bot.delete_message(call.from_user.id, call.message.message_id)
            await OrderFood.init.set()
            table_update(int(call.data), profile["name"], profile["surname"], profile["group"],
                         int(data["period"]))

            await call.message.answer(
                f"✅ Стол № {call.data} был успешно забронирован на время *{'11:20 - 11:40' if data['period'] == 1 else '11:40 - 12:00' if data['period'] == 2 else '12:00 - 12:20'}* на Ваше имя",
                reply_markup=init_keyboard, parse_mode="Markdown")
            for _id in service:
                await bot.send_message(_id,
                                       f"🛎 Стол номер {call.data} был забронирован на имя *{profile['name']}* *{profile['surname']}* и группу *{profile['group']}*!",
                                       parse_mode="Markdown")
        else:
            await call.message.answer(
                "Количество забронированных столов на группу достигло лимита, оставьте места другим)",
                reply_markup=init_keyboard)
            await call.answer()
            await bot.delete_message(call.from_user.id, call.message.message_id - 1)
            await bot.delete_message(call.from_user.id, call.message.message_id)
            await OrderFood.init.set()


# selecting a period on which the table should be reserved
async def period(call, state=FSMContext):
    idle_tables = table_find_idle(int(call.data))
    await state.update_data(period=int(call.data))
    tables = Inline_kb(idle_tables)
    # tables = Inline_kb_custom(labels=idle_tables, callback=int(call.data))  # creating inline keyboard for idle tables
    tables.add(Inline("◀Назад"))
    await call.message.edit_text("Выберите стол который хотите забронировать: ", reply_markup=tables)
    await ReserveTable.select_table.set()


async def people(call, state=FSMContext):
    if call.data == "➕ Добавить":
        profile = profile_find(call.from_user.id)
        people_kb = Inline_kb_vartical(people_find(profile["group"])).add(Inline("◀Назад"))
        await bot.edit_message_text(
            f"Выберите людей из группы *{profile['group']}* которые будут сидесь с Вами за одним столом: ",
            call.from_user.id, call.message.message_id, reply_markup=people_kb, parse_mode="Markdown")
        await ReserveTable.select_confirm.set()
    elif call.data == "🔁 Отменить бронь":
        profile = profile_find(call.from_user.id)
        await state.update_data(table=profile['table'], period=profile['period'])
        await bot.edit_message_text(f"Вы уверены что хотите *отменить бронь* стола № {profile['table']}?\n\n⚠ После отмены брони данного стола его могут тут же забронировать! ", call.from_user.id, call.message.message_id, reply_markup=confirm_inline_kb, parse_mode="Markdown")
        await ReserveTable.cancel_table.set()
    else:
        await bot.edit_message_text(f"Вы уверены что хотите *удалить* ученика *{call.data[2:]}*?", call.from_user.id, call.message.message_id, reply_markup=confirm_inline_kb, parse_mode="Markdown")
        await state.update_data(name=call.data.split(" ")[1], surname=call.data.split(" ")[2], cmd="remove")
        await ReserveTable.confirm.set()


async def cancel_reservation(call, state=FSMContext):
    profile = profile_find(call.from_user.id)
    if call.data == "◀Назад":
        await back_to_add(call, profile['table'], profile['period'])
    else:
        await bot.edit_message_text(f"✅ Вы успешно отменили бронь стола № {profile['table']} на период {'11:20 - 11:40' if profile['period'] == 1 else '11:40 - 12:00' if profile['period'] == 2 else '12:00 - 12:20'}\nТеперь вы можете забронировать другой стол", call.from_user.id, call.message.message_id)
        await bot.send_message(call.from_user.id, init_keyboard.name, reply_markup=init_keyboard)
        table_reset(profile["table"], profile["period"])
        await OrderFood.init.set()


async def select_confirm(call, state=FSMContext):
    if call.data == "◀Назад":
        profile = profile_find(call.from_user.id)
        await back_to_add(call, profile['table'], profile['period'])
    else:
        await bot.edit_message_text(f"Вы уверены что хотите *добавить* ученика *{call.data}*?", call.from_user.id,
                                    call.message.message_id, reply_markup=confirm_inline_kb, parse_mode="Markdown")
        await state.update_data(name=call.data.split(" ")[0], surname=call.data.split(" ")[1], cmd='add')
        await ReserveTable.confirm.set()


async def confirm(call, state=FSMContext):
    data = await state.get_data()
    profile = profile_find(call.from_user.id)
    if call.data == "Подтвердить":
        name = data.get('name')
        surname = data.get('surname')
        if data.get("cmd") == 'add':
            await call.answer(f"✅ Ученик с именем {name} {surname} был успешно добавлен к вам за стол!", show_alert=True)
            add_person(name, surname, profile["table"], profile["period"])
        elif data.get("cmd") == "remove":
            await call.answer(f"❌ {name} {surname} больше не сидит с вами за одним столом!", show_alert=True)
            remove_person(name, surname, profile["table"], int(profile["period"]))

        table = get_seats(profile["table"], profile["period"])
        seats_kb = Inline_kb([])
        for person in [f"❌ {x}" for x in table[1]] + ["➕ Добавить" for _ in range(table[0] - (len(table[1]) + 1))]:
            seats_kb.add(Inline(person))
        seats_kb.add(Inline("🔁 Отменить бронь"))
        await bot.edit_message_text("Хотите добавить людей, которые будут сидеть рядом?", call.from_user.id,
                                    call.message.message_id,
                                    reply_markup=seats_kb)
        await ReserveTable.select_people.set()
    else:
        if data.get("cmd") == "add":
            profile = profile_find(call.from_user.id)
            people_kb = Inline_kb_vartical(people_find(profile["group"])).add(Inline("◀Назад"))
            await bot.edit_message_text(
                f"Выберите людей из группы *{profile['group']}* которые будут сидесь с Вами за одним столом: ",
                call.from_user.id, call.message.message_id, reply_markup=people_kb, parse_mode="Markdown")
            await ReserveTable.select_confirm.set()
        elif data.get("cmd") == "remove":
            await back_to_add(call, profile['table'], profile['period'])


# register handlers
def register_reserve_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(period, lambda call: True, state=ReserveTable.select_period)
    dp.register_callback_query_handler(reserve, lambda call: True, state=ReserveTable.select_table)
    dp.register_callback_query_handler(people, lambda call: True, state=ReserveTable.select_people)
    dp.register_callback_query_handler(cancel_reservation, lambda call: True, state=ReserveTable.cancel_table)
    dp.register_callback_query_handler(select_confirm, lambda call: True, state=ReserveTable.select_confirm)
    dp.register_callback_query_handler(confirm, lambda call: True, state=ReserveTable.confirm)
