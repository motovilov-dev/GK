from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Update
from loguru import logger
import sentry_sdk


class LoggingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        # Логируем входящее обновление
        update_type = event.event_type
        logger.info(f"⬇️ Incoming update | Type: {update_type}")

        try:
            # Логируем информацию в зависимости от типа обновления
            if update_type == "message":
                message = event.message
                logger.info(
                    f"✉️ Message | Chat ID: {message.chat.id} | "
                    f"User ID: {message.from_user.id} | "
                    f"Text: {message.text or '<no text>'}"
                )
            elif update_type == "callback_query":
                callback = event.callback_query
                logger.info(
                    f"🖱 Callback | Chat ID: {callback.message.chat.id if callback.message else 'None'} | "
                    f"User ID: {callback.from_user.id} | "
                    f"Data: {callback.data}"
                )
            elif update_type == "inline_query":
                inline_query = event.inline_query
                logger.info(
                    f"🔍 Inline Query | User ID: {inline_query.from_user.id} | "
                    f"Query: {inline_query.query}"
                )
            elif update_type == "chosen_inline_result":
                chosen_result = event.chosen_inline_result
                logger.info(
                    f"✅ Chosen Inline Result | User ID: {chosen_result.from_user.id} | "
                    f"Result ID: {chosen_result.result_id}"
                )
            elif update_type == "pre_checkout_query":
                checkout_query = event.pre_checkout_query
                logger.info(
                    f"💳 Pre Checkout Query | User ID: {checkout_query.from_user.id} | "
                    f"Amount: {checkout_query.total_amount / 100} {checkout_query.currency}"
                )
            elif update_type == "poll_answer":
                poll_answer = event.poll_answer
                logger.info(
                    f"📊 Poll Answer | User ID: {poll_answer.user.id} | "
                    f"Poll ID: {poll_answer.poll_id}"
                )
            elif update_type == "chat_member":
                chat_member = event.chat_member
                logger.info(
                    f"👥 Chat Member Update | Chat ID: {chat_member.chat.id} | "
                    f"User ID: {chat_member.from_user.id} | "
                    f"New status: {chat_member.new_chat_member.status}"
                )
            elif update_type == "my_chat_member":
                my_chat_member = event.my_chat_member
                logger.info(
                    f"🤖 Bot Chat Member Update | Chat ID: {my_chat_member.chat.id} | "
                    f"New status: {my_chat_member.new_chat_member.status}"
                )
            else:
                logger.info(f"ℹ️ Other update type: {update_type} | Data: {event.model_dump_json(indent=2)}")

            # Вызываем следующий обработчик
            sentry_sdk.profiler.start_profiler()
            result = await handler(event, data)
            sentry_sdk.profiler.stop_profiler()

            # Логируем успешное завершение обработки
            logger.success(f"✅ Successfully processed {update_type} update")
            return result

        except Exception as e:
            # Логируем ошибку при обработке
            logger.error(f"❌ Error processing {update_type} update: {e}")
            raise