from flask import Flask, request, jsonify
import pymysql
import os

app = Flask(__name__)

@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    user_id = data.get("id")
    pw = data.get("pw")

    conn = pymysql.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        db=os.getenv("DB_NAME"),
        charset="utf8",
        port=int(os.getenv("DB_PORT", "3306"))
    )
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id=%s AND password=%s", (user_id, pw))
    result = cursor.fetchone()
    conn.close()

    if result:
        return jsonify({"success": True, "token": "test-token"})
    return jsonify({"success": False})
