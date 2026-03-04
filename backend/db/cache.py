import aiosqlite
import os
import json
from typing import Optional, List, Dict
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv("CACHE_DB_PATH", "data/notepilot.db")

async def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    # Get the directory of the current file (cache.py)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # The schema is in the same directory
    schema_path = os.path.join(current_dir, "schema.sql")
    
    async with aiosqlite.connect(DB_PATH) as db:
        with open(schema_path, "r") as f:
            await db.executescript(f.read())
        await db.commit()

async def get_cached_note(video_id: str) -> Optional[Dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM notes WHERE video_id = ?", (video_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                res = dict(row)
                res["notes"] = json.loads(res["notes_json"])
                return res
    return None

async def save_note(video_id: str, metadata: Dict, transcript: str, notes: Dict):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT OR REPLACE INTO notes (
                video_id, title, channel, duration_seconds, thumbnail, transcript, notes_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                video_id,
                metadata.get("title"),
                metadata.get("channel"),
                metadata.get("duration_seconds"),
                metadata.get("thumbnail"),
                transcript,
                json.dumps(notes)
            )
        )
        await db.commit()

async def get_history(limit: int = 20) -> List[Dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT video_id, title, channel, created_at FROM notes ORDER BY created_at DESC LIMIT ?",
            (limit,)
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

async def get_cache_count() -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM notes") as cursor:
            count = await cursor.fetchone()
            return count[0] if count else 0
