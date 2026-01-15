# 📘 Class 10 English Textbook Extraction Pipeline

This repository contains a **production-grade Python pipeline** for extracting, cleaning, and structuring the **Tamil Nadu State Board – Class 10 English textbook** into a high-quality JSON format suitable for **search, embeddings, RAG systems, and chatbot applications**.

---

## 🚀 Extraction Process

### 1. Web Crawling
- The extraction pipeline uses the **BeautifulSoup (bs4)** Python library.
- The complete textbook is crawled from the official HTML source.

---

### 2. Textbook Structure Analysis

The English textbook follows a consistent academic structure, which was analyzed and encoded into the extraction logic:

```
Unit
 ├─ Warm up
 ├─ Prose
 │   ├─ About the author
 │   ├─ Glossary
 │   ├─ Vocabulary
 │   ├─ Listening
 │   ├─ Speaking
 │   ├─ Reading
 │   ├─ Writing
 │   ├─ Grammar
 ├─ Poem
 │   ├─ About the poet
 │   ├─ Glossary
 │   ├─ Read and Enjoy
 ├─ Supplementary
     ├─ About the author
     ├─ Glossary
```

---

### 3. Unit-wise Content Mapping

#### Unit 1
- Prose: His First Flight  
- Poem: Life  
- Supplementary: The Tempest  

#### Unit 2
- Prose: The Night the Ghost Got In  
- Poem: The Grumble Family  
- Supplementary: Zigzag  

#### Unit 3
- Prose: Empowered Women Navigating The World  
- Poem: I am Every Women*  
- Supplementary: The Story of Mulan  

#### Unit 4
- Prose: The Attic  
- Poem: The Ant and the Cricket  
- Supplementary: The Aged Mother  

#### Unit 5
- Prose: Tech Bloomers  
- Poem: The Secret of the Machines*  
- Supplementary: A Day in 2889 of an American Journalist  

#### Unit 6
- Prose: The Last Lesson  
- Poem: No Men Are Foreign  
- Supplementary: The Little Hero of Holland  

#### Unit 7
- Prose: The Dying Detective  
- Poem: The House on Elm Street  
- Supplementary: A Dilemma  

---

### 4. Manual Mapping for Accuracy

Some metadata such as **unit numbers** and **lesson titles** cannot be reliably inferred through HTML crawling alone.

To ensure academic correctness:
- Unit mappings were hardcoded
- Prose, Poem, and Supplementary titles were aligned with the official textbook

---

## 🧾 JSON Schema

### Regular Content
```json
{
  "content": "The author O. Henry is known for his short stories with surprise endings...",
  "embedding": [],
  "is_table": false,
  "table_json": null,
  "table_markdown": null,
  "metadata": {
    "subject": "English",
    "board": "Tamil Nadu State Board",
    "standard": 10,
    "unit": 2,
    "topic": "Prose",
    "sub_topic": "About the Author",
    "page": 35,
    "position": 4,
    "source": "https://d1wpyxz35bzzz4.cloudfront.net/tnschools/10-ENGLISH-EM/10-ENGLISH-EM.html",
    "lang": "en"
  }
}
```

### Table Content
Tables are extracted in both **Markdown** and **JSON** formats for better visualization and structured access.

---

## 🎧 Listening Passage Handling

- Extracted separately from unit content
- Content before Unit 1 is ignored
- Acknowledgement section is excluded

---

## ⚙️ Configuration

```python
URL = "https://d1wpyxz35bzzz4.cloudfront.net/tnschools/10-eng-n/10-eng-n.html"
SUBJECT = "English"
STANDARD = 10
OUTPUT_DIR = "textbook_output"
BOARD = "Tamil Nadu State Board"
LANG = "en"
```

---

## 🧹 Text Normalization

### Issues Found
- STS / CCH dialogue markers
- Unicode smart quotes
- Control and invisible characters

### Fixes
- Removed STS and CCH completely
- Normalized smart quotes to ASCII
- Removed control characters
- Applied cleaning twice (extraction + sanitization)

✅ Result: **Clean, embedding-safe JSON output**

---

## ✅ Final Outcome

This pipeline is:

- 📚 Academically correct
- 🧹 Textually clean
- 🤖 Embedding & RAG ready
- 🔁 Deterministic and repeatable
- 🧪 Validated against real textbook data
