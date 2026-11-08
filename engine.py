import json, os, re, unicodedata

DB_PATH = "data/question_answer_database.json"
LEVELS_DIR = "data/levels"

def load_db():
    if not os.path.exists(DB_PATH):
        return {}
    with open(DB_PATH, "r", encoding="utf-8") as f:
        data = json.load(f).get("questions", [])
    return {(str(x["chapter_id"]), str(x["question_id"])): x for x in data}

def get_level_data(level_num):
    path = os.path.join(LEVELS_DIR, f"Level_{str(level_num).zfill(2)}.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def extract_answer_from_level(level_data, question_text):
    if not level_data or "lessons" not in level_data:
        return None
        
    def normalize(text):
        text = re.sub(r'[^\w\s]', '', str(text))
        return text.strip().lower()

    target_q = normalize(question_text)

    for lesson in level_data["lessons"]:
        for q in lesson.get("questions", []):
            if normalize(q.get("question", "")) == target_q:
                answer = q.get("answer", "")
                # تنظيف الإجابة من أي كلام عربي إضافي
                if answer:
                    lines = answer.split("\n")
                    code_lines = [line for line in lines if not re.search(r'[\u0600-\u06FF]', line)]
                    if code_lines:
                        return "\n".join(code_lines).strip()
                    return answer.strip()
    return None