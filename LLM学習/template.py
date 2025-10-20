# --- コード概要 ---
# このスクリプトは、LangChain入門(2) – プロンプト/LCELの使い方 で紹介されている
# プロンプトテンプレートの作成と変数埋め込みの例を再現したものです。
# 具体的には、翻訳タスク用のChatPromptTemplateを定義し、変数に値を埋め込んだ結果を表示します。
# ------------------

# LLMの呼び出しは含まれませんが、ChatPromptTemplateの定義には必要なのでインポート
# from langchain_google_genai import ChatGoogleGenerativeAI
import os # 環境変数 GOOGLE_API_KEY が必要な場合のために念のため
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
# LangChainのスキーマはChatPromptTemplate内で自動的に使用されるため、
# print(prompt) の目的であれば直接インポートは不要ですが、他の用途で使う可能性を考慮し含めてもOK
# from langchain.schema import SystemMessage, HumanMessage

# --- プロンプトテンプレートの定義 ---
# SystemMessagePromptTemplateを使って、システムメッセージのテンプレートを作成
system_template = SystemMessagePromptTemplate.from_template("{lang_from}から{lang_to}への翻訳を行います")

# HumanMessagePromptTemplateを使って、ユーザーメッセージのテンプレートを作成
human_template = HumanMessagePromptTemplate.from_template("「{text}」を翻訳してください")

# ChatPromptTemplateを使って、会話全体のテンプレートを構築
# from_messages にメッセージテンプレートのリストを渡します
template = ChatPromptTemplate.from_messages([
    system_template,
    human_template
])

# --- テンプレートに変数を埋め込み、プロンプトを生成 ---
# formatメソッドを使って、テンプレートのプレースホルダーに変数を埋め込みます
prompt = template.format(lang_to="英語", lang_from="日本語", text="今日はいい天気ですね")

# --- 生成されたプロンプトを表示 ---
print(prompt)