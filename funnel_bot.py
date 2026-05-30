"""
Telegram воронка-бот: бесплатный урок + серия напоминаний с продажей программы
Установка: pip install python-telegram-bot
Запуск:    python funnel_bot.py
"""

import logging
from datetime import timedelta
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
#  НАСТРОЙКИ — всё меняете здесь, код трогать не нужно
# ═══════════════════════════════════════════════════════════

TELEGRAM_TOKEN = "AAFiyRfjWTYB3nfXzAVWulZswb82Ti7oXgw"

# ── Бесплатный урок ──────────────────────────────────────
LESSON_TEXT = """
🎓 *Ваш бесплатный урок*

Привет! Я рада, что вы здесь.

В этом уроке вы узнаете:
• Почему на вас смотрят, но не покупают
• Как выглядит личный бренд с деньгами — и без
• Один сдвиг, который меняет всё

👇 Смотрите урок по ссылке:
"""

LESSON_VIDEO_URL   = "https://youtube.com/ВАШ_УРОК"   # ← ссылка на видео
LESSON_VIDEO_LABEL = "▶️ Смотреть урок"

# ── Ссылка на покупку программы ──────────────────────────
BUY_URL   = "https://example.com/buy"   # ← ссылка на оплату
BUY_LABEL = "🔥 Купить трёхдневную программу"

# ── Серия напоминаний ────────────────────────────────────
# delay — через сколько секунд после старта отправить
# (3600 = 1 час, 86400 = 24 часа, 172800 = 48 часов)

REMINDERS = [
    {
        "delay": 3600,   # через 1 час
        "text": """
⏰ *Вы посмотрели урок?*

Если ещё не успели — самое время.

А пока скажу главное: то, что я показываю в уроке — это только верхушка.
В трёхдневной программе мы разбираем *ваш конкретный случай* и выстраиваем образ, который продаёт.

Мест немного. Смотрите пока открыто 👇
""",
    },
    {
        "delay": 86400,  # через 24 часа
        "text": """
💡 *Один вопрос*

Что мешает вам покупать у себя самой?

Чаще всего — не цена. А то, как вы выглядите в глазах аудитории *до* того, как начинаете говорить.

Именно это мы разбираем на программе. За три дня.

Место ещё есть 👇
""",
    },
    {
        "delay": 172800, # через 48 часов
        "text": """
🚪 *Последнее напоминание*

Я закрываю набор завтра.

Если вы чувствуете, что тема резонирует — не откладывайте.
Следующего потока может не быть в ближайшие месяцы.

Успейте занять место 👇
""",
    },
]

# ═══════════════════════════════════════════════════════════
#  КОД БОТА
# ═══════════════════════════════════════════════════════════

def buy_button() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton(BUY_LABEL, url=BUY_URL)]])


def lesson_buttons() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(LESSON_VIDEO_LABEL, url=LESSON_VIDEO_URL)],
        [InlineKeyboardButton(BUY_LABEL, url=BUY_URL)],
    ])


async def send_reminder(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет одно напоминание из очереди."""
    job = context.job
    chat_id  = job.data["chat_id"]
    text     = job.data["text"]

    try:
        await context.bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=buy_button(),
            parse_mode="Markdown"
        )
        logger.info(f"Напоминание отправлено → {chat_id}")
    except Exception as e:
        logger.error(f"Ошибка отправки напоминания {chat_id}: {e}")


def schedule_reminders(context: ContextTypes.DEFAULT_TYPE, chat_id: int) -> None:
    """Ставит все напоминания в очередь."""
    for i, reminder in enumerate(REMINDERS):
        context.job_queue.run_once(
            send_reminder,
            when=timedelta(seconds=reminder["delay"]),
            data={"chat_id": chat_id, "text": reminder["text"].strip()},
            name=f"reminder_{chat_id}_{i}",
        )
    logger.info(f"Запланировано {len(REMINDERS)} напоминаний для {chat_id}")


def cancel_reminders(context: ContextTypes.DEFAULT_TYPE, chat_id: int) -> None:
    """Отменяет все напоминания (если человек уже купил)."""
    for i in range(len(REMINDERS)):
        jobs = context.job_queue.get_jobs_by_name(f"reminder_{chat_id}_{i}")
        for job in jobs:
            job.schedule_removal()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет урок и запускает серию напоминаний."""
    chat_id = update.effective_chat.id

    # Отменяем старые напоминания если человек нажал /start повторно
    cancel_reminders(context, chat_id)

    # Отправляем урок
    await update.message.reply_text(
        LESSON_TEXT.strip(),
        reply_markup=lesson_buttons(),
        parse_mode="Markdown"
    )

    # Запускаем напоминания
    schedule_reminders(context, chat_id)
    logger.info(f"Новый пользователь: {chat_id} (@{update.effective_user.username})")


async def bought(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /bought — отменяет напоминания для купивших."""
    cancel_reminders(context, update.effective_chat.id)
    await update.message.reply_text(
        "🎉 Отлично! Напоминания отключены.\nДо встречи на программе!"
    )


def main() -> None:
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start",  start))
    app.add_handler(CommandHandler("bought", bought))

    print("✅ Бот запущен!")
    app.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    main()
