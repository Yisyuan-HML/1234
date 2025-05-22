import requests
from bs4 import BeautifulSoup
import os
from openai import OpenAI
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# OpenAI GPT 金鑰來自環境變數
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 各情境對應的資料來源網址
scene_to_url = {
    "別餓到了": "https://lordcat.net/archives/454",
    "讀書好去處": "https://today.line.me/tw/v2/article/1DBvKoz",
    "宵夜吃飽飽": "https://dpmm2021.pixnet.net/blog/post/161621317",
    "小小點心": "https://www.juksy.com/article/120736"
}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/recommend", methods=["POST"])
def recommend():
    data = request.json
    user_prompt = data.get("prompt", "")
    scene = data.get("scene", "")
    selected_url = scene_to_url.get(scene)

    if not selected_url:
        return jsonify({"error": "無法對應情境，請點選指定按鈕。"}), 400

    # 擷取該情境對應網址的文字內容
    try:
        res = requests.get(selected_url, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        paragraphs = soup.find_all('p')
        content = "\n".join(p.get_text() for p in paragraphs if p.get_text().strip())
        extracted_text = f"[來源：{selected_url}]\n" + content[:12000]
    except Exception as e:
        extracted_text = f"[來源：{selected_url}] 擷取失敗：{str(e)}"

    # GPT 輸入 prompt
    system_prompt = (
        "你是一位台灣在地美食推薦助手，僅推薦每個情境的網址內容的所有店家，盡量每間都推薦到，禁止推薦(AGCT Apartment咖啡廳)和(戰醬燒肉)這兩家店。\n"
        "每間餐廳請提供店名、地址、營業時間、價格（平價、中等價位、高等價位），如查無營業時間請註明『需向店家確認』。\n"
        "在店名後面請加上簡短推薦理由（根據資料來源，不可捏造）。\n\n"
        f"{extracted_text}\n"
        "根據使用者需求，請回覆兩間符合情境的推薦，格式如下：\n"
        "🍽 [店名]：...\n📍 [地址]：...\n✨ [營業時間]：...\n💰 [價格]：...\n"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7
        )
        reply = response.choices[0].message.content
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)
