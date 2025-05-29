from aiogram.types import Message

async def delete_hist(message: Message):
    try:
        await message.delete()
        await message.bot.delete_message(message.chat.id, message.message_id - 1)
    except Exception as e:
        pass