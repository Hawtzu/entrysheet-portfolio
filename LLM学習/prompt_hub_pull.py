# --- コード概要 ---
# このスクリプトは、LangChain Hub (プロンプトハブ) から
# 共有されているプロンプトをダウンロードし、その内容を表示します。
# ------------------

from langchain import hub # hubモジュールをインポート

# プロンプトハブから特定のプロンプトをプル（ダウンロード）
# "pollychi/rag_japanese_1" は日本語RAGのプロンプトの一例
prompt = hub.pull("pollychi/rag_japanese_1")

# ダウンロードしたプロンプトの内容を表示
# プロンプトオブジェクトは通常、format()やformat_messages()で使うため、
# その内容を確認するには .messages プロパティなどを参照します。
print("--- ダウンロードされたプロンプトの構造 ---")
print(prompt) # プロンプトオブジェクトそのもの
print("\n--- プロンプトメッセージの内容 ---")
# ChatPromptTemplate の場合は .messages プロパティで中身を確認
if hasattr(prompt, 'messages'):
    for msg_template in prompt.messages:
        print(f"タイプ: {type(msg_template).__name__}, 内容: {msg_template.prompt.template}")
else:
    print("このプロンプトはChatPromptTemplate形式ではないか、メッセージ構造を持っていません。")