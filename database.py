import aiosqlite
from config import DB_PATH
import gspread
import json
import os
from datetime import datetime

def _get_sheet():
    creds_json = os.getenv("GOOGLE_CREDENTIALS")
    creds = json.loads(creds_json)
    gc = gspread.service_account_from_dict(creds)
    return gc.open_by_key(os.getenv("SHEET_ID")).sheet1

async def mirror_to_sheets(user_id: int, username: str, data: dict):
    try:
        sheet = _get_sheet()
        sheet.append_row([
            str(user_id),
            username,
            data.get("name", ""),
            data.get("gender", ""),
            data.get("sport", ""),
            data.get("level", ""),
            data.get("city", ""),
            data.get("play_time", ""),
            datetime.now().strftime("%Y-%m-%d %H:%M")
        ])
    except Exception as e:
        pass

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                tg_id       INTEGER PRIMARY KEY,
                username    TEXT,
                name        TEXT,
                gender      TEXT,
                sport       TEXT,
                level       TEXT,
                city        TEXT,
                play_time   TEXT,
                photo_id    TEXT,
                looking_for TEXT,
                active      INTEGER DEFAULT 1,
                created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS swipes (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                from_id     INTEGER NOT NULL,
                to_id       INTEGER NOT NULL,
                action      TEXT NOT NULL,  -- 'like' | 'pass'
                created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(from_id, to_id)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS invites (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                from_id     INTEGER NOT NULL,
                to_id       INTEGER NOT NULL,
                status      TEXT DEFAULT 'pending',  -- 'pending' | 'accepted' | 'declined'
                created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(from_id, to_id)
            )
        """)
        await db.commit()


# ───────────────── Users ─────────────────

async def get_user(tg_id: int) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM users WHERE tg_id = ?", (tg_id,)
        ) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None


async def upsert_user(tg_id: int, username: str, data: dict):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO users (tg_id, username, name, gender, sport, level,
                               city, play_time, photo_id, looking_for)
            VALUES (:tg_id, :username, :name, :gender, :sport, :level,
                    :city, :play_time, :photo_id, :looking_for)
            ON CONFLICT(tg_id) DO UPDATE SET
                username    = excluded.username,
                name        = excluded.name,
                gender      = excluded.gender,
                sport       = excluded.sport,
                level       = excluded.level,
                city        = excluded.city,
                play_time   = excluded.play_time,
                photo_id    = excluded.photo_id,
                looking_for = excluded.looking_for,
                active      = 1
        """, {"tg_id": tg_id, "username": username, **data})
        await db.commit()


async def set_user_active(tg_id: int, active: bool):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET active = ? WHERE tg_id = ?",
            (1 if active else 0, tg_id)
        )
        await db.commit()


# ───────────────── Swipes ─────────────────

async def record_swipe(from_id: int, to_id: int, action: str):
    """action: 'like' | 'pass'"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT OR IGNORE INTO swipes (from_id, to_id, action)
            VALUES (?, ?, ?)
        """, (from_id, to_id, action))
        await db.commit()


async def already_swiped(from_id: int, to_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT 1 FROM swipes WHERE from_id = ? AND to_id = ?",
            (from_id, to_id)
        ) as cur:
            return await cur.fetchone() is not None


# ───────────────── Candidates ─────────────────

async def get_next_candidate(viewer_id: int, looking_for: str) -> dict | None:
    """
    Возвращает следующего кандидата которого viewer ещё не свайпал.
    looking_for: '👨 Парней' | '👩 Девушек' | '👥 Всех'
    """
    gender_filter = ""
    params: list = [viewer_id, viewer_id]

    if looking_for == "👨 Парней":
        gender_filter = "AND u.gender = '👨 Парень'"
    elif looking_for == "👩 Девушек":
        gender_filter = "AND u.gender = '👩 Девушка'"

    query = f"""
        SELECT u.* FROM users u
        WHERE u.tg_id != ?
          AND u.active = 1
          {gender_filter}
          AND u.tg_id NOT IN (
              SELECT to_id FROM swipes WHERE from_id = ?
          )
        ORDER BY RANDOM()
        LIMIT 1
    """
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(query, params) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None


# ───────────────── Invites ─────────────────

async def create_invite(from_id: int, to_id: int) -> bool:
    """Создаёт инвайт. Возвращает True если успешно, False если уже существует."""
    async with aiosqlite.connect(DB_PATH) as db:
        try:
            await db.execute(
                "INSERT INTO invites (from_id, to_id) VALUES (?, ?)",
                (from_id, to_id)
            )
            await db.commit()
            return True
        except aiosqlite.IntegrityError:
            return False


async def get_invite(from_id: int, to_id: int) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM invites WHERE from_id = ? AND to_id = ?",
            (from_id, to_id)
        ) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None


async def update_invite_status(from_id: int, to_id: int, status: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE invites SET status = ? WHERE from_id = ? AND to_id = ?",
            (status, from_id, to_id)
        )
        await db.commit()
