from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext

from FSM import OrderFood, BugReport
from create_bot import bot, service
from keyboards import init_keyboard, yes_no_kb, back_inline_kb, confirm_inline_kb
from db_handlers import bug_save


async def report(call):
    if call.data == 'Да':
        await bot.edit_message_text("📝 В следующем сообщении вам нужно в подробностях предоставить "
                                    "все детали ошибки (бага), которую вы обнаружили"
                                    "\n\nБаг-репорт (отчет об ошибке) должен включать в себя следующие аспекты:"
                                    "\n1. краткое описание бага\n2. критичность\n3. возможные причины"
                                    "\n4. предложения по исправлению (необязательно)\n5. комментарий "
                                    "(необязательно)\n6. скриншот (необязательно)", call.from_user.id, call.message.message_id)
        await BugReport.photo.set()
    else:
        await bot.delete_message(call.from_user.id, call.message.message_id)
        await bot.send_message(call.from_user.id, init_keyboard.name, reply_markup=init_keyboard)
        await OrderFood.init.set()


async def get_photo(message: types.Message, state=FSMContext):
    if len(message.text) > 50 and len(message.text.split(" ")) > 6:
        await bot.send_message(message.from_user.id, "✅ Отлично, хотите отправить скриншот?", reply_markup=yes_no_kb)
        await state.update_data(description=message.text)
        await BugReport.photo_agree.set()
    elif message.text == "◀Назад":
        await bot.send_message(message.from_user.id, init_keyboard.name, reply_markup=init_keyboard)
        await OrderFood.init.set()
    else:
        await bot.send_message(message.from_user.id, "❗ Вы затронули не все обязательные аспекты или описание ошибки недостаточно подробное для отправки")


async def send_photo(call, state=FSMContext):
    if call.data == "Да":
        await bot.edit_message_text("Отправьте скриншот бага...", call.from_user.id, call.message.message_id, reply_markup=back_inline_kb)
        await BugReport.photo_send.set()
    else:
        await bot.edit_message_text("❕ Вы не отправили скриншот", call.from_user.id, call.message.message_id)
        await bot.send_message(call.from_user.id,
                               "⚠ При нажатии на кнопку \"Подтвердить\" вы соглашаетесь на отправку всех, указанных вами выше, данных, включая *Ф.И.О, группу и телеграм юзернейм*",
                               reply_markup=confirm_inline_kb, parse_mode="Markdown")
        await state.update_data(photo_id=0)
        await BugReport.send.set()


async def screenshot(call):
    await bot.edit_message_text("✅ Отлично, хотите отправить скриншот?", call.from_user.id, call.message.message_id, reply_markup=yes_no_kb)
    await BugReport.photo_agree.set()


async def photo(message: types.Message, state=FSMContext):
    await bot.send_message(message.from_user.id, "✅ Noted")
    await bot.send_message(message.from_user.id,
                           "⚠ При нажатии на кнопку \"Подтвердить\" вы соглашаетесь с отправкой всех, указанных вами выше, данных, включая *Ф.И.О, группу и телеграм юзернейм*",
                           reply_markup=confirm_inline_kb, parse_mode="Markdown")
    await bot.edit_message_text("❕ Вы успешно отправили скриншот", message.from_user.id, message.message_id - 1)
    await state.update_data(photo_id=message.photo[-1].file_id)
    await BugReport.send.set()


async def report_send(call, state=FSMContext):
    if call.data == "Подтвердить":
        await bot.edit_message_text(
            "❕ Вы подтвердили отправку данных о баге, а также своих Ф.И.О, группы и телеграм юзернейма разработчикам бота",
            call.from_user.id, call.message.message_id)
        await bot.send_photo(call.from_user.id, "AgACAgIAAxkBAAIwhGQAAfQYMhNum4KemNPljyH_NgMB0gACR8QxG2zwAUivXsPIpfPBgAEAAwIAA3gAAy4E", caption="✅ Баг-репорт был успешно отправлен разработчикам бота!\n📞 В случае возникновения вопросов касаемо бага, с вами могут связаться в ближайшее время\n\nБлагодарим за помощь в разработке, Интерхаус никогда не забудет ваш вклад в развитие бота🫡")
        await bot.send_message(call.from_user.id, init_keyboard.name, reply_markup=init_keyboard)
        await OrderFood.init.set()

        data = await state.get_data()
        bug_save(call.from_user.id, call.from_user.username, data["description"], data["photo_id"])

        for i in service:
            if data['photo_id'] == 0:
                await bot.send_message(call.from_user.id, data['description'])
            else:
                await bot.send_photo(i, data['photo_id'], caption=data['description'])
    elif call.data == "◀Назад":
        await bot.edit_message_text("❗ Вы не отправили баг-репорт", call.from_user.id, call.message.message_id)
        await bot.send_message(call.from_user.id, init_keyboard.name, reply_markup=init_keyboard)
        await OrderFood.init.set()


def register_bug_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(report, lambda call: True, state=BugReport.description)
    dp.register_message_handler(get_photo, state=BugReport.photo)
    dp.register_callback_query_handler(send_photo, lambda call: True, state=BugReport.photo_agree)
    dp.register_callback_query_handler(screenshot, lambda call: True, state=BugReport.photo_send)
    dp.register_message_handler(photo, state=BugReport.photo_send, content_types=["photo"])
    dp.register_callback_query_handler(report_send, lambda call: True, state=BugReport.send)
