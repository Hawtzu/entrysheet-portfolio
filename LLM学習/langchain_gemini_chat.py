import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import SystemMessage, HumanMessage

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
# ChatGoogleGenerativeAI を使用し、現在安定して利用できるモデル名を指定
# "gemini-1.5-flash" または "gemini-1.5-pro" を推奨します。
model_name = "gemini-2.5-pro"
llm = ChatGoogleGenerativeAI(model=model_name)

# --- プロンプトの作成 ---
messages = [
    SystemMessage(content="あなたはイタリア料理店のシェフです。料理教室も運営しています。"),
    HumanMessage(content="ジャガイモとチーズを使った簡単・おいしい料理のレシピを教えてください"),
]

# --- LLMの呼び出しと結果の出力 ---
try:
    response_content = llm.invoke(messages)
    print("--- レシピ ---")
    print(response_content.content)
except Exception as e:
    print(f"エラーが発生しました: {e}")
    print("APIキー、指定したモデル名、またはネットワーク接続を確認してください。")