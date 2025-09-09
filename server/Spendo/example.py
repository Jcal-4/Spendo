import os
from openai import OpenAI

openai_api_key = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

data = {
    "cash_balance": "$2,311.43",
    "savings_balance": "$20.43",
    "investing_retirement": "$320.89"
}

user_question = "How can I improve my savings?"

# Combine user data and question into a message
system_message = (
    f"You are a well-versed financial advisor. Limit the response to under 150 words.\n"
    f"If the question is pertaining to anything about how they can manage their money then make sure to respond with a brief description of their current balances. Only do this if it benefits the response."
    f"Here is the user's financial data:\n"
    f"Cash balance: {data['cash_balance']}\n"
    f"Savings balance: {data['savings_balance']}\n"
    f"Investing/Retirement: {data['investing_retirement']}"
)

messages = [
    {"role": "system", "content": system_message},
    {"role": "user", "content": user_question}
]

response = client.chat.completions.create(
    model="gpt-5-mini",
    messages=messages
)

print(response.choices[0].message.content.strip())