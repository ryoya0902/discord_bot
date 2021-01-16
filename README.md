## Discord Bot  
### インストール
```
git clone https://github.com/ryoya0902/discord_bot
cd discord_bot/
pip install -r requirements.txt
```
### 実行

```
python3 discordbot.py
```
### 対話機能
- SSサイトからスクレイピングで取得した約130万件の対話文をtransformerで学習させました  
- 前処理には全角統一、頻出単語の削除を行っています  
- バックトランスレーション機能を使用すると丁寧口調になります  
- 後処理には一人称の統一、固有名詞の置き換えを行っています  

### その他機能
- 画像検索や天気取得、ニュース取得などの機能があります  
- ログ削除は管理者権限のみ実行できます  
- 強制終了はプログラムを終了させます  

```
/image [word] : wordの画像検索
/news : 技術系ニュース
/tenki : 現在の天気
/clear : ログ削除
/kill : 強制終了
```
### 対話例
