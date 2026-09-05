from database.database import get_connection


def save_user(
    user_id: int,
    username: str | None,
    first_name: str | None,
    last_name: str | None
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


def get_user(user_id: int):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE user_id = ?",
        (user_id,)
    )

    result = cursor.fetchone()

    connection.close()

    return result