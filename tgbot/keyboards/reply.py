from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton

contact_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton(text="Raqamni yuborish 📲", request_contact=True))

remove_kb = ReplyKeyboardRemove()
