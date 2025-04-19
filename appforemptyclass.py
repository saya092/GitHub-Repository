#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 19 10:59:36 2025

@author: monicahu
"""

from flask import Flask, request, jsonify, render_template_string, redirect, url_for
import json, os
from collections import defaultdict
import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt
import base64
from io import BytesIO

app = Flask(__name__)
room_file = "room_status.json"
log_file = "room_log.json"

default_rooms = {"B101": "empty", "B102": "empty", "B103": "empty"}

if not os.path.exists(room_file):
    with open(room_file, "w") as f:
        json.dump(default_rooms, f, indent=2)

if not os.path.exists(log_file):
    with open(log_file, "w") as f:
        json.dump({room: 0 for room in default_rooms}, f, indent=2)

def update_status(room, status):
    with open(room_file) as f:
        data = json.load(f)
    data[room] = status
    with open(room_file, "w") as f:
        json.dump(data, f, indent=2)
    if status == "occupied":
        with open(log_file) as f:
            log = json.load(f)
        log[room] += 1
        with open(log_file, "w") as f:
            json.dump(log, f, indent=2)

def get_texts(lang):
    texts = {
        "zh": {
            "title": "教室狀態查詢",
            "heading": "📱 教室狀態",
            "occupied": "❌ 使用中",
            "empty": "✅ 空教室",
            "reserve": "預約",
            "release": "釋放",
            "search": "🔍 查詢空教室",
            "usage": "📊 使用統計"
        },
        "en": {
            "title": "Classroom Status",
            "heading": "📱 Classroom Status",
            "occupied": "❌ Occupied",
            "empty": "✅ Available",
            "reserve": "Reserve",
            "release": "Release",
            "search": "🔍 Search Available",
            "usage": "📊 Usage Chart"
        }
    }
    return texts.get(lang, texts["zh"])

@app.route("/view")
def view_status():
    lang = request.args.get("lang", "zh")
    texts = get_texts(lang)

    with open(room_file) as f:
        rooms = json.load(f)

    html = """
    <!DOCTYPE html>
    <html lang="{{ lang }}">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{{ texts["title"] }}</title>
        <style>
            body {
                margin: 0;
                font-family: "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                background: #f4f6f8;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
            }
            .phone {
                width: 360px;
                background: white;
                border-radius: 25px;
                box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
                padding: 20px;
            }
            h1 {
                text-align: center;
                color: #333;
            }
            .room {
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 15px;
                margin: 10px 0;
                display: flex;
                justify-content: space-between;
                align-items: center;
                background-color: #fafafa;
                transition: 0.2s;
            }
            .room:hover {
                background-color: #f0f0f0;
            }
            .occupied {
                color: #e74c3c;
                font-weight: bold;
            }
            .empty {
                color: #2ecc71;
                font-weight: bold;
            }
            a.button {
                padding: 6px 12px;
                background: #3498db;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                font-size: 14px;
                transition: background 0.2s;
            }
            a.button:hover {
                background: #2980b9;
            }
            .footer-links {
                margin-top: 20px;
                text-align: center;
            }
            .footer-links a {
                margin: 0 10px;
                text-decoration: none;
                color: #555;
                font-size: 14px;
            }
            select {
                margin-bottom: 10px;
                width: 100%;
                padding: 6px;
                border-radius: 6px;
                border: 1px solid #ccc;
            }
        </style>
    </head>
    <body>
        <div class="phone">
            <form method="get" onchange="this.submit()">
                <select name="lang">
                    <option value="zh" {% if lang == 'zh' %}selected{% endif %}>中文</option>
                    <option value="en" {% if lang == 'en' %}selected{% endif %}>English</option>
                </select>
            </form>
            <h1>{{ texts["heading"] }}</h1>
            {% for room, status in rooms.items() %}
                <div class="room">
                    <span>{{ room }} - 
                    {% if status == 'occupied' %}
                        <span class="occupied">{{ texts["occupied"] }}</span>
                    {% else %}
                        <span class="empty">{{ texts["empty"] }}</span>
                    {% endif %}
                    </span>
                    {% if status == 'occupied' %}
                        <a class="button" href="{{ url_for('release', room=room) }}?lang={{ lang }}">{{ texts["release"] }}</a>
                    {% else %}
                        <a class="button" href="{{ url_for('reserve', room=room) }}?lang={{ lang }}">{{ texts["reserve"] }}</a>
                    {% endif %}
                </div>
            {% endfor %}
            <div class="footer-links">
                <a href="{{ url_for('search_empty') }}?lang={{ lang }}">{{ texts["search"] }}</a> |
                <a href="{{ url_for('usage_chart') }}">{{ texts["usage"] }}</a>
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(html, rooms=rooms, lang=lang, texts=texts)

@app.route("/reserve/<room>")
def reserve(room):
    update_status(room, "occupied")
    return redirect(url_for("view_status", lang=request.args.get("lang", "zh")))

@app.route("/release/<room>")
def release(room):
    update_status(room, "empty")
    return redirect(url_for("view_status", lang=request.args.get("lang", "zh")))

@app.route("/search/empty")
def search_empty():
    lang = request.args.get("lang", "zh")
    texts = get_texts(lang)
    with open(room_file) as f:
        data = json.load(f)
    empty_rooms = [r for r, s in data.items() if s == "empty"]
    return f"<h2>{texts['search']}</h2>" + "<br>".join(f"{texts['empty']} {r}" for r in empty_rooms) + f'<br><br><a href="{url_for("view_status", lang=lang)}">返回</a>'

@app.route("/usage")
def usage_chart():
# %%
    with open(log_file) as f:

        log = json.load(f)

    rooms = list(log.keys())
    counts = list(log.values())

    plt.figure(figsize=(6, 4))
    plt.bar(rooms, counts)
    plt.xlabel("教室")
    plt.ylabel("使用次數")
    plt.title("教室使用統計")
    buf = BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    img_data = base64.b64encode(buf.read()).decode("utf-8")
    buf.close()

    return f'<h2>Classroom usage statistics chart</h2><img src="data:image/png;base64,{img_data}"><br><a href="{url_for("view_status")}">back</a>'

if __name__ == '__main__':
    app.run(debug=True, port=5006, host='0.0.0.0')