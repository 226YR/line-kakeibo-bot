from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os
from dotenv import load_dotenv
from db import init_db, add_purchase, delete_purchase, get_monthly_total

load_dotenv()
app = Flask(__name__)
init_db()

line_bot_api = LineBotApi(os.environ['LINE_CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['LINE_CHANNEL_SECRET'])

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK',200

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    print(f"Received message: {event.message.text}")
    user_id = event.source.user_id
    text = event.message.text.strip()
    if text.startswith("buy "):
        try:
            _, item, price = text.split()
            add_purchase(user_id, item, int(price))
            reply = f"{item} を {price} 円で登録しました。"
        except:
            reply = "形式が正しくありません。例: buy 牛乳 200"
    elif text.startswith("delete "):
        _, item = text.split()
        delete_purchase(user_id, item)
        reply = f"{item} を削除しました。"
    elif text.startswith("view"):
        parts = text.split()
        if len(parts) == 2:
            year_month = parts[1]
            total = get_monthly_total(user_id, year_month)
            reply = f"{year_month} の合計は {total} 円です。"
        elif len(parts) == 1:
            total = get_monthly_total(user_id)
            reply = f"今月の合計は {total} 円です。"
        else:
            reply = "形式が正しくありません。例: view または view 2024-12"
    else:
        reply = "コマンドが不明です。buy / delete / view を使ってください。"

    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))

if __name__ == "__main__":
    app.run(port=5000)
