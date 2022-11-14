from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext

from create_bot import bot
from FSM import Registration, OrderFood
from keyboards import init_keyboard, groups1, groups2, course_kb
from db_handlers import profile_check, register, match_passwords


group_names = {"ТН": ["es", "tn", "тн"], "АФ": ["af", "аф"], "СГ": ["sg", "сг"], "MTN": ["mtn", "мтн"], "ВТН": ["vtn", "втн"]}


# def group_check(group_name):
#     if len(group_name) == 4:
#         if group_name[1:3] in ["sg", "af", "сг", "аф"]:
#             return group_name[-1].isdigit() and group_name[0] in ["1", "2"] and group_name[-1] in ["1", "2"]
#         else:
#             return group_name[-1].isdigit() and group_name[1:3].lower() in ["es", "tn", "тн"] and group_name[0] in ["1", "2"] and group_name[-1] in [str(x) for x in range(1, 5)]
#     elif len(group_name) == 5:
#         if group_name[1:4] in ["vtn", "втн"]:
#             return group_name[-1].isdigit() and group_name[0] == "1" and group_name[-1] in ["1", "2"]
#         else:
#             return group_name[-1].isdigit() and group_name[1:4].lower() in ["mtn", "мтн"] and group_name[0] in ["1", "2"] and group_name[-1] in ["1", "2"]
#     else:
#         return False


# async def group(message: types.Message, state: FSMContext):
#     await bot.send_message(message.from_user.id, "Введите Ф.И.О\n(e.g Иванов Иван Иванович):")
#     gn = message.text[1:3].lower()
#     if len(message.text) == 5:
#         gn = message.text[1:4].lower()
#     for i, j in enumerate(group_names.values()):
#         if gn in j:
#             gn = f"{message.text[0]}{list(group_names.keys())[i]}{message.text[-1]}"
#
#     await state.update_data(group=gn)
#     await Registration.name.set()


async def group(call, state=FSMContext):
    if call.data == "◀Назад":
        await bot.edit_message_text("Выберите курс на котором вы учитесь: ", call.from_user.id, call.message.message_id, reply_markup=course_kb)
        await Registration.course.set()
    else:
        await bot.send_message(call.from_user.id, "Введите Ф.И.О\n(e.g Иванов Иван Иванович):")
        await bot.edit_message_text("Теперь выберите группу: ", call.from_user.id, call.message.message_id, reply_markup="")
        await state.update_data(group=call.data)
        await Registration.name.set()


async def name(message: types.Message, state: FSMContext):
    if len(message.text.split()) == 3:
        data = await state.get_data()
        if profile_check(message.text.split()[1], message.text.split()[0], data.get("group").upper()):
            await bot.send_message(message.from_user.id, "Напоследок введите пароль, который вам дали при регистрации:")
            await state.update_data(name=message.text.split()[1], surname=message.text.split()[0], last_name=message.text.split()[2])
            await Registration.password.set()
        else:
            await bot.send_message(message.from_user.id, "Ф.И.О или группа указаны не правильно!\nЕсли вы абсолютно уверены, что все правильно, но войти в аккаунт не получается, свяжитесь с администрацией")
    else:
        await bot.send_message(message.from_user.id, "Введите свою фамилию, имя и отчество как в примере")


async def check_password(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if match_passwords(data.get("name"), data.get("surname"), message.text):
        await bot.send_message(message.from_user.id, "✅ Вы успешно вошли в аккаунт, наслаждайтесь отсутвием очередей в столовой вместе со Stewart-ом:)", reply_markup=init_keyboard)
        register(message.from_user.id, data.get("name"), data.get("surname"))
        await OrderFood.init.set()
    else:
        await bot.send_message(message.from_user.id, "Указанный пароль неверный, попробуйте заново")


async def course(call):
    if call.data == "1 курс":
        await bot.edit_message_text("Теперь выберите группу: ", call.from_user.id, call.message.message_id, reply_markup=groups1)
    elif call.data == "2 курс":
        await bot.edit_message_text("Теперь выберите группу: ", call.from_user.id, call.message.message_id, reply_markup=groups2)
    await call.answer()
    await Registration.group.set()


def register_registration_handlers(dp: Dispatcher):
    dp.register_message_handler(group, state=Registration.group)
    dp.register_message_handler(name, state=Registration.name)
    dp.register_message_handler(check_password, state=Registration.password)
    dp.register_callback_query_handler(course, lambda call: True, state=Registration.course)
    dp.register_callback_query_handler(group, lambda call: True, state=Registration.group)
