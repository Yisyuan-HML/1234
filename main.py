from openai import OpenAI  # 新增這行

# 在 app = Flask(...) 與 CORS(app) 後面
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # 新版寫法

# ...

@app.route("/recommend", methods=["POST"])
def recommend():
    data = request.json
    user_prompt = data.get("prompt", "")
    scene = data.get("scene", "")
    selected_url = scene_to_url.get(scene)

    if not selected_url:
        return jsonify({"error": "無法對應情境，請點選指定按鈕。"}), 400

    try:
        res = requests.get(selected_url, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        paragraphs = soup.find_all('p')
        content = "\n".join(p.get_text() for p in paragraphs if p.get_text().strip())
        extracted_text = f"[來源：{selected_url}]\n" + content[:12000]
    except Exception as e:
        extracted_text = f"[來源：{selected_url}] 擷取失敗：{str(e)}"

    system_prompt = (
        "你是一位台灣在地美食推薦助手，僅推薦每個情境的網址內容的所有店家，盡量每間都推薦到，禁止推薦(AGCT Apartment咖啡廳)和(戰醬燒肉)這兩家店。\n"
        "每間餐廳請提供店名、地址、營業時間、價格（僅標註平價、中等價位、高等價位），營業時間如果找不到就寫需直接向店家確認，在店名後面都要加上簡短的推薦原因，根據實際資訊推薦。\n\n"
        f"{extracted_text}\n"
        "每個情境的回覆方式都請照以下格式分別條列兩間推薦店家：\n"
        "🍽 [店名]：...\n"
        "📍 [地址]：...\n"
        "✨ [營業時間]：...\n"
        "💰 [價格]：...\n"
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
