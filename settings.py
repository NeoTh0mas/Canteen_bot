from aiogram import types, Dispatcher

from FSM import GeneralStates, OrderFood
from create_bot import bot
from keyboards import settings_keyboard, init_keyboard, Inline_kb
from db_handlers import profile_lang_update, profile_find

languages = {"English": "en", "Türk": "tr", "Русский": "ru"}


# @dp.message_handler(state=GeneralStates.settings)
async def setting(message: types.Message):
    if message.text == settings_keyboard.labels[0]:
        lang = profile_find(message.from_user.id)["language"]
        inline_lang = [x[0] if x[1] != lang else "" for x in languages.items()]
        for i, j in enumerate(inline_lang):
            if not j:
                inline_lang.pop(i)
        language_keyboard = Inline_kb(inline_lang)
        await message.reply("Выбирете язык: ", reply_markup=language_keyboard)
        await GeneralStates.select_lang.set()


async def select_lang(call):
    lang = languages[call.data]
    profile_lang_update(call.from_user.id, lang)
    await call.message.answer(f"✅Язык был изменен на {call.data}", reply_markup=init_keyboard)
    await call.answer()
    await bot.delete_message(call.from_user.id, call.message.message_id)
    await OrderFood.init.set()


def register_settings_handlers(dp: Dispatcher):
    dp.register_message_handler(setting, state=GeneralStates.settings)
    dp.register_callback_query_handler(select_lang, state=GeneralStates.select_lang)
