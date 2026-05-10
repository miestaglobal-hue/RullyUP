from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from database import get_user, set_user_active
from keyboards import kb_main_menu

router = Router()


@router.message(CommandStart())
async def cmd_start(msg: Message, state: FSMContext):
    await state.clear()
    user = await get_user(msg.from_user.id)
    if user:
        await msg.answer(f"👋 С возвращением, {user['name']}!", reply_markup=kb_main_menu())
    else:
        await msg.answer(
            "🎾 Привет! Это <b>RallyUp</b> — находим тебе партнёра для тенниса или падела.\n\nДавай создадим твой профиль 👇",
            parse_mode="HTML", reply_markup=kb_main_menu()
        )
        from .register import cmd_register
        await cmd_register(msg, state)


@router.message(F.text == "👤 Мой профиль")
async def show_profile(msg: Message):
    user = await get_user(msg.from_user.id)
    if not user:
        await msg.answer("Сначала создай профиль — нажми /start")
        return
    status = "✅ Активен" if user["active"] else "🔕 Скрыт"
    text = (
        f"<b>Твой профиль</b>\n\n"
        f"👤 {user['name']} ({user['gender']})\n"
        f"🏅 {user['sport']} · {user['level']}\n"
        f"📍 {user['city']}\n"
        f"🕐 {user['play_time']}\n"
        f"📌 Статус: {status}"
    )
    if user.get("photo_id"):
        await msg.answer_photo(user["photo_id"], caption=text, parse_mode="HTML", reply_markup=kb_main_menu())
    else:
        await msg.answer(text, parse_mode="HTML", reply_markup=kb_main_menu())


@router.message(F.text == "🔕 Скрыть меня")
async def hide_profile(msg: Message):
    user = await get_user(msg.from_user.id)
    if not user:
        await msg.answer("Сначала создай профиль — нажми /start")
        return
    if user["active"]:
        await set_user_active(msg.from_user.id, False)
        await msg.answer("🔕 Профиль скрыт.", reply_markup=kb_main_menu())
    else:
        await set_user_active(msg.from_user.id, True)
        await msg.answer("✅ Профиль снова активен!", reply_markup=kb_main_menu())
