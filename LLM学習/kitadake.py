import os
from langchain_google_genai import ChatGoogleGenerativeAI # Geminiを使うためのインポート
from langchain.schema import HumanMessage

# --- APIキーの設定 ---
# 環境変数 GOOGLE_API_KEY からAPIキーを読み込みます。
# これが推奨される方法であり、このコードはこの環境変数が設定されていることを前提とします。
api_key = os.getenv("GOOGLE_API_KEY")

# APIキーが設定されていない場合はエラーメッセージを出力し、プログラムを終了します。
if not api_key:
    print("エラー: 環境変数 GOOGLE_API_KEY が設定されていません。")
    print("APIキーを環境変数に設定し、VS Codeやターミナルを再起動してから再度お試しください。")
    print("例: export GOOGLE_API_KEY=\"あなたのAPIキー\"")
    exit() # プログラムを終了

# --- モデルの初期化 ---
# ChatGoogleGenerativeAI を使用し、Geminiモデルを指定します。
# "gemini-1.5-flash" または "gemini-1.5-pro" を推奨します。
# あなたの環境で動作した "gemini-2.5-flash" も利用できます。
model_name = "gemini-1.5-flash" # または "gemini-2.5-flash", "gemini-1.5-pro"
llm = ChatGoogleGenerativeAI(model=model_name) # ここを ChatGoogleGenerativeAI に変更

# --- プロンプトの作成と実行 ---
try:
    response = llm.invoke(
        [
            HumanMessage("男子バレーボールにおいて，日本で一番強いレフトのプレイヤーは誰ですか？また，その理由は？")
        ]
    )
    # 結果は .content で取得
    print(response.content)
except Exception as e:
    print(f"エラーが発生しました: {e}")
    print("APIキー、指定したモデル名、またはネットワーク接続を確認してください。")