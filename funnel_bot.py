import os
import logging
import asyncio
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO)

TOKEN = os.environ.get("TELEGRAM_TOKEN", "")

LESSON_TEXT = """🎓 *РАЗБОР. ПОЧЕМУ БЛОГ НЕ ПРОДАЕТ*

В этом уроке я разбираю:
— почему одинаковые специалисты продают по-разному
— почему красивый блог ≠ бренд, которому платят
— и что именно создаёт ощущение ценности ещё до того, как человек прочитал хоть одно слово о ваших услугах

👇 Смотрите урок по ссылке:"""

BUY_URL = "https://example.com/buy"
VIDEO_URL = "https://youtube.com/your_video"

REMINDERS = [
    (3600,  "⏰ Вы посмотрели урок?\n\nСамое время — пока открыто место на программе 👇"),
    (86400, "💡 Один вопрос: что мешает покупать у себя?\n\nРазберём это на программе 👇"),
    (172800,"🚪 Последнее напоминание.\n\nЗакрываю набор завтра. Успейте 👇"),
]

async def send_reminder(chat_id: int, text: str, bot):
    try:
        await bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("Купить программу", url=BUY_URL)
            ]])
        )
    except Exception as e:
        logging.error(f"Ошибка: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    bot = context.bot

    await update.message.reply_text(
        LESSON_TEXT,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("СМОТРЕТЬ УРОК", url=VIDEO_URL)],
            [InlineKeyboardButton("КУПИТЬ ПРОГРАММУ", url=BUY_URL)],
        ])
    )

    async def schedule():
        for delay, text in REMINDERS:
            await asyncio.sleep(delay)
            await send_reminder(chat_id, text, bot)

    asyncio.create_task(schedule())

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()

if __name__ == "__main__":
    main()
