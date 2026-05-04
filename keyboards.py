from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from config import SPORTS, LEVELS, TIMES, GENDERS, LOOKING_FOR


def kb_remove():
    return ReplyKeyboardRemove()


def kb_sports() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    for s in SPORTS:
        builder.button(text=s)
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


def kb_levels() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    for l in LEVELS:
        builder.button(text=l)
    builder.adjust(3)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


def kb_times() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    for t in TIMES:
        builder.button(text=t)
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


def kb_genders() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    for g in GENDERS:
        builder.button(text=g)
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


def kb_looking_for() -> ReplyKeyboardMarkup:
    """Кого ищешь перед свайпом."""
    builder = ReplyKeyboardBuilder()
    for lf in LOOKING_FOR:
        builder.button(text=lf)
    builder.adjust(3)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


def kb_skip_photo() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="⏭ Пропустить фото")
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


def kb_main_menu() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="🎾 Искать партнёра")
    builder.button(text="👤 Мой профиль")
    builder.button(text="✏️ Изменить профиль")
    builder.button(text="🔕 Скрыть меня")
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


def kb_swipe_card(candidate_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="❌ Пропустить", callback_data=f"pass:{candidate_id}")
    builder.button(text="✅ Позвать играть", callback_data=f"like:{candidate_id}")
    builder.adjust(2)
    return builder.as_markup()


def kb_invite_response(from_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Принять", callback_data=f"inv_accept:{from_id}")
    builder.button(text="❌ Отклонить", callback_data=f"inv_decline:{from_id}")
    builder.adjust(2)
    return builder.as_markup()
