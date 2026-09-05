from database.memories import (
    save_memory,
    get_memories,
)
from database.database import clear_memories


# =========================================================
# REMEMBER
# =========================================================

def remember(
    user_id: int,
    text: str,
    importance: int = 1
):

    save_memory(
        user_id=user_id,
        memory=text,
        importance=importance
    )


# =========================================================
# GET USER MEMORIES
# =========================================================

def get_user_memories(
    user_id: int
):

    rows = get_memories(
        user_id=user_id
    )

    if not rows:
        return "هیچ خاطره‌ای از این کاربر ذخیره نشده است."

    result = []

    for row in rows:

        memory = row.get("memory")

        if memory:
            result.append(
                f"- {memory}"
            )

    if not result:
        return "هیچ خاطره‌ای از این کاربر ذخیره نشده است."

    return "\n".join(result)


# =========================================================
# FORGET ALL
# =========================================================

def forget_all(
    user_id: int
):

    clear_memories(
        user_id=user_id
    )