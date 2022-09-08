from aiogram import executor, types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup

import atexit
import menu
import reservation
import settings
from FSM import *
from create_bot import dp, bot, scheduler
from db_handlers import profile_find, table_find_idle, reset_db
from keyboards import *

# variables
greeting = "👋Hi, I am canteen bot working in IHT, you can reserve a table or order meal with me, try my functions to learn more!"
# PRICE = types.LabeledPrice(label="Рис", amount=500000)


async def planned(dispatcher: Dispatcher):
    await dispatcher.bot.send_message(266212760, "Message sent using scheduler!")
    reset_db()


def schedule_jobs():
    scheduler.add_job(planned, "cron", hour="10", args=(dp, ))


async def start_up():
    print("Here")


# initialising keyboard and send greeting
@dp.message_handler(commands="start", state=None)  # launching the bot and initializing buttons
async def initialize(message: types.Message):
    await message.reply(greeting, reply_markup=init_keyboard)
    await OrderFood.init.set()


@dp.message_handler(commands="reset", state=OrderFood.states_names + ReserveTable.states_names + GeneralStates.states_names)
async def state_check(message: types.Message):
    await OrderFood.init.set()
    await message.reply("States were reset successfully", reply_markup=init_keyboard)


@dp.message_handler(commands="terms", state=OrderFood.states_names + ReserveTable.states_names + GeneralStates.states_names)
async def state_check(message: types.Message):
    await message.reply("*terms related with the click payments and our refund policy")


# back function
@dp.message_handler(lambda message: message.text == "◀Назад",
                    state=[OrderFood.on_menu, OrderFood.init, OrderFood.continue_or_order, OrderFood.waiting_for_food, OrderFood.confirm, OrderFood.payment, ReserveTable.select_table, GeneralStates.settings, GeneralStates.select_lang])
async def back_to_the_keyboard(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state.split(":")[1] in ["on_menu", "continue_or_order", "settings", "select_lang"]:
        await message.reply(init_keyboard.name, reply_markup=init_keyboard)
    elif current_state.split(":")[1] == "waiting_for_food":
        await message.reply(menu_keyboard.name, reply_markup=menu_keyboard)
    elif current_state.split(":")[1] == "select_table":
        await message.reply(init_keyboard.name, reply_markup=init_keyboard)
        await bot.delete_message(message.chat.id, message.message_id - 2)
        await bot.delete_message(message.chat.id, message.message_id - 1)
    elif current_state.split(":")[1] == "confirm":
        await bot.delete_message(message.chat.id, message.message_id - 2)
        await message.reply(menu.current_kb.name, reply_markup=menu.current_kb)
    elif current_state.split(":")[1] == "payment":
        await bot.send_message(message.chat.id, "Выберите действие: ", reply_markup=order_keyboard)

    await OrderFood.previous()


# initial menu
@dp.message_handler(state=OrderFood.init)  # initial menu
async def book(message: types.Message):
    if message.text == init_keyboard.labels[0]:
        tables = InlineKeyboardMarkup()
        idle_tables = table_find_idle()
        tables.add(*create_kb(idle_tables))
        await bot.send_photo(message.chat.id, photo=open("images\\canteen.png", 'rb'),
                             caption=f"Свободные столы: *{', '.join(list(map(str, idle_tables)))}*\nОстальные уже забронированы:)", parse_mode="Markdown", reply_markup=back_keyboard)  # reserve a table
        await message.reply("Выбирете стол который хотите забронировать: ", reply_markup=tables)
        await ReserveTable.select_table.set()
    elif message.text == init_keyboard.labels[1]:
        await message.reply("Соберите корзину: ", reply_markup=menu_keyboard)  # order a meal
        await OrderFood.on_menu.set()
    elif message.text == init_keyboard.labels[2]:
        lang = profile_find(message.from_user.id)["language"]
        await message.reply(f"Language: {lang}\nsome other settings are comming soon tho", reply_markup=settings_keyboard)  # settings
        await GeneralStates.settings.set()
    elif message.text == init_keyboard.labels[3]:
        try:
            profile = profile_find(message.from_user.id)
            await message.reply(
                f'Имя: {profile["name"]}\nФамилия: {profile["surname"]}\nГруппа: {profile["group"]}')  # profile
        except (Exception, ):
            await message.reply("Оу, кажется вас нет в базе данных😬\nЕсли вы ученик IHT, обратитесь в администрацию "
                                "лицея с данной проблемой\nP.S заранее извиняемся за доставленные неудобства😅")
    elif message.text == init_keyboard.labels[4]:
        await message.reply("Finding bugs...none found, this function is useless:)")  # report


# @dp.message_handler(content_types=["photo"])
# async def get_photo_id(message: types.Message):
#     _id = message.photo[-1].file_id
#     await message.reply(f"Id of the photo:\n{_id}")


# exit redis database in order not to cause some errors
async def exit_db():
    await dp.storage.close()
    await dp.storage.wait_closed()


# handlers registration
menu.register_menu_handlers(dp)
reservation.register_reserve_handlers(dp)
settings.register_settings_handlers(dp)

# if code is launched not as a module it'll be executed
if __name__ == '__main__':
    atexit.register(exit_db, "exited successfully")
    scheduler.start()
    executor.start_polling(dp, skip_updates=False)
