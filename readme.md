# 開発の準備
* herokuとLINE Developerの登録，その他ライブラリなどの準備
    * https://qiita.com/shimajiri/items/cf7ccf69d184fdb2fb26
* データベースの準備
    * https://qiita.com/takechanman1228/items/917e2eb47fa21f866cb4
        * 記事内の「flask.ext.sqlalchemy」は非推奨であるため，代わりに「flask_sqlalchemy」を使う
# 挨拶メッセージの設定
* LINE Developersにログインし，対象Providerの「Messaging API」を開く
    ![messagin-API](https://user-images.githubusercontent.com/32231297/87848931-a6555200-c91f-11ea-8445-ef683db8e762.png)
* 「LINE Official Account features」の「Greeting messages」の「Edit」をクリックする
    ![edit](https://user-images.githubusercontent.com/32231297/87848965-faf8cd00-c91f-11ea-9838-11e334058674.png)
* あいさつメッセージをオンにし，「あいさつメッセージ設定」をクリックしてメッセージを設定する
    * 例：「クイズを開始するにはメッセージを送ってください！」
    ![on](https://user-images.githubusercontent.com/32231297/87849056-896d4e80-c920-11ea-9e61-9b6a607a9761.png)

# 出題問題の追加
## 既存の分野の問題を追加する場合
1. 対象のjsonファイルを開く
2. 角かっこ内に```{"problem":"出題したい文", "answers":["正解の選択肢", "不正解の選択肢1" "不正解の選択肢2", "不正解の選択肢3"]}```のように記述して問題を追加
    * **選択肢の1つ目を正解にしなければならないため注意**
* 記述の例
    ```json
    [
        {"problem":"投げかける","answers":["cast","interpret","deprive of","classify"]},
        {"problem":"のせいだとされる", "answers": ["is attributed to", "be obliged to", "deserve to be", "forbid to"]},
        {"problem":"凍えて", "answers": ["freeze", "entertain", "strain", "fee"]},
        {"problem":"解決する", "answers": ["resolve", "prejudice", "undergo", "resort"]},
        {"problem":"受け入れる", "answers": ["embrace", "withdraw", "enterprise", "eliminate"]},
        {"problem":"展示する", "answers": ["exhibit", "interpret", "restrict", "exaggerate"]}
    ]
    ```
## 新しい分野を追加する場合
1. main.pyが存在するファイル内に，新しいjsonファイルを作成する（**選択肢の1つ目を正解にしなければならないため注意**）
    * 例：「chemistry.json」
        ```json
        [
            {"problem":"He", "answers":["ヘリウム", "水素", "マグネシウム", "リン"]}
        ]
        ```
2. main.pyの29行目にある「OrderedDict」の角かっこ内に```, ("ユーザに表示したい科目名", "作成したjsonのファイル名")```を追加して完了
    * 変更前
        ```python
        SUBJECT_TO_FILENAME = OrderedDict([("英単語","english_words.json")])
        ```
    * 変更後
        ```python
        SUBJECT_TO_FILENAME = OrderedDict([("英単語","english_words.json"), ("化学", "chemistry.json")])
        ```

