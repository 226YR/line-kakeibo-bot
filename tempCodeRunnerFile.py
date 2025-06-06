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
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
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
    elif text == "view":
        total = get_monthly_total(user_id)
        reply = f"今月の合計は {total} 円です。"
    else:
        reply = "コマンドが不明です。buy / delete / view を使ってください。"

    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
