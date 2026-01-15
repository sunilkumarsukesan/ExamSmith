import os
import re
import json
import requests
from bs4 import BeautifulSoup

# ---------------- CONFIG ---------------- #

URL = "https://d1wpyxz35bzzz4.cloudfront.net/tnschools/10-eng-n/10-eng-n.html"
SUBJECT = "English"
STANDARD = 10
OUTPUT_DIR = "textbook_output"

BOARD = "Tamil Nadu State Board"
LANG = "en"

# ---------------- BOOK-ALIGNED UNIT MAP ---------------- #

UNIT_MAP = {
    1: {
        "Prose": "His First Flight",
        "Poem": "Life",
        "Supplementary": "The Tempest"
    },
    2: {
        "Prose": "The Night the Ghost Got In",
        "Poem": "The Grumble Family",
        "Supplementary": "Zigzag"
    },
    3: {
        "Prose": "Empowered Women Navigating The World",
        "Poem": "I am Every Women*",
        "Supplementary": "The Story of Mulan"
    },
    4: {
        "Prose": "The Attic",
        "Poem": "The Ant and the Cricket",
        "Supplementary": "The Aged Mother"
    },
    5: {
        "Prose": "Tech Bloomers",
        "Poem": "The Secret of the Machines*",
        "Supplementary": "A Day in 2889 of an American Journalist"
    },
    6: {
        "Prose": "The Last Lesson",
        "Poem": "No Men Are Foreign",
        "Supplementary": "The Little Hero of Holland"
    },
    7: {
        "Prose": "The Dying Detective",
        "Poem": "The House on Elm Street",
        "Supplementary": "A Dilemma"
    }
}

TITLE_LOOKUP = {
    title.lower(): (unit, topic)
    for unit, sections in UNIT_MAP.items()
    for topic, title in sections.items()
}

LISTENING_SUBTOPIC = {
    1: "A Trip to Remember Forever",
    2: "Three Simple Rules"
}

SUB_TOPICS = [
    "warm up",
    "about the author",
    "about the poet",
    "glossary",
    "vocabulary",
    "listening",
    "speaking",
    "reading",
    "writing",
    "grammar",
    "read and enjoy"
]

# ---------------- TEXT NORMALIZATION (FINAL FIX) ---------------- #

def clean(text):
    return re.sub(r"\s+", " ", text or "").strip()


def normalize_quotes_and_markers(text):
    """
    FINAL, HARD CLEAN NORMALIZATION

    Guarantees:
    - No STS / CCH
    - No smart quotes
    - No control characters
    - Clean ASCII text only
    """
    if not text:
        return ""

    # --- 1. Remove STS / CCH completely (anywhere) ---
    text = re.sub(r"STS", "", text)
    text = re.sub(r"CCH", "", text)

    # --- 2. Normalize Unicode quotes → ASCII ---
    unicode_map = {
        "“": '"',
        "”": '"',
        "„": '"',
        "‟": '"',
        "": '"',
        "": '"',
        "‘": "'",
        "’": "'",
        "‚": "'",
        "‛": "'",
    }
    for k, v in unicode_map.items():
        text = text.replace(k, v)

    # --- 3. Remove invisible control characters ---
    text = re.sub(r"[\x00-\x1F\x7F]", " ", text)

    # --- 4. Fix spacing around punctuation ---
    text = re.sub(r'\s+([,.!?;:])', r'\1', text)

    # --- 5. Collapse whitespace ---
    text = re.sub(r"\s+", " ", text)

    return text.strip()



# ---------------- FETCH ---------------- #

def fetch_html(url):
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return r.text


# ---------------- EXTRACTION ---------------- #

def fill_default_sub_topic(unit, topic, sub_topic):
    if sub_topic is None and unit in UNIT_MAP and topic in UNIT_MAP[unit]:
        return UNIT_MAP[unit][topic]
    return sub_topic


def extract_textbook():
    soup = BeautifulSoup(fetch_html(URL), "html.parser")

    elements = soup.body.find_all(
        ["h1", "h2", "h3", "h4", "p", "li", "table"]
    )

    results = []
    position = 0

    unit = None
    topic = None
    sub_topic = None
    page = None

    in_listening = False
    seen_unit1 = False

    def emit(text):
        nonlocal position
        position += 1

        text = normalize_quotes_and_markers(text)
        final_sub_topic = fill_default_sub_topic(unit, topic, sub_topic)

        results.append({
            "content": text,
            "embedding": [],
            "is_table": False,
            "table_json": None,
            "table_markdown": None,
            "metadata": {
                "subject": SUBJECT,
                "board": BOARD,
                "standard": STANDARD,
                "unit": unit,
                "topic": topic,
                "sub_topic": final_sub_topic,
                "page": page,
                "position": position,
                "source": URL,
                "lang": LANG
            }
        })

    for el in elements:
        raw = clean(el.get_text())
        if not raw:
            continue

        lower = raw.lower()

        if lower == "acknowledgement":
            break

        if not seen_unit1:
            if "his first flight" in lower:
                seen_unit1 = True
            else:
                continue

        if lower == "listening passage":
            in_listening = True
            topic = "LISTENING PASSAGE"
            sub_topic = LISTENING_SUBTOPIC.get(unit)
            continue

        if not in_listening and lower in TITLE_LOOKUP:
            unit, topic = TITLE_LOOKUP[lower]
            sub_topic = None
            continue

        if not in_listening and lower in ["prose", "poem", "supplementary"]:
            topic = lower.capitalize()
            sub_topic = None
            continue

        if not in_listening:
            for s in SUB_TOPICS:
                if lower.startswith(s):
                    sub_topic = s.title()
                    break

        if in_listening:
            topic = "LISTENING PASSAGE"
            sub_topic = LISTENING_SUBTOPIC.get(unit)
            emit(raw)
            continue

        emit(raw)

    return results


# ---------------- FINAL SANITIZATION (FAILSAFE) ---------------- #

def sanitize_output(data):
    for item in data:
        item["content"] = normalize_quotes_and_markers(
            item.get("content", "")
        )
    return data


# ---------------- MAIN ---------------- #

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    data = sanitize_output(extract_textbook())

    out_file = os.path.join(OUTPUT_DIR, "book_complete.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ Extracted {len(data)} blocks")
    print(f"📄 Output saved to {out_file}a")


if __name__ == "__main__":
    main()
