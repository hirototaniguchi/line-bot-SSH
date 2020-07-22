from flask import Flask, request, abort
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request
import os
import random
import json
import linebot
from collections import OrderedDict
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, QuickReply, MessageAction, QuickReplyButton
)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)

# 環境変数取得
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)
SUBJECT_TO_FILENAME = OrderedDict([("英単語","english_words.json"), ("和訳", "wayaku.json"), ("古文", "kobun.json")])

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(80), unique=True, index=True)
    subject = db.Column(db.String(80))
    answer = db.Column(db.String(1024))
    question_no = db.Column(db.Integer)
    correct_num = db.Column(db.Integer)

    def __init__(self, user_id):
        self.user_id = user_id
        self.subject = ""
        self.answer = ""
        self.question_no = -1
        self.correct_num = 0

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

def select_problem(subject):
    file_name = SUBJECT_TO_FILENAME[subject]
    with open(file_name, 'r', encoding='utf-8') as f:
        problems = json.load(f)
    i = random.randrange(len(problems))
    
    problem = problems[i]['problem']
    answers = problems[i]['answers']
    choice_indices = list(range(len(answers)))
    random.shuffle(choice_indices)
    choices = [f"{i+1}: {answers[choice_indices[i]]}" for i in range(len(answers))]
    
    answer_id = choice_indices.index(0)
    answer = f"{answer_id+1}: {answers[0]}"
    return problem, choices, answer

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    user =  User.query.filter_by(user_id=user_id).first()

    # データベースにユーザを登録
    if not user:
        user = User(user_id)
        db.session.add(user)
        db.session.commit()

    send_messages = []

    # 答え合わせ
    if 1 <= user.question_no and user.question_no <= 10:
        # 回答の確認
        answer = event.message.text
        if user.answer == answer:
            answer_text = '正解'
            user.correct_num += 1
        else:
            answer_text = f'間違い．正解は「{user.answer}」です．'
        send_messages.append(TextSendMessage(text=answer_text))

    # 結果集計
    if user.question_no == 10:
        result_text = f'10問中{user.correct_num}問に正解しました'
        send_messages.append(TextSendMessage(text=result_text))

    # 科目
    if user.question_no == -1 or user.question_no == 10:
        # 科目を聞く
        actions = [MessageAction(label=s, text=s) for s in SUBJECT_TO_FILENAME.keys()]
        quick_reply = QuickReply([QuickReplyButton(action=a) for a in actions])
        send_messages.append(TextSendMessage(text="出題分野を選んでください", quick_reply=quick_reply))
    elif user.question_no == 0:
        # 科目回答を確認する
        subject = event.message.text
        if subject in SUBJECT_TO_FILENAME:
            user.subject = subject
        else:
            subject = list(SUBJECT_TO_FILENAME.keys())[0]
            user.subject = subject
            send_messages.append(TextSendMessage(text=f"不正な入力のため{subject}にしました"))

    # 出題
    if 0 <= user.question_no and user.question_no <= 9:
        problem, choices, answer = select_problem(user.subject)
        problem = f'問{user.question_no+1}: ' + problem
        user.answer = answer
        actions = [MessageAction(label=c, text=c) for c in choices]
        quick_reply = QuickReply([QuickReplyButton(action=a) for a in actions])
        send_messages.append(TextSendMessage(text=problem, quick_reply=quick_reply))

    # 状態遷移
    if user.question_no == 10:
        user.subject = ""
        user.question_no = 0
        user.correct_num = 0
    else:
        user.question_no += 1

    db.session.commit()
    line_bot_api.reply_message(
        event.reply_token,
        send_messages
    )

if __name__ == "__main__":
    port = int(os.getenv("PORT"))
    app.run(host="0.0.0.0", port=port)
