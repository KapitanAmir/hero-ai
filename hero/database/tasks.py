from database.database import get_connection


def add_task(user_id: int, title: str):

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


def get_tasks(user_id: int):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, title, completed
        FROM tasks
        WHERE user_id = ?
        ORDER BY completed ASC, id DESC
    """, (
        user_id,
    ))

    rows = cursor.fetchall()

    connection.close()

    return rows


def complete_task(user_id: int, task_id: int):

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

    changed = cursor.rowcount > 0

    connection.close()

    return changed


def delete_task(user_id: int, task_id: int):

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

    changed = cursor.rowcount > 0

    connection.close()

    return changed