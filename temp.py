import json
import random

# 答え合わせ
if 1 <= user.question_no and user.question_no <= 10:
    # TODO 回答の確認
    if user.answer == answer:
        answer_text = '正解！'
        user.correct_num += 1
    else:
        answer_text = f'間違い．正解は{answer}です．'
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=answer_text)
    )

# 結果集計
if user.question_no == 10:
    result_text = f'10問中{user.correct_num}問に正解しました'
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=result_text)
    )

# 科目
if user.question_no == -1 or user.question_no == 10:
    # TODO 科目を聞く
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=xxxxx)
    )
elif user.question_no == 0:
    # TODO 科目回答を確認する
    user.subject = subject

# 出題
if 0 <= user.question_no and user.question_no <= 9:
    problem_text, choices, answer = select_problem(subject)
    problem_text = f'問{user.question_no+1}: ' + problem_text
    user.answer = answer
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=problem_text)
    )

# 状態遷移
if user.question_no == 10:
    user.question_no = 0
    user.correct_num = 0
    user.subject = ""
else:
    user.question_no += 1

db.session.commit()


def select_problem(subject):
    with open(subject + '.json', 'r', encoding='utf-8') as f:
        problems = json.load(f)
    i = random.randrange(len(problems))
    
    problem = problems[i]['problem']
    answers = problems[i]['answers']
    choice_indices = list(range(len(answers)))
    random.shuffle(answer_indices)
    choices = [f"{i+1}: {answers[choice_indices[i]]}" for i in range(len(answers))]
    
    answer_id = choice_indices.index(0)
    answer = f"{answer_id+1}: {answers[answer_id]}"
    return problem, choices, answer