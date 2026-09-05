def safe_text(text: str) -> str:

    if not text:
        return ""

    return text.strip()


def split_long_message(
    text: str,
    max_length: int = 4000
):

    if len(text) <= max_length:
        return [text]

    chunks = []

    current = ""

    for paragraph in text.split("\n"):

        if len(current) + len(paragraph) + 1 <= max_length:

            current += paragraph + "\n"

        else:

            if current:
                chunks.append(
                    current.strip()
                )

            current = paragraph + "\n"

    if current:
        chunks.append(
            current.strip()
        )

    return chunks