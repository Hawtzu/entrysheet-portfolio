import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.output_parsers import StrOutputParser

# APIキーを環境変数から読み込み、設定
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("エラー: 環境変数 GOOGLE_API_KEY が設定されていません。")
    exit()

# Geminiモデルを初期化 (gemini-2.5-flashを使用)
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

# StrOutputParserを初期化
str_parser = StrOutputParser()

# プロンプトテンプレートを定義
system_template = SystemMessagePromptTemplate.from_template("{lang_from}から{lang_to}への翻訳を行います")
human_template = HumanMessagePromptTemplate.from_template("「{text}」を翻訳してください")
template = ChatPromptTemplate.from_messages([
    system_template,
    human_template
])

# LCELを使ってチェーンを構築: プロンプトテンプレート -> LLM -> 文字列パーサー
chain = template | llm | str_parser

# チェーンを実行し、結果を変数に格納
response = chain.invoke({"lang_to":"英語", "lang_from":"日本語", "text":"今日はいい天気ですね"})

# PythonのインタラクティブシェルやJupyter Notebookでは、
# 最後の行に変数を書くとその内容が出力されます。
# 通常のスクリプト実行の場合は print(response) を使用します。
response