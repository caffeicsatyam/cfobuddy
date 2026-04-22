import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()


# FEEELING LIKE A FREELOADER :)


# HuggingFaceEndpoint from LANGCHAIN 
# model = HuggingFaceEndpoint(
#     repo_id="google/gemma-3-27b-it",
#     task="text-generation",
#     max_new_tokens=512,
#     temperature=0.1,
#     huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN"),
# )
# llm = ChatHuggingFace(llm=model)


# CHATNVIDIA FROM  NVIDIA NMI VIA LANGCHAIN
# llm = ChatNVIDIA(
#   model="meta/llama-3.3-70b-instruct",
#   api_key=os.getenv("NVIDIA_API_KEY"), 
#   temperature=0.1,
#   top_p=0.7,
#   max_tokens=1024,
# )


# Chat Groq from LANGCHAIN
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.2,
)

