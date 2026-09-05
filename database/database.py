import sqlite3
from config import DATABASE_PATH


# =========================================================
# CONNECTION
# =========================================================

def get_connection():
    connection = sqlite3.connect(
        DATABASE_PATH,
        check_same_thread=False
    )

    connection.row_factory = sqlite3.Row

    return connection


# =========================================================
# INIT DATABASE
# =========================================================

def init_database():

    connection = get_connection()
    cursor = connection.cursor()

    # -----------------------------------------------------
    # USERS
    # -----------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # -----------------------------------------------------
    # MESSAGES
    # -----------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # -----------------------------------------------------
    # MEMORIES
    # -----------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            memory TEXT NOT NULL,
            importance INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # -----------------------------------------------------
    # TASKS
    # -----------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            completed INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # -----------------------------------------------------
    # REMINDERS
    # -----------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            text TEXT NOT NULL,
            remind_at TEXT NOT NULL,
            completed INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()


# =========================================================
# USERS
# =========================================================

def create_or_update_user(
    user_id,
    username=None,
    first_name=None,
    last_name=None
):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO users (
            user_id,
            username,
            first_name,
            last_name
        )
        VALUES (?, ?, ?, ?)

        ON CONFLICT(user_id)
        DO UPDATE SET
            username = excluded.username,
            first_name = excluded.first_name,
            last_name = excluded.last_name,
            last_seen = CURRENT_TIMESTAMP
    """, (
        user_id,
        username,
        first_name,
        last_name
    ))

    connection.commit()
    connection.close()


# =========================================================
# MESSAGES
# =========================================================

def save_message(
    user_id,
    role,
    content
):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO messages (
            user_id,
            role,
            content
        )
        VALUES (?, ?, ?)
    """, (
        user_id,
        role,
        content
    ))

    connection.commit()
    connection.close()


def get_recent_messages(
    user_id,
    limit=12
):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            role,
            content,
            created_at
        FROM messages
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT ?
    """, (
        user_id,
        limit
    ))

    rows = cursor.fetchall()

    connection.close()

    # چون از جدیدترین به قدیمی‌ترین گرفتیم،
    # برای AI برعکسش می‌کنیم.
    rows.reverse()

    return [
        {
            "role": row["role"],
            "content": row["content"]
        }
        for row in rows
    ]


def get_message_count(user_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*) AS count
        FROM messages
        WHERE user_id = ?
    """, (
        user_id,
    ))

    result = cursor.fetchone()

    connection.close()

    return result["count"]


def clear_messages(user_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM messages
        WHERE user_id = ?
    """, (
        user_id,
    ))

    connection.commit()
    connection.close()


# =========================================================
# MEMORIES
# =========================================================

def save_memory(
    user_id,
    memory,
    importance=1
):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO memories (
            user_id,
            memory,
            importance
        )
        VALUES (?, ?, ?)
    """, (
        user_id,
        memory,
        importance
    ))

    connection.commit()

    memory_id = cursor.lastrowid

    connection.close()

    return memory_id


def get_memories(
    user_id,
    limit=20
):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            memory,
            importance,
            created_at
        FROM memories
        WHERE user_id = ?
        ORDER BY importance DESC, id DESC
        LIMIT ?
    """, (
        user_id,
        limit
    ))

    rows = cursor.fetchall()

    connection.close()

    return [
        {
            "id": row["id"],
            "memory": row["memory"],
            "importance": row["importance"],
            "created_at": row["created_at"]
        }
        for row in rows
    ]


def delete_memory(
    user_id,
    memory_id
):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM memories
        WHERE id = ?
        AND user_id = ?
    """, (
        memory_id,
        user_id
    ))

    connection.commit()

    deleted = cursor.rowcount > 0

    connection.close()

    return deleted


def clear_memories(user_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM memories
        WHERE user_id = ?
    """, (
        user_id,
    ))

    connection.commit()
    connection.close()


# =========================================================
# TASKS
# =========================================================

def add_task(
    user_id,
    title
):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO tasks (
            user_id,
            title
        )
        VALUES (?, ?)
    """, (
        user_id,
        title
    ))

    connection.commit()

    task_id = cursor.lastrowid

    connection.close()

    return task_id


def get_tasks(user_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            title,
            completed,
            created_at
        FROM tasks
        WHERE user_id = ?
        ORDER BY completed ASC, id DESC
    """, (
        user_id,
    ))

    rows = cursor.fetchall()

    connection.close()

    return [
        {
            "id": row["id"],
            "title": row["title"],
            "completed": bool(row["completed"]),
            "created_at": row["created_at"]
        }
        for row in rows
    ]


def complete_task(
    user_id,
    task_id
):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE tasks
        SET completed = 1
        WHERE id = ?
        AND user_id = ?
    """, (
        task_id,
        user_id
    ))

    connection.commit()

    updated = cursor.rowcount > 0

    connection.close()

    return updated


def delete_task(
    user_id,
    task_id
):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM tasks
        WHERE id = ?
        AND user_id = ?
    """, (
        task_id,
        user_id
    ))

    connection.commit()

    deleted = cursor.rowcount > 0

    connection.close()

    return deleted


# =========================================================
# REMINDERS
# =========================================================

def add_reminder(
    user_id,
    text,
    remind_at
):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO reminders (
            user_id,
            text,
            remind_at
        )
        VALUES (?, ?, ?)
    """, (
        user_id,
        text,
        remind_at
    ))

    connection.commit()

    reminder_id = cursor.lastrowid

    connection.close()

    return reminder_id


def get_pending_reminders(user_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            text,
            remind_at,
            completed,
            created_at
        FROM reminders
        WHERE user_id = ?
        AND completed = 0
        ORDER BY remind_at ASC
    """, (
        user_id,
    ))

    rows = cursor.fetchall()

    connection.close()

    return [
        {
            "id": row["id"],
            "text": row["text"],
            "remind_at": row["remind_at"],
            "completed": bool(row["completed"]),
            "created_at": row["created_at"]
        }
        for row in rows
    ]


def complete_reminder(
    user_id,
    reminder_id
):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE reminders
        SET completed = 1
        WHERE id = ?
        AND user_id = ?
    """, (
        reminder_id,
        user_id
    ))

    connection.commit()

    updated = cursor.rowcount > 0

    connection.close()

    return updated