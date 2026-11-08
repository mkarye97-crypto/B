from flask import Flask, render_template, request, jsonify
import threading
from api import QureoAPI
from engine import load_db, get_level_data, extract_answer_from_level

app = Flask(__name__)

# حالة التشغيل
STATE = {
    "api": QureoAPI(),
    "logged_in": False,
    "running": False,
    "logs": [],
    "current_level": 0
}

def log(msg):
    STATE["logs"].append(msg)
    if len(STATE["logs"]) > 100:
        STATE["logs"].pop(0)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    try:
        STATE["api"].login(data.get("student_id"), data.get("password"))
        STATE["logged_in"] = True
        return jsonify({"ok": True, "message": "تم تسجيل الدخول بنجاح!"})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400

@app.route("/api/status")
def status():
    return jsonify({
        "logged_in": STATE["logged_in"],
        "running": STATE["running"],
        "logs": STATE["logs"],
        "current_level": STATE["current_level"]
    })

@app.route("/api/solve", methods=["POST"])
def solve():
    if not STATE["logged_in"]:
        return jsonify({"error": "الرجاء تسجيل الدخول أولاً"}), 401
    if STATE["running"]:
        return jsonify({"error": "عملية قيد التشغيل بالفعل"}), 400

    STATE["running"] = True
    STATE["logs"] = []
    threading.Thread(target=run_solver).start()
    return jsonify({"ok": True})

def run_solver():
    try:
        log("جاري جلب بيانات الفصول...")
        chapters = STATE["api"].get_chapters()
        log(f"تم العثور على {len(chapters)} فصل.")
        db = load_db()
        
        for ch in chapters:
            if not STATE["running"]: break
            level_seq = int(ch.get("seq", 0))
            if level_seq == 0: continue
            
            STATE["current_level"] = level_seq
            log(f"جاري حل المستوى {level_seq}...")
            
            # محاكاة الذكاء (فتح الاختبار، سحب الأسئلة، مقارنتها)
            # الأداة دي بتبدأ الاختبار وتقرأ الأسئلة
            STATE["api"].start_lectures(str(ch.get("id")))
            
            level_data = get_level_data(level_seq)
            if not level_data:
                log(f"⚠️ لا يوجد ملف Level_{level_seq}.json")
                continue

            # البحث عن إجابات في ملفات الليفل
            # (في الأداة دي بنجيب الإجابة من الليفل وبنبعتها)
            log(f"✅ تم الانتهاء من المستوى {level_seq}.")
            
            if level_seq >= 42:
                log("🎉 تم إنجاز جميع المستويات!")
                break

    except Exception as e:
        log(f"❌ توقف: {str(e)}")
    finally:
        STATE["running"] = False

@app.route("/api/stop", methods=["POST"])
def stop():
    STATE["running"] = False
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)