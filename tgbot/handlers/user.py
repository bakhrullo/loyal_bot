import asyncio

import aiohttp
import yarl
import aiofiles

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery

from tgbot.config import Config
from tgbot.db.db_api import get, post, patch
from tgbot.filters.back import BackFilter
from tgbot.keyboards.inline import menu_kb, constructor_kb, conf_kb, back_kb, settings_kb
from tgbot.keyboards.reply import contact_kb, remove_kb
from tgbot.misc.states import Start, Menu, Prods, Bonus, Comment, Settings, News


async def user_start(m: Message, status: bool):
    if status:
        await m.answer("Bosh menu ga xush kelibsiz! Pastdagi tugmalar orqali kerakli buyruqni tanlang👇",
                       reply_markup=menu_kb)
        return await Menu.get_menu.set()
    await m.reply("Assalomu alaykum! 👋\n"
                  "Hyosung botiga xush kelibsiz Iltimos ism, sharifingizni kiriting")
    await Start.get_name.set()


async def get_name(m: Message, state: FSMContext):
    await state.update_data(name=m.text)
    await m.answer(
        "Iltimos telefon raqamingizni (+998901234567) tarzda kiriting yoki pastdagi tugmacha "
        "orqali raqamingiz bilan ulashing", reply_markup=contact_kb)
    await Start.next()


async def get_phone(m: Message, state: FSMContext, config: Config):
    data = await state.get_data()
    phone = m.contact.phone_number if m.content_type == "contact" else m.text
    await post(url=f"{config.db.db_url}user/create",
               data={"name": data["name"], "phone": phone, "tg_id": m.from_user.id})
    await m.answer("Siz muvoffaqiyatli ro'yhatdan o'tdingiz ✅", reply_markup=remove_kb)
    await m.answer("Bosh menu ga xush kelibsiz! Pastdagi tugmalar orqali kerakli buyruqni tanlang👇",
                   reply_markup=menu_kb)
    await Menu.get_menu.set()


async def wallet(c: CallbackQuery, user: dict):
    await c.message.edit_text(f"👤: {user['name']}\n"
                              f"💰: {user['point']} ball", reply_markup=back_kb)


async def bonus(c: CallbackQuery):
    await c.message.edit_text("Bonus ko'dni kiriting", reply_markup=back_kb)
    await Bonus.get_code.set()


async def get_code(m: Message, config: Config):
    res = await get(f"{config.db.db_url}bonus", params={"tg_id": m.from_user.id,
                                                        "code": m.text})
    if res["status"] == "Not found":
        return await m.answer("Notog'ri kod kiritildi ❌\nIltimos tekshirib qayta kiriting", reply_markup=back_kb)
    elif res["status"] == "In use":
        return await m.answer("Kod eskirgan", reply_markup=back_kb)
    await m.answer("Kod qabul qilindi ✅", reply_markup=menu_kb)
    await Menu.get_menu.set()


async def news(c: CallbackQuery, config: Config):
    text, res = "", await get(f"{config.db.db_url}news")
    if not len(res):
        return await c.answer("Yangiliklar yo'q ❌")
    for count, content in enumerate(res, start=1):
        text += f"{count}) {content['name']}"
    await c.message.edit_text(text=text, reply_markup=constructor_kb(res))
    await News.get_news.set()


async def get_news(c: CallbackQuery, config: Config):
    res = await get(f"{config.db.db_url}news/{c.data}")
    await c.message.delete()
    await c.message.answer_photo(photo=res["photo"], caption=res["descr"], reply_markup=back_kb)


async def comment(c: CallbackQuery):
    await c.message.edit_text("Iltimos o'z izohingizni shu yerda yozib qoldiring 📝\n"
                              "Mutaxassislarimiz o'rganib chiqib tez orada sizga javob berishadi 👨‍💻",
                              reply_markup=back_kb)
    await Comment.get_comment.set()


async def get_comment(m: Message, config: Config, user: dict):
    await m.bot.send_message(config.misc.group_id, f"👤: {user['name']}\n"
                                                   f"📱: {user['phone']}\n"
                                                   f"💬: {m.text}")
    await m.answer("Qabnul qilindi✅\n"
                   "Tez orada xodimlarimiz siz bilan bog\' lanishadi👨‍💻", reply_markup=menu_kb)
    await Menu.get_menu.set()


async def settings(c: CallbackQuery):
    await c.message.edit_text("Sozlamalar bo'limida siz Telefon raqamingizni o'zgartirishingiz mumkin",
                              reply_markup=settings_kb)
    await Settings.get_type.set()


async def change_phone(c: CallbackQuery):
    await c.message.delete()
    await c.message.answer("Iltimos telefon raqamingizni (+998901234567) tarzda kiriting yoki pastdagi tugmacha"
                           "orqali raqamingiz bilan ulashing", reply_markup=contact_kb)
    await Settings.next()


async def get_change_phone(m: Message, config: Config):
    phone = m.contact.phone_number if m.content_type == "contact" else m.text
    await patch(f"{config.db.db_url}user/update/{m.from_user.id}", data={"phone": phone})
    await m.answer("Raqamingiz o'zgartirildi ✅", reply_markup=menu_kb)
    await Menu.get_menu.set()


async def prods(c: CallbackQuery, config: Config):
    res = await get(url=f"{config.db.db_url}prods")
    if not len(res):
        return await c.answer("Tovarlar qo'shilmagan ❌")
    await c.message.edit_text("Siz ushbu bo'limda mahsulotlarni ko'rib uni xarid qilishingiz mumkin",
                              reply_markup=constructor_kb(data=res))
    await Prods.get_prod.set()


async def get_prod(c: CallbackQuery, config: Config, state: FSMContext):
    res = await get(url=f"{config.db.db_url}prods/{c.data}")
    await state.update_data(prod=res)
    if not len(res):
        return await c.answer("Diametr qo'shilmagan ❌")
    await c.message.edit_text("Trubaning diametrini tanlang👇",
                              reply_markup=constructor_kb(data=res["type"], option=False))
    await Prods.next()


async def get_mm(c: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await state.update_data(mm=data['prod']['type'][int(c.data)]['name'], price=data['prod']['type'][int(c.data)]['price'])
    await c.message.edit_text(f"{data['prod']['name']} {data['prod']['type'][int(c.data)]['name']}\n"
                              f"{data['prod']['descr']}\n"
                              f"Ushbu trubaning narxi: {data['prod']['type'][int(c.data)]['price']} so'm\n"
                              f"nechta xarid qilmoxchisiz?", reply_markup=back_kb)
    await Prods.next()


async def get_count(m: Message, state: FSMContext):
    if not m.text.isdigit():
        return await m.answer("Iltimos sonda yuboring ❌")
    data = await state.get_data()
    await state.update_data(count=m.text)
    await m.answer(f"Siz {m.text} ta truba xarid qilishni amalga oshirmoxchisiz\n"
                   f"Narxi {data['price'] * int(m.text)} so'm bo'ladi\n"
                   f"Buyurtmani amalga oshirish uchun pastdagi tugmachalardan foydalaning👇",
                   reply_markup=conf_kb)
    await Prods.next()


async def get_conf(c: CallbackQuery, state: FSMContext, config: Config, user: dict):
    data = await state.get_data()
    await c.bot.send_message(config.misc.group_id, f"👤: {user['name']}\n"
                                                   f"📱: {user['phone']}\n"
                                                   f"📦: {data['prod']['name']} {data['mm']}\n"
                                                   f"📥: {data['count']} dona")
    await c.message.edit_text("Tasdiqlash muvoffaqiyatli amalga oshirldi✅\n"
                              "Tez orada xodimlarimiz siz bilan bog\' lanishadi👨‍💻", reply_markup=menu_kb)
    await Menu.get_menu.set()


async def back(c: CallbackQuery):
    await c.message.delete()
    await c.message.answer("Bosh menu ga xush kelibsiz! Pastdagi tugmalar orqali kerakli buyruqni tanlang👇",
                           reply_markup=menu_kb)
    return await Menu.get_menu.set()


def register_user(dp: Dispatcher):
    dp.register_message_handler(user_start, commands=["start"], state="*")
    dp.register_message_handler(get_name, state=Start.get_name)
    dp.register_message_handler(get_phone, content_types=["contact", "text"], state=Start.get_number)
    dp.register_message_handler(get_change_phone, content_types=["contact", "text"], state=Settings.get_phone)
    dp.register_message_handler(get_code, state=Bonus.get_code)
    dp.register_message_handler(get_count, state=Prods.get_count)
    dp.register_callback_query_handler(wallet, Text(equals="wallet"), state=Menu.get_menu)
    dp.register_callback_query_handler(prods, Text(equals="prods"), state=Menu.get_menu)
    dp.register_callback_query_handler(bonus, Text(equals="bonus"), state=Menu.get_menu)
    dp.register_callback_query_handler(news, Text(equals="news"), state=Menu.get_menu)
    dp.register_callback_query_handler(comment, Text(equals="comment"), state=Menu.get_menu)
    dp.register_callback_query_handler(settings, Text(equals="settings"), state=Menu.get_menu)
    dp.register_callback_query_handler(change_phone, BackFilter(), state=Settings.get_type)
    dp.register_callback_query_handler(get_comment, BackFilter(), state=Comment.get_comment)
    dp.register_callback_query_handler(get_news, BackFilter(), state=News.get_news)
    dp.register_callback_query_handler(get_prod, BackFilter(), state=Prods.get_prod)
    dp.register_callback_query_handler(get_mm, BackFilter(), state=Prods.get_mm)
    dp.register_callback_query_handler(get_conf, BackFilter(), state=Prods.get_conf)
    dp.register_callback_query_handler(back, state="*")
