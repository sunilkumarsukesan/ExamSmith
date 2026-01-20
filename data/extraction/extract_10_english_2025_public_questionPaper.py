import re
import json
import os
from pathlib import Path

# ===============================
# CONFIGURATION
# ===============================

BASE_DIR = Path(__file__).parent
QUESTION_FILE = BASE_DIR / "10 English Public Exam Question Paper.txt"
ANSWER_FILE   = BASE_DIR / "10 English Public Exam Answer Key .txt"

OUTPUT_DIR = BASE_DIR.parent / "extractionOutput"
OUTPUT_JSON = OUTPUT_DIR / "tn_10th_english_2025.json"
IMAGE_DIR = OUTPUT_DIR / "images"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(IMAGE_DIR, exist_ok=True)

# ===============================
# HELPERS
# ===============================

def clean(text):
    if not text:
        return None
    return re.sub(r"\s+", " ", text).strip()

def strip_trailing_headers(text):
    return re.split(
        r"(Part\s*-\s*[IVX]+|SECTION\s*-\s*\d+|Answer any)",
        text,
        flags=re.IGNORECASE
    )[0].strip()

# ===============================
# PART / SECTION / TOPIC
# ===============================

def detect_part(q):
    if 1 <= q <= 14: return "Part - I"
    if 15 <= q <= 28: return "Part - II"
    if 29 <= q <= 45: return "Part - III"
    return "Part - IV"

def detect_section(q):
    if 15 <= q <= 18: return "SECTION - I"
    if 19 <= q <= 22: return "SECTION - II"
    if 23 <= q <= 27: return "SECTION - III"
    if q == 28: return "SECTION - IV"
    if 29 <= q <= 32: return "SECTION - I"
    if 33 <= q <= 36: return "SECTION - II"
    if q in (37, 38): return "SECTION - III"
    if 39 <= q <= 44: return "SECTION - IV"
    if q == 45: return "SECTION - V"
    return None

def detect_topic(q):
    return {
        1:"Synonyms",2:"Synonyms",3:"Synonyms",
        4:"Antonyms",5:"Antonyms",6:"Antonyms",
        7:"Plural Forms",8:"Affixes",9:"Abbreviations",
        10:"Phrasal Verbs",11:"Compound Words",
        12:"Prepositions",13:"Tenses",14:"Linkers"
    }.get(q, "General")

# ===============================
# PARSE QUESTIONS
# ===============================

with open(QUESTION_FILE, encoding="utf-8") as f:
    q_text = f.read()

question_blocks = re.split(r"\n(?=\d+\.)", q_text)
questions = {}

for block in question_blocks:
    m = re.match(r"(\d+)\.\s*(.*)", block, re.DOTALL)
    if m:
        questions[int(m.group(1))] = clean(strip_trailing_headers(m.group(2)))

# ===============================
# PARSE ANSWERS
# ===============================

with open(ANSWER_FILE, encoding="utf-8") as f:
    a_text = f.read()

# ---- MCQ answers ----
MCQ_PATTERN = re.compile(r"^\s*(\d+)\.\s*\(([a-d])\)\s*(.+)$")
mcq_answers = {}

for line in a_text.splitlines():
    m = MCQ_PATTERN.match(line.strip())
    if m:
        mcq_answers[int(m.group(1))] = {
            "option": m.group(2),
            "text": clean(m.group(3))
        }

# ---- Other answers ----
answer_blocks = re.split(r"\n(?=\d+\.)", a_text)
answers = {}

for block in answer_blocks:
    m = re.match(r"(\d+)\.\s*(.*)", block, re.DOTALL)
    if m:
        q_no = int(m.group(1))
        answers[q_no] = clean(strip_trailing_headers(m.group(2)))

# ===============================
# OR + SUB QUESTIONS
# ===============================

SUB_Q_PATTERN = re.compile(r"\(([ivx]+)\)\s*(.*?)(?=\([ivx]+\)|$)", re.DOTALL)

def extract_subs(text):
    return [
        {"id": m.group(1), "question": clean(m.group(2))}
        for m in SUB_Q_PATTERN.finditer(text or "")
    ]

def split_or(text):
    if not text or "(OR)" not in text:
        return None
    a, b = text.split("(OR)", 1)
    return {"a": clean(a), "b": clean(b)}

# ===============================
# BUILD FINAL JSON
# ===============================

final = []

for q_no, q_text in questions.items():

    part = detect_part(q_no)
    section = detect_section(q_no)
    topic = detect_topic(q_no)

    base = {
        "embedding": [],
        "metadata": {
            "exam": "TN SSLC Public Exam",
            "year": 2025,
            "subject": "English",
            "board": "Tamil Nadu State Board",
            "standard": 10,
            "part": part,
            "section": section,
            "topic": topic,
            "marks": 1 if q_no <= 14 else 2 if q_no <= 28 else 5 if q_no <= 45 else 8,
            "difficulty": "easy",
            "syllabus_map": {
                "unit": None,
                "lesson_type": None,
                "lesson_name": None
            },
            "source": "TN SSLC English Public Exam 2025",
            "lang": "en"
        }
    }

    # ================= MCQ =================
    if q_no <= 14:
        choices = dict(re.findall(r"\(([a-d])\)\s*([^()]+)", q_text))

        record = {
            **base,
            "content": q_text.split("(")[0].strip(),
            "question": {
                "number": q_no,
                "type": "mcq",
                "choices": choices,
                "answer": mcq_answers.get(q_no)
            }
        }

    # ================= OR QUESTIONS =================
    elif q_no in (46, 47):
        q_split = split_or(q_text)
        a_split = split_or(answers.get(q_no))

        record = {
            **base,
            "content": "OR question",
            "question": {
                "number": q_no,
                "type": "or",
                "choices": {
                    "a": {
                        "content": q_split["a"],
                        "sub_questions": extract_subs(q_split["a"]),
                        "answer": a_split["a"] if a_split else None
                    },
                    "b": {
                        "content": q_split["b"],
                        "sub_questions": extract_subs(q_split["b"]),
                        "answer": a_split["b"] if a_split else None
                    }
                }
            }
        }

    # ================= NORMAL =================
    else:
        record = {
            **base,
            "content": q_text,
            "question": {
                "number": q_no,
                "type": "short_answer" if part == "Part - II" else "long_answer",
                "answer": answers.get(q_no)
            }
        }

    final.append(record)

# ===============================
# SAVE
# ===============================

with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(final, f, indent=2, ensure_ascii=False)

print("✅ Extraction completed")
print(f"📄 Questions extracted: {len(final)}")
print(f"📦 Output saved to: {OUTPUT_JSON}")
