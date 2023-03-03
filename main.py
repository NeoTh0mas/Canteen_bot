#!/usr/bin/env python
# -*- coding: utf-8 -*-

from aiogram import executor, types, Dispatcher
from aiogram.dispatcher import FSMContext

import atexit
import menu
import reservation
import registration
import settings
import bug_report
from FSM import *
from create_bot import dp, bot, scheduler, time_check
from db_handlers import profile_find, reset_db, time_period, time_period_get, table_check_profile, get_seats
from keyboards import *

# variables
greeting = "👋Hi, I am canteen bot working in IHT, you can reserve a table or order meal with me, try my functions to learn more!"


async def planned(dispatcher: Dispatcher):
    reset_db()


def schedule_jobs():
    scheduler.add_job(planned, "cron", hour=8, minute=30, args=(dp, ))


schedule_jobs()


async def start_up():
    print("Here")


# initialising keyboard and send greeting
@dp.message_handler(commands="start", state=None)  # launching the bot and initializing buttons
async def initialize(message: types.Message):
    await message.reply(greeting, reply_markup=init_keyboard)
    await OrderFood.init.set()


@dp.message_handler(commands="reset", state=OrderFood.states_names + ReserveTable.states_names + GeneralStates.states_names + Registration.states_names + BugReport.states_names)
async def state_check(message: types.Message):
    await OrderFood.init.set()
    await message.reply("States were reset successfully", reply_markup=init_keyboard)


@dp.message_handler(commands="reset_tables", state=OrderFood.states_names + ReserveTable.states_names + GeneralStates.states_names + Registration.states_names)
async def state_check(message: types.Message):
    await OrderFood.init.set()
    await message.reply("Tables were reset successfully", reply_markup=init_keyboard)


@dp.message_handler(commands="terms", state=OrderFood.states_names + ReserveTable.states_names + GeneralStates.states_names)
async def state_check(message: types.Message):
    await message.reply("*terms related with the click payments and our refund policy")\



@dp.message_handler(commands="time_period", state=OrderFood.states_names + ReserveTable.states_names + GeneralStates.states_names)
async def state_check(message: types.Message):
    time_period()
    await bot.send_message(message.from_user.id, f"The time period is {'ON' if time_period_get() else 'OFF'}")


# back function
@dp.message_handler(lambda message: message.text == "◀Назад",
                    state=[OrderFood.on_menu, OrderFood.init, OrderFood.continue_or_order, OrderFood.waiting_for_food,
                           OrderFood.confirm, OrderFood.payment, ReserveTable.select_table, ReserveTable.select_period,
                           ReserveTable.select_people, ReserveTable.select_confirm, ReserveTable.confirm, GeneralStates.settings, GeneralStates.select_lang,
                           Registration.course, Registration.group, Registration.name, BugReport.description])
async def back_to_the_keyboard(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state.split(":")[1] in ["on_menu", "continue_or_order", "settings", "select_lang"]:
        await bot.send_message(message.chat.id, init_keyboard.name, reply_markup=init_keyboard)
    elif current_state.split(":")[1] == "waiting_for_food":
        await bot.send_message(message.chat.id, menu_keyboard.name, reply_markup=menu_keyboard)
    elif current_state.split(":")[1] in ["select_table", "select_period", "select_confirm", "confirm"]:
        await bot.send_message(message.chat.id, init_keyboard.name, reply_markup=init_keyboard)
        await bot.delete_message(message.chat.id, message.message_id - 2)
        await bot.delete_message(message.chat.id, message.message_id - 1)
    elif current_state.split(":")[1] in ["description", "select_people"]:
        await bot.delete_message(message.from_user.id, message.message_id - 1)
        await bot.send_message(message.chat.id, init_keyboard.name, reply_markup=init_keyboard)
    elif current_state.split(":")[1] == "confirm":
        await bot.delete_message(message.chat.id, message.message_id - 2)
        await bot.send_message(message.chat.id, menu.current_kb.name, reply_markup=menu.current_kb)
    elif current_state.split(":")[1] == "payment":
        await bot.send_message(message.chat.id, "Выберите действие: ", reply_markup=order_keyboard)
    elif current_state.split(":")[1] in ["course", "group", "name"]:
        await bot.send_message(message.chat.id, init_keyboard.name, reply_markup=init_keyboard)

    await OrderFood.previous()


# initial menu
@dp.message_handler(state=OrderFood.init)  # initial menu
async def book(message: types.Message):
    if profile_find(message.from_user.id):
        profile = profile_find(message.from_user.id)
        if message.text == init_keyboard.labels[0]:  # table reservation
            if time_check():
                if not table_check_profile(message.from_user.id):
                    await bot.send_photo(message.chat.id,
                                         photo="AgACAgIAAxkBAAIe22MfWKQe0kNQ-MOkVGqa4oFjHO9rAAKfwjEb-dz5SNhQ_YJkWNSmAQADAgADeQADKQQ",
                                         reply_markup=back_keyboard)  # reserve a table
                    # AgACAgIAAxkBAAPJY_Xx4LXRl0NwEEjijCdTtPAUiPMAApHBMRvQybFLhEzBp3fjW0UBAAMCAAN5AAMuBA test
                    # AgACAgIAAxkBAAIe22MfWKQe0kNQ-MOkVGqa4oFjHO9rAAKfwjEb-dz5SNhQ_YJkWNSmAQADAgADeQADKQQ original
                    await bot.send_message(message.chat.id, "Выберите период на который хотите забронировать стол: ", reply_markup=period_kb)
                    await ReserveTable.select_period.set()
                else:
                    time = '11:20 - 11:40' if profile['period'] == 1 else '11:40 - 12:00' if profile['period'] == 2 else '12:00 - 12:20'
                    await bot.send_message(message.from_user.id, f"Вы забронировали стол № *{profile['table']}* на время *{time}*", reply_markup=back_keyboard, parse_mode="Markdown")
                    table = get_seats(profile["table"], int(profile["period"]))
                    print(table)
                    seats_kb = Inline_kb([])
                    for person in [f"❌ {x}" for x in table[1]] + ["➕ Добавить" for _ in range(table[0] - (len(table[1]) + 1))]:
                        seats_kb.add(Inline(person))
                    await bot.send_message(message.from_user.id, "Хотите добавить людей, которые будут сидеть рядом?", reply_markup=seats_kb)
                    await ReserveTable.select_people.set()
            else:
                await bot.send_message(message.from_user.id, "Бронирование столов доступно только в период с 9:45 до 13:40!")
        elif message.text == init_keyboard.labels[1]:
            await message.reply("Соберите корзину: ", reply_markup=menu_keyboard)  # order a meal
            await OrderFood.on_menu.set()
        elif message.text == init_keyboard.labels[2]:
            lang = profile_find(message.from_user.id)["language"]
            await message.reply(f"Language: {lang}\nsome other settings are comming soon tho",
                                reply_markup=settings_keyboard)  # settings
            await GeneralStates.settings.set()
        elif message.text == init_keyboard.labels[3]:
            await message.reply(
                f'Фамилия: {profile["surname"]}\nИмя: {profile["name"]}\nГруппа: {profile["group"]}\nСтатус в группе: {"Староста" if profile["status"] == 1 else "Ученик"}')  # profile
        elif message.text == init_keyboard.labels[4]:
            await message.reply("С помощью данной функции вы можете отправлять отчеты об ошибках создателям бота и участвовать в его улучшении.", reply_markup=back_keyboard)  # bug report
            await bot.send_message(message.from_user.id, "Вы нашли ошибку и готовы подробно описать ее и отправить создателям бота?", reply_markup=yes_no_kb)
            await BugReport.description.set()
    else:
        if message.text == init_keyboard.labels[3]:
            await bot.send_message(message.from_user.id, "Войдите в свою учетную запись следуя следующим инструкциям...", reply_markup=back_keyboard)
            await message.reply("Для начала выберите курс на котором вы учитесь: ", reply_markup=course_kb)
            await Registration.course.set()
        else:
            await message.reply("Вы не вошли в свой аккаунт!\n Для входа в аккаунт нажмите на кнопку \"Профиль\" в главном меню\nP.S. Если возникли проблемы со входом, обратитесь к администрации лицея")


# "1ТН1", "1ТН2", "1ТН3", "1ТН4", "2ТН1", "2ТН2", "2ТН3", "2ТН4", "1СГ1", "2СГ1", "1МТН1", "1МТН2", "2МТН1", "2МТН2", "1ВТН1", "1ВТН2"
@dp.message_handler(content_types=["photo"])
async def get_photo_id(message: types.Message):
    _id = message.photo[-1].file_id
    await message.reply(f"Id of the photo:\n{_id}")


# exit redis database in order not to cause errors
async def exit_db():
    await dp.storage.close()
    await dp.storage.wait_closed()


# handlers registration
menu.register_menu_handlers(dp)
reservation.register_reserve_handlers(dp)
settings.register_settings_handlers(dp)
registration.register_registration_handlers(dp)
bug_report.register_bug_handlers(dp)

# if code is launched not as a module it'll be executed
if __name__ == '__main__':
    atexit.register(exit_db, "exited successfully")
    scheduler.start()
    executor.start_polling(dp, skip_updates=False)
