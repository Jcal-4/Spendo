# Setting Up and Using OpenAI API in Your Python Project

This guide will walk you through securely setting up your OpenAI API key and using it in a Python backend project, including best practices for local development and deployment.

## 1. Securely Storing Your OpenAI API Key

**Never hardcode your API key in your code or commit it to version control.**

### On Linux/macOS

1. Open your terminal.
2. Add your API key to your shell profile (e.g., `~/.bashrc`):
   ```bash
   echo 'export OPENAI_API_KEY="your_api_key_here"' >> ~/.bashrc
   source ~/.bashrc
   ```
3. Verify it is set:
   ```bash
   echo $OPENAI_API_KEY
   ```

### On Heroku (or other cloud platforms)

- Set the key as a config var:
  ```bash
  heroku config:set OPENAI_API_KEY=your_api_key_here
  ```
- Or use the dashboard: Settings → Config Vars.

## 2. Accessing the API Key in Python

Use the `os` module to access your API key in your code:

```python
import os
openai_api_key = os.environ.get("OPENAI_API_KEY")
```

data = {
system_message = (

## 3. Using the OpenAI Python SDK (Chat Models)

When using chat models (like GPT-4 or GPT-5), you must use the chat completions endpoint and format your messages as a list of dictionaries. Each dictionary represents a message with a role ("system", "user", or "assistant") and content.

### What is a system message?

The `system_message` is like the initial prompt or instruction for the model. It sets the behavior, context, or persona for the assistant. For example, you can instruct the model to act as a financial advisor, limit its response length, or use a specific tone.

### Adding instructions and limiting response length

You can add instructions (such as limiting the response to a certain number of words or characters) directly in the system message. To further control the output length, use the `max_tokens` parameter in your API call.

### Example: Including user data, instructions, and limiting response length

```python
from openai import OpenAI
import os

openai_api_key = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

data = {
    "cash_balance": "$2,311.43",
    "savings_balance": "$20.43",
    "investing_retirement": "$320.89"
}

user_question = "How can I improve my savings?"

# The system message acts as the prompt for the model's behavior and context
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
    model="gpt-5-nano",  # or "gpt-4" if available
    messages=messages,
    max_tokens=200  # Adjust as needed for your character/word limit
)

print(response.choices[0].message.content.strip())
```

**Key points:**

- The `system_message` is part of the prompt and sets the assistant's behavior.
- Add instructions (like response length) to the system message.
- Use `max_tokens` to further limit the response length.

## 4. Troubleshooting

- If your script cannot find the environment variable, make sure you have sourced your shell profile and are running the script from the same terminal.
- For deployment, always set the environment variable in your deployment environment (not in your code).

## 5. Best Practices

- Never commit your API key to version control.
- Use environment variables for all secrets.
- Always use the correct endpoint for the model you are using (chat models require the chat completions endpoint).

---

This guide should help any first-time user set up and use the OpenAI API securely and correctly in a Python backend project.
