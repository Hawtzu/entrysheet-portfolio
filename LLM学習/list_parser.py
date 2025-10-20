import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import HumanMessagePromptTemplate, ChatPromptTemplate
from langchain.output_parsers import CommaSeparatedListOutputParser

# APIキーを環境変数から読み込み、設定
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("エラー: 環境変数 GOOGLE_API_KEY が設定されていません。")
    exit()

# Geminiモデルを初期化 (gemini-2.5-flashを使用)
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

# CommaSeparatedListOutputParserを初期化
list_parser = CommaSeparatedListOutputParser()

# プロンプトテンプレートを定義
template = ChatPromptTemplate.from_messages([
    HumanMessagePromptTemplate.from_template(
        "{item}の種類を{count}個列挙してください。要素は,で区切ってください"
    )
])

# LCELを使ってチェーンを構築: プロンプトテンプレート -> LLM -> CommaSeparatedListOutputParser
chain = template | llm | list_parser

# チェーンを実行し、結果を出力
try:
    response = chain.invoke({"item": "アイスクリーム", "count": "5"})
    
    # CommaSeparatedListOutputParserによってPythonのリストに変換済み
    print(response)
    print(type(response))

except Exception as e:
    print(f"エラーが発生しました: {e}")