import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.output_parsers.json import SimpleJsonOutputParser # For parsing JSON output
import json # To pretty-print the JSON output

# Set up API key
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("Error: GOOGLE_API_KEY environment variable is not set.")
    exit()

# Initialize Gemini model
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

# Define the human message template for JSON generation
human_str = """
ランダムなデータが必要です。生徒{count}人分のダミーデータをJSON形式で生成してください。

各生徒のデータは以下の形式でお願いします:
"name": 氏名,
"age": 年齢,
"hobby": 趣味
"""
human_template = HumanMessagePromptTemplate.from_template(human_str)

# Create the chat prompt template
template = ChatPromptTemplate.from_messages([
    human_template
])

# Initialize the JSON output parser
json_parser = SimpleJsonOutputParser()

# Build the LCEL chain: prompt template -> LLM -> JSON parser
chain = template | llm | json_parser

# Invoke the chain and print the response
try:
    response = chain.invoke({"count": 3})
    
    # The SimpleJsonOutputParser already converts it to a Python object (list/dict)
    # We can use json.dumps for pretty printing if needed
    print(json.dumps(response, indent=2, ensure_ascii=False)) 
    print(type(response))

except Exception as e:
    print(f"An error occurred: {e}")