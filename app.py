import os
from dotenv import load_dotenv

from langchain_core.messages import HumanMessage
from langchain_community.document_loaders import CSVLoader

from router import router  

# --------------------------------------------------
# ENV SETUP
# --------------------------------------------------
load_dotenv()

# --------------------------------------------------
# LOAD FINANCIAL DATA
# --------------------------------------------------
print("Loading financial data...")
loader = CSVLoader("data/FinancialStatements.csv")
documents = loader.load()
print(f"Loaded {len(documents)} financial records")

# --------------------------------------------------
# INITIAL STATE
# --------------------------------------------------
state = {
    "messages": [],
    "financeSheet": documents,
    "summary": "",
    "next": "",
}

thread_id = "cfo-session"   # memory session id

# --------------------------------------------------
# CLI LOOP
# --------------------------------------------------
print("\n CFOBuddy AI Ready")
print("Type 'exit' to quit\n")

while True:
    user_input = input("You: ")

    if user_input.lower() in ["exit", "quit"]:
        print("Goodbye")
        break

    # add user message
    state["messages"].append(HumanMessage(content=user_input))

    # invoke router graph
    result = router.invoke(
        state,
        config={"configurable": {"thread_id": thread_id}},
    )

    ai_reply = result["messages"][-1].content

    print("\nCFOBuddy:", ai_reply)

    # update state
    state = result

print(router.get_graph().draw_ascii())