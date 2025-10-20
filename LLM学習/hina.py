# --- コード概要 ---
# このスクリプトは、LangChain入門(2) – プロンプト/LCELの使い方 で一番最初に紹介された
# 会話形式のプロンプト入力の例を、Google Gemini (gemini-2.5-flash) を使って再現したものです。
# LLM（大規模言語モデル）に質問を投げかけ、その応答を表示します。
# GOOGLE_API_KEY 環境変数からAPIキーを読み込みます。
# LangChainのChat Modelの基本的な呼び出し方を示しています。
# ------------------
import os
from langchain_google_genai import ChatGoogleGenerativeAI # Geminiを使うためのインポート

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
# ChatGoogleGenerativeAI を使用し、gemini-2.5-flash モデルを指定します。
model_name = "gemini-2.5-flash"
llm = ChatGoogleGenerativeAI(model=model_name)

# --- プロンプトの定義 ---
# ここでは例として、HumanMessageを使用します。
# 元のコードには `prompt` 変数の定義がないため、仮で定義しています。
# 実際には、ご自身のコードに合わせて prompt 変数を定義してください。
from langchain.schema import HumanMessage
prompt = HumanMessage(content="今日の天気について教えてください。")


# --- LLMの呼び出しと結果の出力 ---
try:
    response = llm.invoke([prompt]) # invokeにはリスト形式でメッセージを渡します
    print(response.content)
except Exception as e:
    print(f"エラーが発生しました: {e}")
    print("APIキー、指定したモデル名、またはネットワーク接続を確認してください。")