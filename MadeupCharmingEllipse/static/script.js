async function fetchRecommendation(sceneKey) {
  const output = document.getElementById("output");
  const promptMap = {
    "別餓到了": "請推薦兩間網址內的小吃店。",
    "讀書好去處": "請推薦兩間網址內適合讀書的咖啡廳。",
    "宵夜吃飽飽": "請推薦兩間網址內適合當宵夜的店。",
    "小小點心": "請推薦網址內兩間甜點、點心店。"
  };
  const prompt = promptMap[sceneKey] || sceneKey;
  output.innerText = "推薦中，請稍候...";
  const res = await fetch("/recommend", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      prompt: prompt,
      scene: sceneKey
    })
  });
  const data = await res.json();
  if (data.reply) {
    const formatted = data.reply.replace(
      /🔗 \[參考連結\]：(https?:\/\/[^\s]+)/g,
      '🔗 <a href="$1" target="_blank">$1</a>'
    );
    output.innerHTML = formatted.replace(/\n/g, "<br>");
    document.getElementById("reward-section").style.display = "block";
  } else {
    output.innerText = "錯誤：" + data.error;
  }
}
function showReward() {
  const images = [
    "/static/ramen.jpg",
    "/static/cute.jpg",
    "/static/pink-happy.jpg",
    "/static/strawberry-cake.jpg"
  ];
  const messages = [
    "今天也好好吃飯了呢！",
    "吃飽才有力氣打拼！",
    "好棒～又完成一天的任務了！",
    "繼續努力，美食能量UP！"
  ];
  const index = Math.floor(Math.random() * images.length);
  const img = images[index];
  const msg = messages[index];
  document.getElementById("reward-area").innerHTML = `
    <img src="${img}" style="width: 160px; border-radius: 12px;"><br>
    <p style="font-weight: bold; margin-top: 10px; color: #e67373;">${msg}</p>
  `;
}
