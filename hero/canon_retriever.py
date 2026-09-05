"""
Hero AI - Local Canon Retriever

This module retrieves the most relevant sections from HERO_CANON
without using embeddings, external APIs, databases, or local AI models.

Source:
    hero/personality.py

The retriever:
    1. Loads the official Hero canon.
    2. Splits it into sections.
    3. Normalizes Persian/Arabic text.
    4. Scores sections against the user's query.
    5. Returns the most relevant canon sections.

100% local and free.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Tuple

from hero.personality import get_hero_canon


# ============================================================
# Configuration
# ============================================================

# Maximum number of sections returned for a query.
DEFAULT_MAX_SECTIONS = 4

# Maximum total characters returned by the retriever.
DEFAULT_MAX_CHARS = 9000

# Minimum score required for a section to be considered relevant.
DEFAULT_MIN_SCORE = 2


# ============================================================
# Data structure
# ============================================================

@dataclass
class CanonSection:
    """
    Represents one section of the official Hero Canon.
    """

    title: str
    content: str
    normalized_title: str
    normalized_content: str
    keywords: Tuple[str, ...]


# ============================================================
# Persian text normalization
# ============================================================

def normalize_persian(text: str) -> str:
    """
    Normalize Persian/Arabic text so searches are more reliable.

    Examples:
        ي -> ی
        ى -> ی
        ك -> ک

    Also:
        - removes zero-width characters
        - normalizes whitespace
        - removes most punctuation
    """

    if not text:
        return ""

    text = str(text)

    # Arabic -> Persian characters
    replacements = {
        "ي": "ی",
        "ى": "ی",
        "ك": "ک",
        "ۀ": "ه",
        "ة": "ه",
        "ؤ": "و",
        "إ": "ا",
        "أ": "ا",
        "ٱ": "ا",
        "‌": " ",   # ZWNJ
        "\u200c": " ",
        "\u200d": " ",
        "\ufeff": " ",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    # Normalize common Persian punctuation
    punctuation_replacements = {
        "،": " ",
        "؛": " ",
        "؟": " ",
        ":": " ",
        "؟": " ",
        "!": " ",
        "٬": " ",
        "٫": " ",
        ",": " ",
        ".": " ",
        ";": " ",
        "(": " ",
        ")": " ",
        "[": " ",
        "]": " ",
        "{": " ",
        "}": " ",
        "\"": " ",
        "'": " ",
        "«": " ",
        "»": " ",
        "/": " ",
        "\\": " ",
        "-": " ",
        "_": " ",
        "—": " ",
        "–": " ",
    }

    for old, new in punctuation_replacements.items():
        text = text.replace(old, new)

    # Normalize English punctuation/characters around words
    text = re.sub(r"[^\w\s\u0600-\u06FF]", " ", text, flags=re.UNICODE)

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()

    return text


# ============================================================
# Tokenization
# ============================================================

def tokenize(text: str) -> List[str]:
    """
    Convert text into searchable tokens.

    Very short tokens are ignored.
    """

    normalized = normalize_persian(text)

    if not normalized:
        return []

    tokens = normalized.split()

    # Remove extremely short/common noise tokens.
    stop_words = {
        "و",
        "در",
        "به",
        "از",
        "با",
        "که",
        "را",
        "این",
        "آن",
        "یک",
        "برای",
        "روی",
        "بر",
        "تا",
        "یا",
        "چی",
        "چه",
        "کی",
        "چطور",
        "چگونه",
        "من",
        "تو",
        "او",
        "ما",
        "شما",
        "آنها",
    }

    result = []

    for token in tokens:
        if len(token) < 2:
            continue

        if token in stop_words:
            continue

        result.append(token)

    return result


# ============================================================
# Keyword extraction
# ============================================================

def extract_keywords(title: str, content: str) -> Tuple[str, ...]:
    """
    Extract useful keywords from a canon section.

    Title words receive special importance during scoring.
    """

    title_tokens = tokenize(title)
    content_tokens = tokenize(content)

    # Preserve order while removing duplicates.
    seen = set()
    keywords = []

    for token in title_tokens + content_tokens:
        if token not in seen:
            seen.add(token)
            keywords.append(token)

    return tuple(keywords)


# ============================================================
# Canon parsing
# ============================================================

SECTION_SEPARATOR = re.compile(
    r"={10,}"
)


def parse_canon(canon: str) -> List[CanonSection]:
    """
    Split the official canon into sections.

    Expected structure:

        ========================================
        TITLE
        ========================================

        content...

    The parser is intentionally tolerant so small formatting
    differences in personality.py do not break it.
    """

    if not canon:
        return []

    # Split around separator lines.
    raw_parts = SECTION_SEPARATOR.split(canon)

    sections: List[CanonSection] = []

    i = 0

    while i < len(raw_parts):
        part = raw_parts[i].strip()

        if not part:
            i += 1
            continue

        # After splitting, a title normally appears before its content.
        title = part.strip()

        content = ""

        if i + 1 < len(raw_parts):
            possible_content = raw_parts[i + 1].strip()

            # If the next part looks like another title, content may
            # be empty. Otherwise use it as section content.
            content = possible_content

        # Skip obvious file-level markers.
        if title.upper() in {
            "BEGIN",
            "END",
            "BEGIN OF CURRENT CANON",
            "END OF CURRENT CANON",
        }:
            i += 1
            continue

        # Avoid treating huge blocks as titles.
        if len(title) > 300:
            i += 1
            continue

        normalized_title = normalize_persian(title)
        normalized_content = normalize_persian(content)

        if normalized_title:
            keywords = extract_keywords(title, content)

            sections.append(
                CanonSection(
                    title=title,
                    content=content,
                    normalized_title=normalized_title,
                    normalized_content=normalized_content,
                    keywords=keywords,
                )
            )

        i += 2

    # If the separator format did not produce useful sections,
    # use a safer fallback parser.
    if len(sections) < 2:
        sections = parse_canon_fallback(canon)

    return sections


def parse_canon_fallback(canon: str) -> List[CanonSection]:
    """
    Fallback parser for Canon files that use separator lines
    slightly differently.
    """

    lines = canon.splitlines()

    sections: List[CanonSection] = []

    current_title = None
    current_content: List[str] = []

    separator_count = 0

    def flush():
        nonlocal current_title, current_content

        if current_title:
            title = current_title.strip()
            content = "\n".join(current_content).strip()

            if title:
                sections.append(
                    CanonSection(
                        title=title,
                        content=content,
                        normalized_title=normalize_persian(title),
                        normalized_content=normalize_persian(content),
                        keywords=extract_keywords(title, content),
                    )
                )

        current_title = None
        current_content = []

    for line in lines:
        stripped = line.strip()

        if re.fullmatch(r"={10,}", stripped):
            separator_count += 1

            # Two separator lines around a title.
            if current_title is None:
                continue

            continue

        if separator_count >= 2 and current_title is None:
            current_title = stripped
            separator_count = 0
            continue

        if current_title is not None:
            current_content.append(line)

    flush()

    return sections


# ============================================================
# Query aliases
# ============================================================

# These aliases help when the user asks indirectly about
# important Hero characters/concepts.

ALIASES = {
    "همسر": {
        "ریکا",
    },
    "زن": {
        "ریکا",
    },
    "همسر هیرو": {
        "ریکا",
    },
    "دختر هیرو": {
        "ریکا",
    },
    "ازدواج": {
        "ریکا",
    },
    "ازدواج کرد": {
        "ریکا",
    },
    "ازدواج کرده": {
        "ریکا",
    },
    "ازدواج با": {
        "ریکا",
    },
}


def expand_query_tokens(query: str) -> List[str]:
    """
    Add a small set of local aliases to improve retrieval.

    This is NOT an AI model.
    It is simply a deterministic keyword expansion layer.
    """

    normalized_query = normalize_persian(query)
    tokens = tokenize(normalized_query)

    expanded = list(tokens)

    # Direct phrase aliases
    for phrase, additions in ALIASES.items():
        normalized_phrase = normalize_persian(phrase)

        if normalized_phrase in normalized_query:
            for item in additions:
                normalized_item = normalize_persian(item)

                if normalized_item not in expanded:
                    expanded.append(normalized_item)

    # Character-specific normalization / variants
    special_aliases = {
        "ريکا": "ریکا",
        "ریكا": "ریکا",
        "ريك": "ریک",
        "ريكـا": "ریکا",
        "هيـرو": "هیرو",
        "هيرو": "هیرو",
        "كرتور": "کرتور",
    }

    for old, new in special_aliases.items():
        old_normalized = normalize_persian(old)
        new_normalized = normalize_persian(new)

        if old_normalized in normalized_query:
            if new_normalized not in expanded:
                expanded.append(new_normalized)

    return expanded


# ============================================================
# Relevance scoring
# ============================================================

def score_section(
    section: CanonSection,
    query: str,
    query_tokens: List[str],
) -> int:
    """
    Calculate a deterministic relevance score.

    Higher score = more relevant.

    Scoring priorities:
        - exact title match: very high
        - title token match: high
        - exact phrase in content: medium/high
        - token match in content: medium
        - keyword overlap: low/medium
    """

    if not query:
        return 0

    normalized_query = normalize_persian(query)

    if not normalized_query:
        return 0

    score = 0

    title = section.normalized_title
    content = section.normalized_content

    # --------------------------------------------------------
    # Exact title match
    # --------------------------------------------------------

    if normalized_query == title:
        score += 100

    # Query appears directly inside title.
    if normalized_query in title:
        score += 60

    # --------------------------------------------------------
    # Exact phrase in content
    # --------------------------------------------------------

    if normalized_query in content:
        score += 25

    # --------------------------------------------------------
    # Token matching
    # --------------------------------------------------------

    title_tokens = set(tokenize(section.title))
    content_tokens = set(tokenize(section.content))
    keyword_set = set(section.keywords)

    for token in query_tokens:

        # Exact title token.
        if token in title_tokens:
            score += 20

        # Content token.
        elif token in content_tokens:
            score += 7

        # Keyword overlap.
        elif token in keyword_set:
            score += 3

        # Partial match for longer words.
        else:
            if len(token) >= 4:
                for candidate in keyword_set:
                    if len(candidate) >= 4:
                        if token in candidate or candidate in token:
                            score += 2
                            break

    # --------------------------------------------------------
    # Character name emphasis
    # --------------------------------------------------------

    important_names = {
        "ریکا",
        "هیرو",
        "گوست",
        "آستا",
        "آلیس",
        "کرتور",
        "ریمگان",
    }

    for name in important_names:
        if name in query_tokens and name in title_tokens:
            score += 30

    return score


# ============================================================
# Retriever
# ============================================================

class CanonRetriever:
    """
    Local Canon Retrieval engine.

    The Canon is loaded once when this object is created.
    """

    def __init__(
        self,
        canon: str | None = None,
        max_sections: int = DEFAULT_MAX_SECTIONS,
        max_chars: int = DEFAULT_MAX_CHARS,
        min_score: int = DEFAULT_MIN_SCORE,
    ):
        if canon is None:
            canon = get_hero_canon()

        self.canon = canon or ""

        self.max_sections = max(1, int(max_sections))
        self.max_chars = max(1000, int(max_chars))
        self.min_score = max(0, int(min_score))

        self.sections = parse_canon(self.canon)

    # --------------------------------------------------------
    # Information
    # --------------------------------------------------------

    def section_count(self) -> int:
        """
        Return number of parsed Canon sections.
        """

        return len(self.sections)

    # --------------------------------------------------------
    # Search
    # --------------------------------------------------------

    def search(
        self,
        query: str,
        max_sections: int | None = None,
        max_chars: int | None = None,
        min_score: int | None = None,
    ) -> List[Tuple[CanonSection, int]]:
        """
        Search the Canon and return ranked sections.

        Returns:
            [
                (CanonSection, score),
                ...
            ]
        """

        if not query:
            return []

        if max_sections is None:
            max_sections = self.max_sections

        if max_chars is None:
            max_chars = self.max_chars

        if min_score is None:
            min_score = self.min_score

        query_tokens = expand_query_tokens(query)

        if not query_tokens:
            return []

        scored: List[Tuple[CanonSection, int]] = []

        for section in self.sections:
            score = score_section(
                section,
                query,
                query_tokens,
            )

            if score >= min_score:
                scored.append((section, score))

        # Highest score first.
        scored.sort(
            key=lambda item: (
                item[1],
                len(item[0].content),
            ),
            reverse=True,
        )

        # ----------------------------------------------------
        # Limit number of sections and total characters.
        # ----------------------------------------------------

        results: List[Tuple[CanonSection, int]] = []
        total_chars = 0

        for section, score in scored:

            section_text_length = len(section.title) + len(section.content)

            if results and (
                total_chars + section_text_length > max_chars
            ):
                continue

            results.append((section, score))
            total_chars += section_text_length

            if len(results) >= max_sections:
                break

        return results

    # --------------------------------------------------------
    # Build context
    # --------------------------------------------------------

    def build_context(
        self,
        query: str,
        max_sections: int | None = None,
        max_chars: int | None = None,
        min_score: int | None = None,
    ) -> str:
        """
        Return formatted Canon context ready to inject into
        the Hero system prompt.
        """

        results = self.search(
            query=query,
            max_sections=max_sections,
            max_chars=max_chars,
            min_score=min_score,
        )

        if not results:
            return ""

        parts = []

        parts.append(
            "OFFICIAL HERO CANON — RELEVANT SECTIONS\n"
            "The following information was retrieved locally "
            "from the official Hero Canon.\n"
            "Treat it as authoritative canon information.\n"
        )

        for index, (section, score) in enumerate(results, start=1):

            parts.append(
                f"\n--- CANON SECTION {index} ---\n"
                f"TITLE: {section.title}\n"
                f"{section.content.strip()}\n"
            )

        parts.append(
            "\n--- END RELEVANT CANON ---"
        )

        context = "\n".join(parts).strip()

        # Final safety limit.
        if max_chars is not None and len(context) > max_chars:
            context = context[:max_chars].rstrip()

            # Avoid ending in the middle of a Unicode character/word.
            context += "\n\n--- END RELEVANT CANON ---"

        return context


# ============================================================
# Global retriever
# ============================================================

_retriever: CanonRetriever | None = None


def get_canon_retriever() -> CanonRetriever:
    """
    Return a cached global CanonRetriever.

    The Canon is parsed only once during the process lifetime.
    """

    global _retriever

    if _retriever is None:
        _retriever = CanonRetriever()

    return _retriever


# ============================================================
# Simple public helper
# ============================================================

def retrieve_canon(
    query: str,
    max_sections: int = DEFAULT_MAX_SECTIONS,
    max_chars: int = DEFAULT_MAX_CHARS,
) -> str:
    """
    Convenience function.

    Example:

        context = retrieve_canon("ریکا کیه؟")
    """

    retriever = get_canon_retriever()

    return retriever.build_context(
        query=query,
        max_sections=max_sections,
        max_chars=max_chars,
    )


# ============================================================
# Debug / testing
# ============================================================

def debug_search(query: str) -> None:
    """
    Print search results for local testing.

    This function is not used by the Telegram bot directly.
    """

    retriever = get_canon_retriever()

    print()
    print("=" * 60)
    print("HERO CANON RETRIEVER TEST")
    print("=" * 60)

    print(f"Query: {query}")
    print(f"Canon sections: {retriever.section_count()}")

    results = retriever.search(query)

    if not results:
        print("No relevant Canon section found.")
        return

    print()
    print("Results:")

    for index, (section, score) in enumerate(results, start=1):
        print()
        print(f"[{index}] Score: {score}")
        print(f"Title: {section.title}")
        print(f"Content preview: {section.content[:300]}")

    print()
    print("=" * 60)


# ============================================================
# Direct execution
# ============================================================

if __name__ == "__main__":
    # Simple standalone test.
    #
    # Run from G:\hero:
    #
    #     python -m hero.canon_retriever
    #
    debug_search("ریکا کیه؟")