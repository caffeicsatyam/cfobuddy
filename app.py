
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from core.graph import CFOBuddy  
from core.memory import retrieve_all_threads  
import uuid
from cfobuddy_logging import configure_logging
from langchain_core.messages.utils import trim_messages, count_tokens_approximately

load_dotenv()
logger = configure_logging()

# ==========================
# RESPONSE PARSER
# ==========================


# ===========================
# MAX TOKENS
# ============================
MAX_TOKENS = 150

def parse_response(content):
    if isinstance(content, list):
        text_parts = []
        for block in content:
            if isinstance(block, str):
                text_parts.append(block)
            elif isinstance(block, dict):
                text = block.get("text") or block.get("content") or ""
                if text:
                    text_parts.append(text)
        return "\n".join(text_parts) or str(content)
    return str(content)

# ==========================
# CHAT LOOP
# ==========================

print("=" * 50)
print("  CFO Buddy — Ready!")
print("  Type 'exit' or 'stop' to quit.")
print("  Type 'threads' to see past conversations.")
print("=" * 50 + "\n")


thread_id = str(uuid.uuid4())
config = {"configurable": {"thread_id": thread_id}, "recursion_limit": 25}
print(f"Session ID: {thread_id}\n")

while True:

    user_input = input("You: ").strip()

    if user_input.lower() in ["quit", "exit", "stop", "bye", "q"]:
        print("Goodbye!")
        break

    if user_input.lower() == "threads":
        threads = retrieve_all_threads()
        print("\nExisting threads:", threads, "\n")
        continue

    if not user_input:
        continue

    try:
        response = CFOBuddy.invoke(
            {"messages": [HumanMessage(content=user_input)]},
            config=config
        )
        content = parse_response(response["messages"][-1].content)
        print("\nCFO Buddy:", content, "\n")

    except Exception as e:
        logger.exception("Unhandled error in CLI chat loop")
        print("\nError:", e, "\n")