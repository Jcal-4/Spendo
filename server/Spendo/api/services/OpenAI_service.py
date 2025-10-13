from openai import OpenAI
import os
openai_api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=openai_api_key)

def analyze_user_message(message):
    response = client.responses.create(
        prompt={
            "id": "pmpt_68c1c8c9b8908190add547c625d1be4004d1e9d14ef967a3",
            "version": "9"
        },
        input=[
            {
                "role": "user",
                "content": message  # your user message here
            }
        ]
    )
    
    if not response:
        return "No response from openAI"
    return response
    
    

# An example if a quick custom prompt is needed
# def backened_prompt_example(request):
#     user_message = request.data.get('user_message')
#     # user_accounts_data = get_accounts_by_userid(request.data.get('user_id'))
#     user_accounts_data = request.data.get('user_balance')
#     # Combine user data and question into a message
#     system_message = (
#         f"You are a well-versed financial advisor. Limit the response to under 500 characters.\n"
#         f"If the question is pertaining to anything about how they can manage their money then make sure to respond with a brief description of their current balances. Only do this if it benefits the response and try to only repeat this once in a conversation unless asked for this information again."
#         f"Format your answer with clear paragraphs and line breaks. Use bullet points if listing items."
#         f"Here is the user's financial data:\n"
#         f"Cash balance: {user_accounts_data['cash_balance']}\n"
#         f"Savings balance: {user_accounts_data['savings_balance']}\n"
#         f"Investing/Retirement: {user_accounts_data['investing_retirement']}"
#     )

#     messages = [
#         {"role": "system", "content": system_message},
#         {"role": "user", "content": user_message}
#     ]

#     response = client.chat.completions.create(
#         model="gpt-5-nano",
#         messages=messages
#     )
    
#     if not response:
#         return Response('No response from openAI')
#     return Response({"result": response.choices[0].message.content})
#     # return Response({"result": "fake return"})