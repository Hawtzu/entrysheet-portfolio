import os
import json # JSON出力の整形表示のために必要です

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.output_parsers.json import SimpleJsonOutputParser # SimpleJsonOutputParserをインポート

# --- APIキーの設定 ---
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("エラー: 環境変数 GOOGLE_API_KEY が設定されていません。")
    exit()

# --- Geminiモデルの初期化 (gemini-2.5-flashを使用) ---
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

# --- プロンプトテンプレートの定義 ---
human_str = """
ランダムなデータが必要です。生徒{count}人分のダミーデータをJSON形式で生成してください。

各生徒のデータは以下の形式でお願いします:
"name": 氏名,
"age": 年齢,
"hobby": 趣味
"""
human_template = HumanMessagePromptTemplate.from_template(human_str)

template = ChatPromptTemplate.from_messages([
    human_template
])

# --- LCELを使ってチェーンを構築 ---
# プロンプトテンプレート -> LLM -> SimpleJsonOutputParser
# SimpleJsonOutputParserがLLMのテキスト出力をPythonのJSONオブジェクトに変換します。
chain = template | llm | SimpleJsonOutputParser()

# --- チェーンの実行と結果の出力 ---
try:
    response = chain.invoke({"count": 3})
    
    # SimpleJsonOutputParserによって既にPythonオブジェクトに変換されているため、
    # json.dumpsを使って整形して表示すると、より見やすくなります (日本語対応)。
    print(json.dumps(response, indent=2, ensure_ascii=False))
    print(type(response))

except Exception as e:
    print(f"エラーが発生しました: {e}")