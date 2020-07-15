from flask import Flask, request, abort
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request
import os
import random
import json

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
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)

#環境変数取得
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(80), unique=True)
    answer = db.Column(db.String(80), unique=True)

    def __init__(self, user_id, answer):
        self.user_id = user_id
        self.answer = answer

    def __repr__(self):
        return '<User %r>' % self.user_id


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

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    print("ユーザー名：" + user_id)
    with open("problem.json","r") as f:
        problems=json.load(f)
        print(problems)

    # データベースにユーザを登録
    if not db.session.query(User).filter(User.user_id == user_id).count():
        reg = User(user_id, str(answer))
        db.session.add(reg)
        db.session.commit()

    if "算数" in event.message.text:
        operator = ['+','-','*','/']
        # ope_num = random.randint(0, 3)
        ope_num = 0
        
        r1 = random.randint(0, 10000)
        r2 = random.randint(0, 10000)
        send_text = str(r1) + operator[ope_num] + str(r2)

        answer = r1 + r2

        # Update処理
        reg = User.query.filter_by(user_id=user_id).first()
        reg.answer = answer
        db.session.commit()

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=send_text))
    elif "クイズ" == event.message.text:
        answer = problems["problems"][0]["1"]
        reg = User.query.filter_by(user_id=user_id).first()
        reg.answer = answer
        db.session.commit()
        send_text = problems["problems"][0]["problem"]
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=send_text))

    else:
        answer = User.query.filter_by(user_id = user_id).first().answer
        if event.message.text == answer:
            send_text = "正解"
        else:
            print(event.message.text)
            print(answer)
            send_text = "間違い"

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=send_text))


if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT"))
    app.run(host="0.0.0.0", port=port)
