from typing import List

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

back_btn = InlineKeyboardButton("Orqaga 🔙", callback_data="back")

back_kb = InlineKeyboardMarkup(row_width=1).add(back_btn)

menu_kb = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton("Mahsulotlar 📦", callback_data="prods"),
                                                InlineKeyboardButton("Mening bonuslarim 💰", callback_data="wallet"),
                                                InlineKeyboardButton("Bonus kod 💸", callback_data="bonus"),
                                                InlineKeyboardButton("Yangiliklar 🗣", callback_data="news"),
                                                InlineKeyboardButton("Izoh qoldirish 💬", callback_data="feedback"),
                                                InlineKeyboardButton("Sozlamalar ⚙️", callback_data="settings"))

conf_kb = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton("Tasdiqlash ✅", callback_data="confirm"),
                                                back_btn)

settings_kb = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("Telefon raqam o'zgartirish 📲", callback_data="change"), back_btn)


def constructor_kb(data: List, option: bool = True) -> InlineKeyboardMarkup():
    btn = InlineKeyboardMarkup(row_width=1)
    for count, i in enumerate(data):
        btn.insert(InlineKeyboardButton(text=i["name"], callback_data=i["id"] if option else count))
    btn.insert(back_btn)
    return btn
