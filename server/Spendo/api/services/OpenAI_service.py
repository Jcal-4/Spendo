# from openai import OpenAI
# import os
# openai_api_key = os.getenv('OPENAI_API_KEY')
# client = OpenAI(api_key=openai_api_key)


from pydantic import BaseModel
from agents import Agent, ModelSettings, RunContextWrapper, TResponseInputItem, Runner, RunConfig, trace
from openai.types.shared.reasoning import Reasoning

class FinancialReasoningSchema(BaseModel):
  validpromptresponse: bool
  financequestion: bool
  monetarybalancequery: bool
  tentativeresponse: str


financial_reasoning = Agent(
  name="Financial Reasoning",
  instructions="""You are to assist with analyzing the users message and based on their messages you are to respond with one of three options depending on which criteria are met:


Option 1: The User message directly revolves around concerns about finances
Return:  An object in the following format
{\"validPromptResponse\": true, \"financequestion\": true, \"monetaryBalanceQuery\": true, \"tentativeResponse\": <The answer to the message of the user to the best of your ability. Note to keep the response under 500 characters.>}

Option 2: The User message does not have anything to do with anything regarding finances
Return: An object in the following format {\"validPromptResponse\": false, \"financequestion\": false,  \"tentativeResponse\": \"Question does not pertain to finances please ask another question.\"}

Option 3: The user is continuing a conversation regarding finances where the question did not relate to a prompt message but is a finance question.
Return: An object in the following format {\"validPromptResponse\": false, \"financequestion\": true, \"tentativeResponse\": <The answer to the message of the user to the best of your ability. Note to keep the response under 500 characters.>}

Option 4: The user is continuing a conversation regarding finances where the question did relate to a prompt message and is a finance question.
Return:  An object in the following format
{\"validPromptResponse\": true, \"financequestion\": true, \"monetaryBalanceQuery\": true, \"tentativeResponse\": <The answer to the message of the user to the best of your ability. Note to keep the response under 500 characters.>}

For any of the above returns make sure that they are returned in a JSON format.""",
  model="gpt-5-nano",
  output_type=FinancialReasoningSchema,
  model_settings=ModelSettings(
    store=True,
    reasoning=Reasoning(
      effort="medium",
      summary="auto"
    )
  )
)


class AgentContext:
  def __init__(self, state_tentativeresponse: str):
    self.state_tentativeresponse = state_tentativeresponse
def agent_instructions(run_context: RunContextWrapper[AgentContext], _agent: Agent[AgentContext]):
  state_tentativeresponse = run_context.context.state_tentativeresponse
  return f" {state_tentativeresponse}"
agent = Agent(
  name="Agent",
  instructions=agent_instructions,
  model="gpt-5",
  model_settings=ModelSettings(
    store=True,
    reasoning=Reasoning(
      effort="low",
      summary="auto"
    )
  )
)


class AgentContext1:
  def __init__(self, state_tentativeresponse: str):
    self.state_tentativeresponse = state_tentativeresponse
def agent_instructions1(run_context: RunContextWrapper[AgentContext1], _agent: Agent[AgentContext1]):
  state_tentativeresponse = run_context.context.state_tentativeresponse
  return f" {state_tentativeresponse}"
agent1 = Agent(
  name="Agent",
  instructions=agent_instructions1,
  model="gpt-5",
  model_settings=ModelSettings(
    store=True,
    reasoning=Reasoning(
      effort="low",
      summary="auto"
    )
  )
)


class WorkflowInput(BaseModel):
  input_as_text: str


# Main code entrypoint
async def run_workflow(workflow_input: WorkflowInput):
  with trace("Spendo Chatbot"):
    state = {
      "validpromptmessage": None,
      "isfinancequestion": None,
      "tentativeresponse": None
    }
    workflow = workflow_input.model_dump()
    conversation_history: list[TResponseInputItem] = [
      {
        "role": "user",
        "content": [
          {
            "type": "input_text",
            "text": workflow["input_as_text"]
          }
        ]
      }
    ]
    financial_reasoning_result_temp = await Runner.run(
      financial_reasoning,
      input=[
        *conversation_history
      ],
      run_config=RunConfig(trace_metadata={
        "__trace_source__": "agent-builder",
        "workflow_id": "wf_68ee92d551ac819096e06e9789e4accf05c17f1103e9f72d"
      })
    )

    conversation_history.extend([item.to_input_item() for item in financial_reasoning_result_temp.new_items])

    financial_reasoning_result = {
      "output_text": financial_reasoning_result_temp.final_output.json(),
      "output_parsed": financial_reasoning_result_temp.final_output.model_dump()
    }
    state["validpromptmessage"] = financial_reasoning_result["output_parsed"]["validpromptresponse"]
    state["isfinancequestion"] = financial_reasoning_result["output_parsed"]["financequestion"]
    state["tentativeresponse"] = financial_reasoning_result["output_parsed"]["tentativeresponse"]
    if financial_reasoning_result["output_parsed"]["financequestion"] == False:
      agent_result_temp = await Runner.run(
        agent,
        input=[
          *conversation_history
        ],
        run_config=RunConfig(trace_metadata={
          "__trace_source__": "agent-builder",
          "workflow_id": "wf_68ee92d551ac819096e06e9789e4accf05c17f1103e9f72d"
        }),
        context=AgentContext(state_tentativeresponse=state["tentativeresponse"])
      )

      conversation_history.extend([item.to_input_item() for item in agent_result_temp.new_items])

      agent_result = {
        "output_text": agent_result_temp.final_output_as(str)
      }
      end_result = {
        "tentativeresponse": state["tentativeresponse"],
        "isfinancequestion": state["isfinancequestion"]
      }
      return end_result
    elif financial_reasoning_result["output_parsed"]["financequestion"] == True:
      agent_result_temp = await Runner.run(
        agent1,
        input=[
          *conversation_history
        ],
        run_config=RunConfig(trace_metadata={
          "__trace_source__": "agent-builder",
          "workflow_id": "wf_68ee92d551ac819096e06e9789e4accf05c17f1103e9f72d"
        }),
        context=AgentContext1(state_tentativeresponse=state["tentativeresponse"])
      )

      conversation_history.extend([item.to_input_item() for item in agent_result_temp.new_items])

      agent_result = {
        "output_text": agent_result_temp.final_output_as(str)
      }
      end_result = {
        "tentativeresponseee": state["tentativeresponse"],
        "isfinancequestion": state["isfinancequestion"]
      }
      return end_result
    else:
      return financial_reasoning_result


# def analyze_user_message(message):
#     response = client.responses.create(
#         prompt={
#             "id": "pmpt_68c1c8c9b8908190add547c625d1be4004d1e9d14ef967a3",
#             "version": "9"
#         },
#         input=[
#             {
#                 "role": "user",
#                 "content": message  # your user message here
#             }
#         ]
#     )
    
#     if not response:
#         return "No response from openAI"
#     return response
    
    

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