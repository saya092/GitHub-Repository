#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 19 15:58:47 2025

@author: monicahu
"""

from flask import Flask, request, render_template_string, redirect, url_for
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# 建立上傳資料夾
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# 判斷檔案是否為允許格式
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 模擬分類器
def classify_image(filename):
    # 模擬判斷邏輯，可依需求替換成真正 AI 模型
    if "plastic" in filename.lower():
        return "🔁 可回收：塑膠類"
    elif "paper" in filename.lower():
        return "🔁 可回收：紙類"
    elif "metal" in filename.lower():
        return "🔁 可回收：金屬類"
    else:
        return "🚫 不可回收"

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    html = """
    <!DOCTYPE html>
    <html lang="zh">
    <head>
        <meta charset="UTF-8">
        <title>資源回收辨識系統</title>
        <style>
            body { font-family: Arial; background: #f0f2f5; display: flex; justify-content: center; align-items: center; height: 100vh; }
            .container { background: white; padding: 40px; border-radius: 10px; box-shadow: 0 8px 16px rgba(0,0,0,0.1); text-align: center; width: 350px; }
            h1 { margin-bottom: 20px; }
            input[type=file] { margin: 15px 0; }
            button { padding: 10px 20px; background: #3498db; color: white; border: none; border-radius: 5px; cursor: pointer; }
            button:hover { background: #2980b9; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>♻️ 資源回收分類辨識</h1>
            <form method="POST" enctype="multipart/form-data">
                <input type="file" name="file"><br>
                <button type="submit">上傳並辨識</button>
            </form>
            {% if result %}
                <h3>分類結果：</h3>
                <p><strong>{{ result }}</strong></p>
                <img src="{{ url_for('static', filename='uploads/' + filename) }}" width="250">
            {% endif %}
        </div>
    </body>
    </html>
    """
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template_string(html, result="未選擇檔案")
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(save_path)
            result = classify_image(filename)
            return render_template_string(html, result=result, filename=filename)
        else:
            return render_template_string(html, result="不支援的檔案類型")
    return render_template_string(html)

if __name__ == '__main__':
    app.run(debug=True, port=5059, host='0.0.0.0')