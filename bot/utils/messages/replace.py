from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup

async def call_replace_answer(call: CallbackQuery, text: str, reply_markup: InlineKeyboardMarkup) -> None:
    try:
        await call.message.edit_text(
            text=text,
            reply_markup=reply_markup,
        )
    except:
        try:
            await call.message.delete()
        except:
            pass
        await call.message.answer(
            text=text,
            reply_markup=reply_markup
        )