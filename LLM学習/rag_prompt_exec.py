import os
from langchain_google_genai import ChatGoogleGenerativeAI # Geminiを使うためのインポート
from langchain_core.output_parsers import StrOutputParser
from langchain import hub # hubモジュールをインポート

# --- APIキーの設定 ---
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("エラー: 環境変数 GOOGLE_API_KEY が設定されていません。")
    exit()

# --- プロンプトハブからプロンプトをプル ---
# "pollychi/rag_japanese_1" は日本語RAG用のプロンプト
prompt = hub.pull("pollychi/rag_japanese_1")

# --- Geminiモデルを初期化 (gemini-2.5-flashを使用) ---
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

# --- StrOutputParserを初期化 ---
str_parser = StrOutputParser()

# --- LCELを使ってチェーンを構築 ---
# プロンプトテンプレート -> LLM -> 文字列パーサー
chain = prompt | llm | str_parser

# --- チェーンを実行し、結果を出力 ---
try:
    response = chain.invoke({
        "context": "税務関係に詳しい専門家です。小学生にもわかるようシンプル・平易に説明します。",
        "question": "累進課税とはどのような制度ですか？"
    })
    print(response)
except Exception as e:
    print(f"エラーが発生しました: {e}")