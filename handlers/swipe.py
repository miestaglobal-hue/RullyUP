from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove

from config import LOOKING_FOR
from database import get_user, get_next_candidate, record_swipe, create_invite
from keyboards import kb_looking_for, kb_swipe_card, kb_main_menu

router = Router()


class SwipeState(StatesGroup):
    choosing_gender = State()
    swiping         = State()


@router.message(F.text == "🎾 Искать партнёра")
async def start_swiping(msg: Message, state: FSMContext):
    user = await get_user(msg.from_user.id)
    if not user:
        await msg.answer("Сначала создай профиль — нажми /start", reply_markup=kb_main_menu())
        return
    await state.set_state(SwipeState.choosing_gender)
    await msg.answer("🔍 Кого ищешь?", reply_markup=kb_looking_for())


@router.message(SwipeState.choosing_gender, F.text.in_(LOOKING_FOR))
async def gender_chosen(msg: Message, state: FSMContext):
    await state.update_data(looking_for=msg.text)
    await state.set_state(SwipeState.swiping)
    await msg.answer("✅ Листай карточки!", reply_markup=ReplyKeyboardRemove())
    await show_next_card(msg, state)


@router.message(SwipeState.choosing_gender)
async def gender_invalid(msg: Message):
    await msg.answer("Выбери из кнопок 👇", reply_markup=kb_looking_for())


async def show_next_card(msg_or_query, state: FSMContext):
    is_cb = isinstance(msg_or_query, CallbackQuery)
    tg_id = msg_or_query.from_user.id
    send  = msg_or_query.message if is_cb else msg_or_query
    data  = await state.get_data()
    looking_for = data.get("looking_for", "👥 Всех")
    candidate = await get_next_candidate(tg_id, looking_for)
    if not candidate:
        await send.answer("😔 Пока нет игроков. Попробуй позже!", reply_markup=kb_main_menu())
        await state.clear()
        return
    caption = (
        f"<b>{candidate['name']}</b>\n\n"
        f"{candidate['sport']} · {candidate['level']}\n"
        f"📍 {candidate['city']}\n"
        f"🕐 {candidate['play_time']}"
    )
    if candidate.get("photo_id"):
        await send.answer_photo(candidate["photo_id"], caption=caption, parse_mode="HTML",
                                reply_markup=kb_swipe_card(candidate["tg_id"]))
    else:
        await send.answer(caption, parse_mode="HTML", reply_markup=kb_swipe_card(candidate["tg_id"]))


@router.callback_query(F.data.startswith("pass:"), SwipeState.swiping)
async def cb_pass(cb: CallbackQuery, state: FSMContext):
    candidate_id = int(cb.data.split(":")[1])
    await record_swipe(cb.from_user.id, candidate_id, "pass")
    await cb.answer("Пропущено")
    await cb.message.delete()
    await show_next_card(cb, state)


@router.callback_query(F.data.startswith("like:"), SwipeState.swiping)
async def cb_like(cb: CallbackQuery, state: FSMContext):
    candidate_id = int(cb.data.split(":")[1])
    viewer    = await get_user(cb.from_user.id)
    candidate = await get_user(candidate_id)
    if not candidate:
        await cb.answer("Игрок недоступен")
        await show_next_card(cb, state)
        return
    await record_swipe(cb.from_user.id, candidate_id, "like")
    created = await create_invite(cb.from_user.id, candidate_id)
    await cb.answer("✅ Инвайт отправлен!")
    await cb.message.delete()
    if created:
        text = (
            f"🎾 <b>Тебя хотят позвать играть!</b>\n\n"
            f"<b>{viewer['name']}</b>\n"
            f"{viewer['sport']} · {viewer['level']}\n"
            f"📍 {viewer['city']}\n\nПринять?"
        )
        from keyboards import kb_invite_response
        try:
            if viewer.get("photo_id"):
                await cb.bot.send_photo(candidate_id, viewer["photo_id"], caption=text,
                                        parse_mode="HTML", reply_markup=kb_invite_response(cb.from_user.id))
            else:
                await cb.bot.send_message(candidate_id, text, parse_mode="HTML",
                                          reply_markup=kb_invite_response(cb.from_user.id))
        except Exception:
            pass
    await cb.message.answer(f"📨 Инвайт отправлен {candidate['name']}! Уведомлю когда ответит 🔔",
                            reply_markup=ReplyKeyboardRemove())
    await show_next_card(cb, state)
