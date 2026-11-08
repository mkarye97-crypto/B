import requests

API_BASE = "https://me-tp.qureo.education"
PORTAL_URL = "https://me-portal.qureo.education"

class QureoAPI:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0 Safari/537.36",
            "Accept-Language": "ar,en-US;q=0.8,en;q=0.7"
        })

    def login(self, student_id, password):
        landing = self.session.get(PORTAL_URL + "/", timeout=30)
        landing.raise_for_status()
        
        response = self.session.post(
            PORTAL_URL + "/oauth2/password-login",
            json={"student_id": student_id, "password": password},
            headers={"Origin": PORTAL_URL, "Referer": PORTAL_URL + "/", "Content-Type": "application/json"},
            allow_redirects=False, timeout=30
        )
        if response.status_code not in (200, 201, 202, 204, 302, 303, 307, 308):
            raise Exception("بيانات الدخول غير صحيحة أو الحساب محظور.")

        # تأكيد الجلسة
        test = self.session.get(API_BASE + "/api/study/students/me", timeout=30)
        if test.status_code != 200:
            raise Exception("فشل تأكيد الجلسة مع خادم QUREO.")
        
        return True

    def get_chapters(self):
        response = self.session.get(API_BASE + "/api/study/sections/5", timeout=30)
        if response.status_code != 200: return []
        data = response.json()
        return data.get("chapters", [])

    def start_lectures(self, chapter_id):
        # تشغيل وفتح المحاضرات
        self.session.put(API_BASE + f"/api/study/students/chapters/{chapter_id}/test", timeout=30)