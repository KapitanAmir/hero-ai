from database.database import get_connection
from config import MAX_MEMORIES


def save_memory(
    user_id: int,
    memory: str,
    importance: int = 1
):

    memory = memory.strip()

    if not memory:
        return

    connection = get_connection()
    cursor = connection.cursor()

    # جلوگیری از ثبت دقیق یک خاطره چند بار
    cursor.execute("""
        SELECT id
        FROM memories
        WHERE user_id = ?
        AND memory = ?
        LIMIT 1
    """, (
        user_id,
        memory
    ))

    existing = cursor.fetchone()

    if existing:
        connection.close()
        return

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

    # نگه داشتن تعداد محدود خاطرات
    cursor.execute("""
        DELETE FROM memories
        WHERE user_id = ?
        AND id NOT IN (
            SELECT id
            FROM memories
            WHERE user_id = ?
            ORDER BY importance DESC, id DESC
            LIMIT ?
        )
    """, (
        user_id,
        user_id,
        MAX_MEMORIES
    ))

    connection.commit()
    connection.close()


def get_memories(user_id: int):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT memory, importance
        FROM memories
        WHERE user_id = ?
        ORDER BY importance DESC, id DESC
        LIMIT ?
    """, (
        user_id,
        MAX_MEMORIES
    ))

    rows = cursor.fetchall()

    connection.close()

    return rows


def delete_memories(user_id: int):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM memories WHERE user_id = ?",
        (user_id,)
    )

    connection.commit()
    connection.close()