import aiosqlite
import time

DB_NAME = "bot_database.db"

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                balance REAL DEFAULT 0.0,
                ads_watched INTEGER DEFAULT 0,
                daily_ads INTEGER DEFAULT 0,
                last_ad_time REAL DEFAULT 0.0,
                referrals_count INTEGER DEFAULT 0,
                referred_by INTEGER,
                tasks_completed TEXT DEFAULT ""
            )
        """)
        await db.commit()

async def add_user(user_id: int, referred_by: int = None):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
        user = await cursor.fetchone()
        if not user:
            if referred_by == user_id:
                referred_by = None
                
            await db.execute(
                "INSERT INTO users (user_id, referred_by) VALUES (?, ?)", 
                (user_id, referred_by)
            )
            
            if referred_by:
                await db.execute(
                    "UPDATE users SET balance = balance + 2.0, referrals_count = referrals_count + 1 WHERE user_id = ?", 
                    (referred_by,)
                )
                
            await db.commit()
            return True
        return False

async def get_user(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT balance, ads_watched, daily_ads, last_ad_time, referrals_count, tasks_completed FROM users WHERE user_id = ?", 
            (user_id,)
        )
        return await cursor.fetchone()

async def complete_task_db(user_id: int, task_id: str, reward: float):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("SELECT balance, tasks_completed FROM users WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()
        if row:
            balance, tasks_completed = row
            tasks_list = tasks_completed.split(",") if tasks_completed else []
            
            if task_id not in tasks_list:
                tasks_list.append(task_id)
                new_tasks_str = ",".join(tasks_list)
                new_balance = balance + reward
                
                await db.execute(
                    "UPDATE users SET balance = ?, tasks_completed = ? WHERE user_id = ?",
                    (new_balance, new_tasks_str, user_id)
                )
                await db.commit()
                return True
        return False
