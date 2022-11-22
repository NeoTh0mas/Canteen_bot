<<<<<<< HEAD
from FSM import OrderFood
from keyboards import *
from create_bot import bot, service, PAYMENT_PROVIDER_TOKEN
from db_handlers import menu_get, menu_get_photo, cart_update, cart_get, cart_clear, profile_find, cart_remove, \
    cart_deleted_list, cart_deleted_update, cart_deleted_reset
from datetime import datetime

from aiogram import types, Dispatcher
from aiogram.types import ReplyKeyboardRemove
from aiogram.types.message import ContentType

menu = menu_get()
current_meal = ""
current_kb = ""


# menu ->
# start menu with all the categories of food
async def order(message: types.Message):
    global current_kb
    if message.text == menu_keyboard.labels[0]:
        await message.reply("Выберите гарнир:", reply_markup=rice_keyboard)  # garnish
        current_kb = rice_keyboard
        await OrderFood.waiting_for_food.set()
    elif message.text == menu_keyboard.labels[1]:
        await message.reply("Выберите мясные изделия:", reply_markup=meat_keyboard)  # meat
        current_kb = meat_keyboard
        await OrderFood.waiting_for_food.set()
    elif message.text == menu_keyboard.labels[2]:
        await message.reply("Выберите готовые блюда:", reply_markup=meals_keyboard)  # meals
        current_kb = meals_keyboard
        await OrderFood.waiting_for_food.set()
    elif message.text == menu_keyboard.labels[3]:
        await message.reply("Выберите овощи:", reply_markup=vegs_keyboard)  # vegetables
        current_kb = vegs_keyboard
        await OrderFood.waiting_for_food.set()
    elif message.text == menu_keyboard.labels[4]:
        await message.reply("Выберите салаты:", reply_markup=salads_keyboard)  # salads
        current_kb = salads_keyboard
        await OrderFood.waiting_for_food.set()
    elif message.text == menu_keyboard.labels[5]:
        await message.reply("Выберите готовые наборы:", reply_markup=starter_pack_keyboard)  # starter packs
        current_kb = starter_pack_keyboard
        await OrderFood.waiting_for_food.set()
    elif message.text == menu_keyboard.labels[6]:
        cart = cart_get(message.from_user.id)
        set_cart = list(set(cart))
        # cart_keyboard = InlineKeyboardMarkup()
        # cart_keyboard.add(*create_kb([f"❌ {meal}" for meal in [set_cart[x] for x in range(len(set_cart))]]))
        final_cart = [f"{i + 1}. *{set_cart[i]}*\n{cart.count(set_cart[i])} x {menu[set_cart[i]][1]}\n\n" for i in
                      range(len(set_cart))]  # cool alg to group all selected products and their prices from cart
        await message.reply(f"*🛒 Корзина*:\n\n{''.join(final_cart)}\n🧾Итого: {sum([menu[x][1] for x in cart])} сум",
                            parse_mode="Markdown", reply_markup=order_keyboard)
        await OrderFood.order_food.set()


# adding food to the cart
async def send_meal(message: types.Message):
    global current_meal
    if message.text == "◀Назад":
        return
    current_meal = message.text[:-1].capitalize()
    if current_meal not in menu.keys():  # in case of not existing the meal in the menu
        await message.reply("Данного блюда нет в меню, попробуйте снова!")
        return
    else:
        if menu_get_photo(message.text[:-1]) != "":  # in case of existing the image of the meal
            await bot.send_photo(message.chat.id, photo=menu_get_photo(message.text[:-1]),
                                 caption=f"\"{current_meal}\"\nОписание: {menu[current_meal][0]}\n\n💸 Цена: {menu[current_meal][1]} сум")
        else:  # not sending the photo
            await bot.send_message(message.chat.id,
                                   f"\"{current_meal}\"\nОписание: {menu[current_meal][0]}\n\n💸 Цена: {menu[current_meal][1]} сум")
        await message.reply("Добавить данное блюдо в корзину?", reply_markup=confirm_keyboard)
        await OrderFood.confirm.set()


# adding meal to the cart
async def confirm(message: types.Message):
    global current_meal
    if message.text == "◀Назад":
        return
    elif message.text == "Подтвердить":
        await bot.delete_message(message.chat.id,
                                 message.message_id - 2)  # deleting image of the food in order not to excessive number of photos
        cart_update(message.from_user.id, current_meal)  # adding new item to the cart
        await message.reply(
            f"📥 Блюдо \"{current_meal}\" было успешно добавлено в корзину!\n\nХотите заказать еду из вашей корзины или продолжить ее собирать?",
            reply_markup=full_cart_keyboard)
        await OrderFood.continue_or_order.set()


# choosing to continue or to order the food in the cart
async def cont_ord(message: types.Message):
    cart = cart_get(message.from_user.id)
    set_cart = list(set(cart))
    if message.text == full_cart_keyboard.labels[0]:  # cart
        final_cart = [f"{i + 1}. *{set_cart[i]}*\n{cart.count(set_cart[i])} x {menu[set_cart[i]][1]}\n\n" for i in
                      range(len(set_cart))]  # cool alg to group all selected products and their prices from cart
        await message.reply(f"*🛒 Корзина*:\n\n{''.join(final_cart)}\n🧾Итого: {sum([menu[x][1] for x in cart])} сум",
                            parse_mode="Markdown",
                            reply_markup=order_keyboard)  # list of the items added to the cart (receipt)
        await OrderFood.order_food.set()
    elif message.text == full_cart_keyboard.labels[1]:  # back to the menu
        await message.reply("Выберите еще что-нибудь:", reply_markup=menu_keyboard)
        await OrderFood.on_menu.set()


# ordering the food from the cart
async def cart_order(message: types.Message):
    if message.text == order_keyboard.labels[0]:  # confirm the order
        now = datetime.now()
        time_s = now.replace(hour=9, minute=45)
        time_f = now.replace(hour=14, minute=40)
        if time_s < now < time_f:
            await message.reply("Выберите способ оплаты: ", reply_markup=payment_keyboard)
            await OrderFood.payment.set()
        else:
            await message.reply("Заказы еды доступны только в период с 9:45 до 13:40!", reply_markup=init_keyboard)
            await OrderFood.init.set()
    elif message.text == order_keyboard.labels[1]:  # editing cart
        ReplyKeyboardRemove()
        cart = cart_get(message.from_user.id)
        if not cart:  # is there is no items in the cart
            await message.reply("Хмм, кажется вы забыли добавить еду в корзину:)", reply_markup=order_keyboard)
        else:
            cart_keyboard = Inline_kb([f"❌ {meal}" for meal in [cart[x] for x in range(len(cart))]]).add(Inline("Подтвердить"))  # creating dinamic inline keyboard so that it could be changed after deleting some items
            await message.reply("Удалите ненужное: ", reply_markup=cart_keyboard)
            # print(message.message_id)
            # await bot.edit_message_text("Удалите ненужное:", message.chat.id, message.message_id - 1, reply_markup=ReplyKeyboardRemove())
            await OrderFood.edit_cart.set()
    elif message.text == order_keyboard.labels[2]:  # back the main menu
        await message.reply("Меню", reply_markup=menu_keyboard)
        await OrderFood.on_menu.set()


# removing meals from the cart
async def edit_cart(call):
    if call.data == "Подтвердить":
        deleted = cart_deleted_list(call.from_user.id)
        if not deleted:
            await call.message.edit_text(f"Корзина осталась прежней")
            await bot.send_message(call.from_user.id, "Выберите действие: ", reply_markup=order_keyboard)
        else:
            await call.message.edit_text(f"Блюда(о) *{' '.join(deleted)[:-1]}* были удалены из вашей корзины",
                                         parse_mode="Markdown")
            await bot.send_message(call.from_user.id, "Выберите действие: ", reply_markup=order_keyboard)
        cart_deleted_reset(call.from_user.id)
        await OrderFood.order_food.set()
    else:  # if call data is equal to one of the meals
        meal = call.data[2:]
        cart_remove(call.from_user.id, meal)
        await call.answer(f"Блюдо \"{meal}\" было удалено из корзины!", show_alert=True)
        set_cart = cart_get(call.from_user.id)
        if not set_cart:  # if there is at least one meal in the cart
            deleted = cart_deleted_list(call.from_user.id)
            # print(deleted)
            if not deleted:
                await call.message.edit_text(f"Корзина осталась прежней")
            else:
                await call.message.edit_text(f"Блюда(о) *{' '.join(deleted)[:-1]}* были удалены из вашей корзины",
                                             parse_mode="Markdown")
                cart_deleted_reset(call.from_user.id)
                await OrderFood.order_food.set()
        else:
            cart_keyboard = Inline_kb([f"❌ {meal}" for meal in [set_cart[x] for x in range(len(set_cart))]]).add(Inline("Подтвердить"))  # update the inline keyboard so that it will change after a certain meal was deleted
            await call.message.edit_text("Удалите ненужное: ", reply_markup=cart_keyboard)  # edit inline keyboard
            cart_deleted_update(call.from_user.id, meal)  # update the list of meals that were deleted from the cart


# food payment
async def pay(message: types.Message):
    cart = cart_get(message.from_user.id)
    set_cart = list(set(cart))
    price = sum([menu[x][1] for x in cart])  # final price of all the meals in the cart
    if price > 0:
        profile_find(message.from_user.id)
        if message.text == payment_keyboard.labels[0]:  # order goes directly to the canteen staff and payment is made manually with cash
            profile = profile_find(message.from_user.id)
            final_cart = [f"{i + 1}. *{set_cart[i]}*\n{cart.count(set_cart[i])} x {menu[set_cart[i]][1]}\n\n" for i in
                          range(
                              len(set_cart))]  # cool alg to group all selected products and their prices from the cart
            await bot.send_message(message.from_user.id,
                                   f"✅ Заказ был передан администрации столовой на обработку, можете забрать его на большой перемене после совершения oплаты в размере *{price} сум* в кассу столовой)\n\nБлагодарим, что использовали бота для заказа еды:)",
                                   reply_markup=init_keyboard, parse_mode="Markdown")
            await bot.send_message(service,
                                   f"🛎 Поступил новый заказ:\n\n*{profile['name']} {profile['surname']}* из группы *{profile['group']}* заказал:\n\n{''.join(final_cart)}\nНа сумму: {price}сум",
                                   parse_mode="Markdown")
            cart_clear(message.from_user.id)
            await OrderFood.init.set()
        elif message.text == payment_keyboard.labels[1]:
            PRICES = [types.LabeledPrice(label=set_cart[i], amount=menu[set_cart[i]][1] * 100) for i in
                      range(len(set_cart))]  # cool alg to arrange every meal and its price from the cart

            if PAYMENT_PROVIDER_TOKEN.split(":")[1] == "TEST":
                await bot.send_message(message.chat.id,
                                       "Bot is in test mode, no real money is involved in the following operations")
            await bot.send_invoice(
                message.chat.id,
                title="Еда из корзины",
                description=''.join([f"{set_cart[i]} " for i in range(len(set_cart))]),
                provider_token=PAYMENT_PROVIDER_TOKEN,
                currency="uzs",
                photo_url="https://upload.wikimedia.org/wikipedia/commons/6/6d/Good_Food_Display_-_NCI_Visuals_Online.jpg",
                photo_height=256,
                photo_width=512,
                photo_size=512,
                is_flexible=False,
                prices=PRICES,
                start_parameter="payment_test",
                payload="i_wish_i_knew_what_does_it_mean"
            )
    else:
        await message.reply("Хмм, кажется вы забыли добавить еду в корзину:)")


async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


# in case of successfull payment
async def process_successful_payment(message: types.Message):
    print('successful_payment:')
    pmnt = message.successful_payment.to_python()  # payment components
    for key, val in pmnt.items():
        print(f'{key} = {val}')

    await bot.send_message(message.chat.id,
                           f"✅ Оплата в размере *{message.successful_payment.total_amount // 100}* сум прошла успешно, можете забрать свой заказ на большой перемене в столовой.\n\nP.S правила возврата средств смотрите в /terms",
                           parse_mode="Markdown", reply_markup=init_keyboard)
    await OrderFood.init.set()
    cart = cart_get(message.from_user.id)
    set_cart = list(set(cart))
    price = sum([menu[x][1] for x in cart])
    profile = profile_find(message.from_user.id)
    final_cart = [f"{i + 1}. *{set_cart[i]}*\n{cart.count(set_cart[i])} x {menu[set_cart[i]][1]}\n\n" for i in
                  range(len(set_cart))]  # cool alg to group all selected products and their prices from cart
    await bot.send_message(service,
                           f"🛎 Поступил новый заказ:\n\n*{profile['name']} {profile['surname']}* из группы *{profile['group']}* заказал:\n{''.join(final_cart)}\nНа сумму: {price}сум\nОплата была произведена через CLICK.",
                           parse_mode="Markdown")

    cart_clear(message.from_user.id)


# register the handlers
def register_menu_handlers(dp: Dispatcher):
    dp.register_message_handler(order, state=OrderFood.on_menu)
    dp.register_message_handler(send_meal, state=OrderFood.waiting_for_food)
    dp.register_message_handler(confirm, state=OrderFood.confirm)
    dp.register_message_handler(cont_ord, state=OrderFood.continue_or_order)
    dp.register_message_handler(cart_order, state=OrderFood.order_food)
    dp.register_callback_query_handler(edit_cart, state=OrderFood.edit_cart)
    dp.register_message_handler(pay, state=OrderFood.payment)
    dp.register_pre_checkout_query_handler(process_pre_checkout_query, lambda query: True, state=OrderFood.payment)
    dp.register_message_handler(process_successful_payment, state=OrderFood.payment,
                                content_types=ContentType.SUCCESSFUL_PAYMENT)
=======
from FSM import OrderFood
from keyboards import *
from create_bot import bot, service, PAYMENT_PROVIDER_TOKEN
from db_handlers import menu_get, menu_get_photo, cart_update, cart_get, cart_clear, profile_find, cart_remove, \
    cart_deleted_list, cart_deleted_update, cart_deleted_reset

from aiogram import types, Dispatcher
from aiogram.types import ReplyKeyboardRemove
from aiogram.types.message import ContentType

menu = menu_get()
current_meal = ""
current_kb = ""


# menu ->
# start menu with all the categories of food
async def order(message: types.Message):
    global current_kb
    if message.text == menu_keyboard.labels[0]:
        await message.reply("Выберите гарнир:", reply_markup=rice_keyboard)  # garnish
        current_kb = rice_keyboard
        await OrderFood.waiting_for_food.set()
    elif message.text == menu_keyboard.labels[1]:
        await message.reply("Выберите мясные изделия:", reply_markup=meat_keyboard)  # meat
        current_kb = meat_keyboard
        await OrderFood.waiting_for_food.set()
    elif message.text == menu_keyboard.labels[2]:
        await message.reply("Выберите готовые блюда:", reply_markup=meals_keyboard)  # meals
        current_kb = meals_keyboard
        await OrderFood.waiting_for_food.set()
    elif message.text == menu_keyboard.labels[3]:
        await message.reply("Выберите овощи:", reply_markup=vegs_keyboard)  # vegetables
        current_kb = vegs_keyboard
        await OrderFood.waiting_for_food.set()
    elif message.text == menu_keyboard.labels[4]:
        await message.reply("Выберите салаты:", reply_markup=salads_keyboard)  # salads
        current_kb = salads_keyboard
        await OrderFood.waiting_for_food.set()
    elif message.text == menu_keyboard.labels[5]:
        await message.reply("Выберите готовые наборы:", reply_markup=starter_pack_keyboard)  # starter packs
        current_kb = starter_pack_keyboard
        await OrderFood.waiting_for_food.set()
    elif message.text == menu_keyboard.labels[6]:
        cart = cart_get(message.from_user.id)
        set_cart = list(set(cart))
        # cart_keyboard = InlineKeyboardMarkup()
        # cart_keyboard.add(*create_kb([f"❌ {meal}" for meal in [set_cart[x] for x in range(len(set_cart))]]))
        final_cart = [f"{i + 1}. *{set_cart[i]}*\n{cart.count(set_cart[i])} x {menu[set_cart[i]][1]}\n\n" for i in
                      range(len(set_cart))]  # cool alg to group all selected products and their prices from cart
        await message.reply(f"*🛒 Корзина*:\n\n{''.join(final_cart)}\n🧾Итого: {sum([menu[x][1] for x in cart])} сум",
                            parse_mode="Markdown", reply_markup=order_keyboard)
        await OrderFood.order_food.set()


# adding food to the cart
async def send_meal(message: types.Message):
    global current_meal
    if message.text == "◀Назад":
        return
    current_meal = message.text[:-1].capitalize()
    if current_meal not in menu.keys():  # in case of not existing the meal in the menu
        await message.reply("Данного блюда нет в меню, попробуйте снова!")
        return
    else:
        if menu_get_photo(message.text[:-1]) != "":  # in case of existing the image of the meal
            await bot.send_photo(message.chat.id, photo=menu_get_photo(message.text[:-1]),
                                 caption=f"\"{current_meal}\"\nОписание: {menu[current_meal][0]}\n\n💸 Цена: {menu[current_meal][1]} сум")
        else:  # not sending the photo
            await bot.send_message(message.chat.id,
                                   f"\"{current_meal}\"\nОписание: {menu[current_meal][0]}\n\n💸 Цена: {menu[current_meal][1]} сум")
        await message.reply("Добавить данное блюдо в корзину?", reply_markup=confirm_keyboard)
        await OrderFood.confirm.set()


# adding meal to the cart
async def confirm(message: types.Message):
    global current_meal
    if message.text == "◀Назад":
        return
    elif message.text == "Подтвердить":
        await bot.delete_message(message.chat.id,
                                 message.message_id - 2)  # deleting image of the food in order not to excessive number of photos
        cart_update(message.from_user.id, current_meal)  # adding new item to the cart
        await message.reply(
            f"📥 Блюдо \"{current_meal}\" было успешно добавлено в корзину!\n\nХотите заказать еду из вашей корзины или продолжить ее собирать?",
            reply_markup=full_cart_keyboard)
        await OrderFood.continue_or_order.set()


# choosing to continue or to order the food in the cart
async def cont_ord(message: types.Message):
    cart = cart_get(message.from_user.id)
    set_cart = list(set(cart))
    if message.text == full_cart_keyboard.labels[0]:  # cart
        final_cart = [f"{i + 1}. *{set_cart[i]}*\n{cart.count(set_cart[i])} x {menu[set_cart[i]][1]}\n\n" for i in
                      range(len(set_cart))]  # cool alg to group all selected products and their prices from cart
        await message.reply(f"*🛒 Корзина*:\n\n{''.join(final_cart)}\n🧾Итого: {sum([menu[x][1] for x in cart])} сум",
                            parse_mode="Markdown",
                            reply_markup=order_keyboard)  # list of the items added to the cart (receipt)
        await OrderFood.order_food.set()
    elif message.text == full_cart_keyboard.labels[1]:  # back to the menu
        await message.reply("Выберите еще что-нибудь:", reply_markup=menu_keyboard)
        await OrderFood.on_menu.set()


# ordering the food from the cart
async def cart_order(message: types.Message):
    if message.text == order_keyboard.labels[0]:  # confirn the order
        await message.reply("Выберите способ оплаты: ", reply_markup=payment_keyboard)
        await OrderFood.payment.set()
    elif message.text == order_keyboard.labels[1]:  # editing cart
        ReplyKeyboardRemove()
        cart = cart_get(message.from_user.id)
        if not cart:  # is there is no items in the cart
            await message.reply("Хмм, кажется вы забыли добавить еду в корзину:)", reply_markup=order_keyboard)
        else:
            cart_keyboard = Inline_kb([f"❌ {meal}" for meal in [cart[x] for x in range(len(cart))]]).add(Inline("Подтвердить"))  # creating dinamic inline keyboard so that it could be changed after deleting some items
            await message.reply("Удалите ненужное: ", reply_markup=cart_keyboard)
            # print(message.message_id)
            # await bot.edit_message_text("Удалите ненужное:", message.chat.id, message.message_id - 1, reply_markup=ReplyKeyboardRemove())
            await OrderFood.edit_cart.set()
    elif message.text == order_keyboard.labels[2]:  # back the main menu
        await message.reply("Меню", reply_markup=menu_keyboard)
        await OrderFood.on_menu.set()


# removing meals from the cart
async def edit_cart(call):
    if call.data == "Подтвердить":
        deleted = cart_deleted_list(call.from_user.id)
        if not deleted:
            await call.message.edit_text(f"Корзина осталась прежней")
            await bot.send_message(call.from_user.id, "Выберите действие: ", reply_markup=order_keyboard)
        else:
            await call.message.edit_text(f"Блюда(о) *{' '.join(deleted)[:-1]}* были удалены из вашей корзины",
                                         parse_mode="Markdown")
            await bot.send_message(call.from_user.id, "Выберите действие: ", reply_markup=order_keyboard)
        cart_deleted_reset(call.from_user.id)
        await OrderFood.order_food.set()
    else:  # if call data is equal to one of the meals
        meal = call.data[2:]
        cart_remove(call.from_user.id, meal)
        await call.answer(f"Блюдо \"{meal}\" было удалено из корзины!", show_alert=True)
        set_cart = cart_get(call.from_user.id)
        if not set_cart:  # if there is at least one meal in the cart
            deleted = cart_deleted_list(call.from_user.id)
            print(deleted)
            if not deleted:
                await call.message.edit_text(f"Корзина осталась прежней")
            else:
                await call.message.edit_text(f"Блюда(о) *{' '.join(deleted)[:-1]}* были удалены из вашей корзины",
                                             parse_mode="Markdown")
                cart_deleted_reset(call.from_user.id)
                await OrderFood.order_food.set()
        else:
            cart_keyboard = Inline_kb([f"❌ {meal}" for meal in [set_cart[x] for x in range(len(set_cart))]]).add(Inline("Подтвердить"))  # update the inline keyboard so that it will change after a certain meal was deleted
            await call.message.edit_text("Удалите ненужное: ", reply_markup=cart_keyboard)  # edit inline keyboard
            cart_deleted_update(call.from_user.id, meal)  # update the list of meals that were deleted from the cart


# food payment
async def pay(message: types.Message):
    cart = cart_get(message.from_user.id)
    set_cart = list(set(cart))
    price = sum([menu[x][1] for x in cart])  # final price of all the meals in the cart
    if price > 0:
        profile_find(message.from_user.id)
        if message.text == payment_keyboard.labels[0]:  # order goes directly to the canteen staff and payment is made manually with cash
            profile = profile_find(message.from_user.id)
            final_cart = [f"{i + 1}. *{set_cart[i]}*\n{cart.count(set_cart[i])} x {menu[set_cart[i]][1]}\n\n" for i in
                          range(
                              len(set_cart))]  # cool alg to group all selected products and their prices from the cart
            await bot.send_message(message.from_user.id,
                                   f"✅ Заказ был передан администрации столовой на обработку, можете забрать его на большой перемене после совершения oплаты в размере *{price} сум* в кассу столовой)\n\nБлагодарим, что использовали бота для заказа еды:)",
                                   reply_markup=init_keyboard, parse_mode="Markdown")
            await bot.send_message(service,
                                   f"🛎 Поступил новый заказ:\n\n*{profile['name']} {profile['surname']}* из группы *{profile['group']}* заказал:\n\n{''.join(final_cart)}\nНа сумму: {price}сум",
                                   parse_mode="Markdown")
            cart_clear(message.from_user.id)
            await OrderFood.init.set()
        elif message.text == payment_keyboard.labels[1]:
            PRICES = [types.LabeledPrice(label=set_cart[i], amount=menu[set_cart[i]][1] * 100) for i in
                      range(len(set_cart))]  # cool alg to arrange every meal and its price from the cart

            if PAYMENT_PROVIDER_TOKEN.split(":")[1] == "TEST":
                await bot.send_message(message.chat.id,
                                       "Bot is in test mode, no real money is involved in the following operations")
            await bot.send_invoice(
                message.chat.id,
                title="Еда из корзины",
                description=''.join([f"{set_cart[i]} " for i in range(len(set_cart))]),
                provider_token=PAYMENT_PROVIDER_TOKEN,
                currency="uzs",
                photo_url="https://upload.wikimedia.org/wikipedia/commons/6/6d/Good_Food_Display_-_NCI_Visuals_Online.jpg",
                photo_height=256,
                photo_width=512,
                photo_size=512,
                is_flexible=False,
                prices=PRICES,
                start_parameter="payment_test",
                payload="i_wish_i_knew_what_does_it_mean"
            )
    else:
        await message.reply("Хмм, кажется вы забыли добавить еду в корзину:)")


async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


# in case of successfull payment
async def process_successful_payment(message: types.Message):
    print('successful_payment:')
    pmnt = message.successful_payment.to_python()  # payment components
    for key, val in pmnt.items():
        print(f'{key} = {val}')

    await bot.send_message(message.chat.id,
                           f"✅ Оплата в размере *{message.successful_payment.total_amount // 100}* сум прошла успешно, можете забрать свой заказ на большой перемене в столовой.\n\nP.S правила возврата средств смотрите в /terms",
                           parse_mode="Markdown", reply_markup=init_keyboard)
    await OrderFood.init.set()
    cart = cart_get(message.from_user.id)
    set_cart = list(set(cart))
    price = sum([menu[x][1] for x in cart])
    profile = profile_find(message.from_user.id)
    final_cart = [f"{i + 1}. *{set_cart[i]}*\n{cart.count(set_cart[i])} x {menu[set_cart[i]][1]}\n\n" for i in
                  range(len(set_cart))]  # cool alg to group all selected products and their prices from cart
    await bot.send_message(service,
                           f"🛎 Поступил новый заказ:\n\n*{profile['name']} {profile['surname']}* из группы *{profile['group']}* заказал:\n{''.join(final_cart)}\nНа сумму: {price}сум\nОплата была произведена через CLICK.",
                           parse_mode="Markdown")

    cart_clear(message.from_user.id)


# register the handlers
def register_menu_handlers(dp: Dispatcher):
    dp.register_message_handler(order, state=OrderFood.on_menu)
    dp.register_message_handler(send_meal, state=OrderFood.waiting_for_food)
    dp.register_message_handler(confirm, state=OrderFood.confirm)
    dp.register_message_handler(cont_ord, state=OrderFood.continue_or_order)
    dp.register_message_handler(cart_order, state=OrderFood.order_food)
    dp.register_callback_query_handler(edit_cart, state=OrderFood.edit_cart)
    dp.register_message_handler(pay, state=OrderFood.payment)
    dp.register_pre_checkout_query_handler(process_pre_checkout_query, lambda query: True, state=OrderFood.payment)
    dp.register_message_handler(process_successful_payment, state=OrderFood.payment,
                                content_types=ContentType.SUCCESSFUL_PAYMENT)
>>>>>>> 2b4e0576a6bb5ad7557b0d37e51b800ea9e6a1f8
