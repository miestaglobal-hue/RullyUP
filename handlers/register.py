from database import upsert_user, mirror_to_sheets
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import SPORTS, LEVELS, TIMES, GENDERS
from database import upsert_user
from keyboards import kb_sports, kb_levels, kb_times, kb_genders, kb_skip_photo, kb_main_menu, kb_remove

router = Router()


class RegState(StatesGroup):
    name      = State()
    gender    = State()
    sport     = State()
    level     = State()
    city      = State()
    play_time = State()
    photo     = State()


@router.message(F.text == "✏️ Изменить профиль")
async def edit_profile(msg: Message, state: FSMContext):
    await cmd_register(msg, state)


async def cmd_register(msg: Message, state: FSMContext):
    await state.clear()
    await state.set_state(RegState.name)
    await msg.answer("📝 Как тебя зовут?", reply_markup=kb_remove())


@router.message(RegState.name)
async def step_name(msg: Message, state: FSMContext):
    if len(msg.text.strip()) < 2:
        await msg.answer("Введи имя длиннее 1 символа 😅")
        return
    await state.update_data(name=msg.text.strip())
    await state.set_state(RegState.gender)
    await msg.answer("Ты парень или девушка?", reply_markup=kb_genders())


@router.message(RegState.gender, F.text.in_(GENDERS))
async def step_gender(msg: Message, state: FSMContext):
    await state.update_data(gender=msg.text)
    await state.set_state(RegState.sport)
    await msg.answer("Во что играешь?", reply_markup=kb_sports())


@router.message(RegState.gender)
async def step_gender_invalid(msg: Message):
    await msg.answer("Выбери из кнопок 👇", reply_markup=kb_genders())


@router.message(RegState.sport, F.text.in_(SPORTS))
async def step_sport(msg: Message, state: FSMContext):
    await state.update_data(sport=msg.text)
    await state.set_state(RegState.level)
    await msg.answer("Какой у тебя уровень?", reply_markup=kb_levels())


@router.message(RegState.sport)
async def step_sport_invalid(msg: Message):
    await msg.answer("Выбери из кнопок 👇", reply_markup=kb_sports())


@router.message(RegState.level, F.text.in_(LEVELS))
async def step_level(msg: Message, state: FSMContext):
    await state.update_data(level=msg.text)
    await state.set_state(RegState.city)
    await msg.answer("В каком городе ищешь партнёра?", reply_markup=kb_remove())


@router.message(RegState.level)
async def step_level_invalid(msg: Message):
    await msg.answer("Выбери из кнопок 👇", reply_markup=kb_levels())


@router.message(RegState.city)
async def step_city(msg: Message, state: FSMContext):
    await state.update_data(city=msg.text.strip())
    await state.set_state(RegState.play_time)
    await msg.answer("Когда обычно играешь?", reply_markup=kb_times())


@router.message(RegState.play_time, F.text.in_(TIMES))
async def step_time(msg: Message, state: FSMContext):
    await state.update_data(play_time=msg.text)
    await state.set_state(RegState.photo)
    await msg.answer("📸 Загрузи фото профиля или пропусти.", reply_markup=kb_skip_photo())


@router.message(RegState.play_time)
async def step_time_invalid(msg: Message):
    await msg.answer("Выбери из кнопок 👇", reply_markup=kb_times())


@router.message(RegState.photo, F.photo)
async def step_photo(msg: Message, state: FSMContext):
    await _finish_registration(msg, state, msg.photo[-1].file_id)


@router.message(RegState.photo, F.text == "⏭ Пропустить фото")
async def step_photo_skip(msg: Message, state: FSMContext):
    await _finish_registration(msg, state, None)


@router.message(RegState.photo)
async def step_photo_invalid(msg: Message):
    await msg.answer("Отправь фото или нажми «⏭ Пропустить фото»", reply_markup=kb_skip_photo())


async def _finish_registration(msg: Message, state: FSMContext, photo_id):
    data = await state.get_data()
    data["photo_id"] = photo_id
    data["looking_for"] = "👥 Всех"
    await upsert_user(msg.from_user.id, msg.from_user.username or "", data)
   async def _finish_registration(msg: Message, state: FSMContext, photo_id):
    data = await state.get_data()
    data["photo_id"] = photo_id
    data["looking_for"] = "👥 Всех"
    await upsert_user(msg.from_user.id, msg.from_user.username or "", data)
    await mirror_to_sheets(msg.from_user.id, msg.from_user.username or "", data)
    await state.clear()
    await msg.answer(
        f"✅ <b>Профиль создан!</b>\n\n"
        f"👤 {data['name']} ({data['gender']})\n"
        f"🏅 {data['sport']} · {data['level']}\n"
        f"📍 {data['city']}\n"
        f"🕐 {data['play_time']}\n\n"
        f"Нажми <b>«🎾 Искать партнёра»</b> — начнём!",
        parse_mode="HTML",
        reply_markup=kb_main_menu()
    )
