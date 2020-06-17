from flask import Flask, request, abort
import os
import random

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

app = Flask(__name__)

#環境変数取得
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

@app.route("/")
def hello_world():
    return "hello world!"

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

answer = 0
send_text = ""

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if "算数" in event.message.text:
        r1 = random.randint(0,100)
        r2 = random.randint(0,100)
        answer = r1 + r2
        send_text = str(r1) + " + " + str(r2) 
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=send_text))
    elif str(answer) == event.message.text:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="〇"))
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="×"))


if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT"))
    app.run(host="0.0.0.0", port=port)
