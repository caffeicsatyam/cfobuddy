import os
from typing import Annotated, List, TypedDict
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_community.document_loaders import CSVLoader
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

from graphs.analytics_graph import ChatState, Analytic_node
# --------------------------------------------------
# ENV SETUP
# --------------------------------------------------
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

# --------------------------------------------------
# LOAD FINANCIAL DATA
# --------------------------------------------------
loader = CSVLoader("data/FinancialStatements.csv")
documents = loader.load()

# --------------------------------------------------
# MEMORY CHECKPOINTER
# --------------------------------------------------
checkpointer = InMemorySaver()

# --------------------------------------------------
# DEFINE STATE
# --------------------------------------------------
class ChatState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    financeSheet: object
    summary: str

# --------------------------------------------------
# CHAT NODE
# --------------------------------------------------
def Chat_node(state: ChatState):
    user_question = state["messages"][-1].content

    prompt = f"""You are a helpful assistant answering questions.
    You need to answer any question asked by the user and direct to the tools and subgraphs if needed.
    """



# --------------------------------------------------
# BUILD GRAPH
# --------------------------------------------------
graph = StateGraph(ChatState)

graph.add_node("chat_node", Chat_node)
graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", "analytic_node")
graph.add_edge("analytic_node", END)

chatbot = graph.compile(checkpointer=checkpointer)

# --------------------------------------------------
# RUN CHAT LOOP
# --------------------------------------------------
if __name__ == "__main__":

    print("\nCFOBuddy AI Ready\n")

    state = {
        "messages": [],
        "financeSheet": documents,
        "summary": "",
    }

    thread = "cfo-session"

    while True:
        user_input = input("\nYou: ")

        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye")
            break

        state["messages"].append(HumanMessage(content=user_input))

        result = chatbot.invoke(
            state,
            config={"configurable": {"thread_id": thread}},
        )

        AI = result["messages"][-1].content
        print("\nCFOBuddy:", AI)

        state = result

print(graph.visualize())