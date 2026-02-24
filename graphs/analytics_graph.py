import os
from typing import Annotated, List, TypedDict

from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver

from langchain_core.messages import BaseMessage, HumanMessage
from langchain_community.document_loaders import CSVLoader
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint


load_dotenv()
hf_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")

hf_model = "Qwen/Qwen2.5-7B-Instruct"

endpoint = HuggingFaceEndpoint(
    repo_id=hf_model,
    temperature=0.3,
    max_new_tokens=512,
    huggingfacehub_api_token=hf_token,
)

llm = ChatHuggingFace(llm=endpoint)


class AnalyticsState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    financeSheet: object
    response: str

#-------------------------------------------------
#  Chat Phase
#-------------------------------------------------

def Analytic_node(state: AnalyticsState):
    finance_data = state["financeSheet"]

    # limit context size
    context = "\n".join([doc.page_content for doc in finance_data[:20]])

    user_question = state["messages"][-1].content

    prompt = f"""
You are an expert CFO advisor.

Analyze the financial data and answer the question.

Provide:
• key insights
• profitability status
• cost observations
• financial risks
• actionable recommendations

FINANCIAL DATA:
{context}

QUESTION:
{user_question}
"""

    response = llm.invoke(prompt)

    return {
        "messages": state["messages"] + [response],
        "financeSheet": finance_data,
        "summary": response.content,
    }

