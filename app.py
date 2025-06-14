from flask import Flask, request, jsonify
import pymysql
import os

app = Flask(__name__)

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
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        result = cursor.fetchone()
        conn.close()

        if result:
            return jsonify({"success": True, "token": "test-token"})
        else:
            return jsonify({"success": False, "message": "ID 또는 PW가 틀렸습니다."})
    except Exception as e:
        return jsonify({"success": False, "message": f"DB 오류: {str(e)}"})

# 🚨 포트 지정 (Render용)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
