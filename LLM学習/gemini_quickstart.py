import google.generativeai as genai
import os # 環境変数からAPIキーを読み込むためのモジュール

# あなたのAPIキーを設定してください
# 環境変数に設定することが推奨されます。
# 例: os.getenv("GEMINI_API_KEY")

# 直接コードに記述する場合（非推奨ですが、最初はこれで試してもOK）
API_KEY = "AIzaSyANM3Ypt0RdQ1V04JJc79ypN6ZygYKnqCU" # あなたのAPIキーに置き換えてください

# 環境変数から取得する場合
# API_KEY = os.getenv("GEMINI_API_KEY")
# if not API_KEY:
#     print("エラー: GEMINI_API_KEY 環境変数が設定されていません。")
#     exit()

# APIキーを設定
genai.configure(api_key=API_KEY)

# Geminiモデルをロード
model = genai.GenerativeModel(model_name="gemini-1.5-flash") # gemini-2.0-flashは存在しないため、gemini-1.5-flashを推奨

# コンテンツを生成
response = model.generate_content("AIはどのように機能しますか？簡潔に説明してください。")

# 生成されたテキストを出力
print(response.text)