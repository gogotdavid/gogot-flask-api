from flask import Flask, request, jsonify
import pymysql
import jwt
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
SECRET_KEY = os.getenv("SECRET_KEY", "defaultsecret")

# ✅ 로그인 API
@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    try:
        conn = pymysql.connect(
            host="117.52.84.19",
            user="david",
            password="Rlawhdgjs1!",
            database="mydatabase",
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor
        )
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cursor.fetchone()
        conn.close()

        if not user:
            return jsonify({"success": False, "message": "존재하지 않는 사용자입니다."})

        # ✅ 평문 비교
        if password != user["password"]:
            return jsonify({"success": False, "message": "비밀번호가 일치하지 않습니다."})

        # ✅ 만료일 확인
        expiry_date = user["expiry_date"]
        if expiry_date and datetime.strptime(str(expiry_date), "%Y-%m-%d").date() < datetime.today().date():
            return jsonify({"success": False, "message": "사용기간이 만료되었습니다."})

        # ✅ JWT 발급
        payload = {
            "username": username,
            "exp": datetime.utcnow() + timedelta(days=1)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

        return jsonify({
            "success": True,
            "token": token,
            "username": username
        })

    except Exception as e:
        return jsonify({"success": False, "message": f"DB 오류: {str(e)}"})

# ✅ 토큰 검증 API
@app.route("/api/check-token", methods=["POST"])
def check_token():
    data = request.json
    token = data.get("token")

    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        username = decoded.get("username")

        # DB 재조회
        conn = pymysql.connect(
            host="117.52.84.19",
            user="david",
            password="Rlawhdgjs1!",
            database="mydatabase",
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor
        )
        cursor = conn.cursor()
        cursor.execute("SELECT expiry_date FROM users WHERE username=%s", (username,))
        user = cursor.fetchone()
        conn.close()

        if not user:
            return jsonify({"valid": False, "reason": "사용자 없음"})

        expiry = datetime.strptime(str(user["expiry_date"]), "%Y-%m-%d").date()
        if expiry < datetime.today().date():
            return jsonify({"valid": False, "reason": "기간 만료"})

        return jsonify({"valid": True, "username": username})

    except jwt.ExpiredSignatureError:
        return jsonify({"valid": False, "reason": "토큰 만료"})
    except jwt.InvalidTokenError:
        return jsonify({"valid": False, "reason": "유효하지 않은 토큰"})

# ✅ Render에서 포트 지정
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
