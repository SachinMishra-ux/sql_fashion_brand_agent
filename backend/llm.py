"""
llm.py
Initializes and returns the SenseNova LLM model via LangChain's ChatOpenAI.
"""
import os
from dotenv import load_dotenv
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI

load_dotenv(override=True)


def get_llm() -> BaseChatModel:
    """
    Initialize and return the SenseNova ChatModel.
    """
    sensenova_api_key = os.getenv("SENSENOVA_API_KEY")
    if not sensenova_api_key:
        raise ValueError("SENSENOVA_API_KEY is not set in environment.")

    model = os.getenv("SENSENOVA_MODEL", "sensenova-6.8-flash-lite")
    return ChatOpenAI(
        base_url="https://token.sensenova.ai/v1",
        api_key=sensenova_api_key,
        model=model,
        temperature=0,
    )