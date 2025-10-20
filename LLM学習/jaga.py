import google.generativeai as genai
import os # 環境変数からAPIキーを読み込むために必要です

# --- APIキーの設定 ---
# 環境変数からAPIキーを読み込みます。
# あなたの環境に GOOGLE_API_KEY が正しく設定されていることを前提とします。
api_key = os.getenv("GOOGLE_API_KEY")

# APIキーが取得できたか確認します。
if not api_key:
    print("エラー: 環境変数 GOOGLE_API_KEY が設定されていません。")
    print("APIキーを環境変数に設定し、VS Codeやターミナルを再起動してから再度お試しください。")
    exit() # プログラムを終了します

# 取得したAPIキーを使ってGemini APIを設定します。
genai.configure(api_key=api_key)

# --- モデルのロード ---
# gemini-proではなく、generate_contentに対応しているモデルを指定します。
# 一般的に利用可能で推奨されるのは "gemini-1.5-flash" または "gemini-1.5-pro" です。
# どちらか一方を選んでください。ここでは "gemini-1.5-flash" を例とします。
model_name = "gemini-1.5-flash" # または "gemini-1.5-pro"
model = genai.GenerativeModel(model_name)

# --- プロンプトとコンテンツ生成 ---
prompt = "ジャガイモとチーズを使った簡単・おいしい料理のレシピを教えてください"

# コンテンツを生成します。
try:
    response = model.generate_content(prompt)
    # 生成されたテキストを出力します。
    print(response.text)
except Exception as e:
    print(f"コンテンツ生成中にエラーが発生しました: {e}")
    print("APIキー、モデル名、またはネットワーク接続を確認してください。")