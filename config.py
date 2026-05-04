import os

# ─── Обязательно замени на свой токен от @BotFather ───
BOT_TOKEN = os.getenv("BOT_TOKEN", "8647291318:AAHsx1g0sLHASsJh6w2pHKD8W9t82OACl4I")

# ─── Telegram-канал комьюнити (например @RallyUpKyiv) ───
COMMUNITY_CHANNEL = os.getenv("COMMUNITY_CHANNEL", "@RallyUpKyiv")

# ─── Путь к базе данных ───
DB_PATH = "rallyup.db"

# ─── Тексты ───
SPORTS = ["🎾 Теннис", "🏸 Падел"]
LEVELS = ["🟢 Новичок", "🟡 Средний", "🔴 Продвинутый"]
TIMES  = ["☀️ Утро", "🌤 День", "🌙 Вечер", "📅 Выходные", "⚡ Любое время"]
GENDERS = ["👨 Парень", "👩 Девушка"]
LOOKING_FOR = ["👨 Парней", "👩 Девушек", "👥 Всех"]
