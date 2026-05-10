from aiogram import Router, F
from aiogram.types import CallbackQuery

from database import get_user, update_invite_status, get_invite
from keyboards import kb_main_menu

router = Router()


@router.callback_query(F.data.startswith("inv_accept:"))
async def cb_accept(cb: CallbackQuery):
    inviter_id = int(cb.data.split(":")[1])
    receiver   = await get_user(cb.from_user.id)
    inviter    = await get_user(inviter_id)
    if not inviter or not receiver:
        await cb.answer("Профиль не найден")
        return
    invite = await get_invite(inviter_id, cb.from_user.id)
    if not invite or invite["status"] != "pending":
        await cb.answer("Инвайт уже обработан")
        return
    await update_invite_status(inviter_id, cb.from_user.id, "accepted")
    await cb.answer("🎉 Матч!")
    await cb.message.delete()
    contact = f"@{inviter['username']}" if inviter.get("username") else f"Напиши первым"
    await cb.message.answer(
        f"🎉 <b>Матч!</b>\n\nКонтакт {inviter['name']}: {contact}\n\nУдачной игры! 🏆",
        parse_mode="HTML", reply_markup=kb_main_menu()
    )
    try:
        contact2 = f"@{receiver['username']}" if receiver.get("username") else "Напиши первым"
        await cb.bot.send_message(
            inviter_id,
            f"🎉 <b>{receiver['name']} принял твой инвайт!</b>\n\nКонтакт: {contact2}\n\nУдачной игры! 🏆",
            parse_mode="HTML", reply_markup=kb_main_menu()
        )
    except Exception:
        pass


@router.callback_query(F.data.startswith("inv_decline:"))
async def cb_decline(cb: CallbackQuery):
    inviter_id = int(cb.data.split(":")[1])
    invite = await get_invite(inviter_id, cb.from_user.id)
    if not invite or invite["status"] != "pending":
        await cb.answer("Инвайт уже обработан")
        return
    await update_invite_status(inviter_id, cb.from_user.id, "declined")
    await cb.answer("Отклонено")
    await cb.message.delete()
    await cb.message.answer("Листай дальше 👇", reply_markup=kb_main_menu())
    try:
        await cb.bot.send_message(inviter_id, "😔 Игрок отклонил инвайт. Листай дальше! 🎾",
                                  reply_markup=kb_main_menu())
    except Exception:
        pass
