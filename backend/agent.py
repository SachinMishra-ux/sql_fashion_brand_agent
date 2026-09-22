"""
agent.py
Pure ReAct agent logic for the fashion brand catalog assistant (STELLA).
Assembles tools, prompt, LLM, and persistence checkpointer using create_agent.
"""
import json
import logging
from dotenv import load_dotenv

from langchain.agents import create_agent
from langchain_core.tools import tool

import llm as llm_module
import mysql_db
import supabase

load_dotenv(override=True)

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────
# Tools
# ──────────────────────────────────────────────────────────────

@tool
def execute_sql_query(query: str) -> str:
    """
    Executes a MySQL SELECT query against the fashion brand database.
    Returns JSON-serialisable results.
    If the query fails, returns the error message so you can correct and retry.
    Only use SELECT statements. Never INSERT, UPDATE, DELETE or DROP.
    """
    try:
        results = mysql_db.run_query(query)
        if not results:
            return "Query returned no rows."
        return json.dumps(results, default=str)
    except Exception as e:
        return f"SQL Error: {str(e)}\nPlease fix your SQL and try again."


@tool
def get_database_schema() -> str:
    """
    Returns the full CREATE TABLE SQL for every table in the fashion brand database.
    Call this whenever you are unsure about column names or table structure.
    """
    try:
        return mysql_db.get_schema()
    except Exception as e:
        return f"Error fetching schema: {str(e)}"


# ──────────────────────────────────────────────────────────────
# System Prompt
# ──────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are STELLA, the AI personal stylist and catalog assistant for a premium fashion brand.

You have access to the following MySQL database tables:
- users         : customer profiles with loyalty tiers (Bronze/Silver/Gold/Platinum)
- products      : fashion items with name, brand, category, price, discount, stock, image_url, description
- catalogs      : seasonal collections (Spring/Summer/Autumn/Winter)
- catalog_products : which products belong to which catalog
- orders        : customer purchase history

Your responsibilities:
1. Answer any fashion-related question by querying the database with `execute_sql_query`.
2. If you are unsure about column names, call `get_database_schema` first.
3. If you get a SQL Error, analyze it, fix the query, and retry automatically.
4. When the user asks about products, ALWAYS include relevant results in a structured format.
5. When listing products, always include: id, name, brand, category, price, discount_pct, image_url, description, color, size_range.
6. For questions about catalogs, join catalog_products with products to show items.
7. Be warm, stylish, and enthusiastic — you are a fashion expert!

CRITICAL OUTPUT FORMAT for product queries:
When your final answer contains products, format it EXACTLY like this JSON structure in your response:
{
  "type": "products",
  "message": "Your conversational reply here",
  "products": [
    { "id": 1, "name": "...", "brand": "...", "category": "...", "price": 0.00, "discount_pct": 0, "image_url": "...", "description": "...", "color": "...", "size_range": "..." }
  ]
}

For non-product answers (stats, user info, order history etc), format as:
{
  "type": "text",
  "message": "Your conversational reply here"
}
"""


# ──────────────────────────────────────────────────────────────
# Build Agent with create_agent
# ──────────────────────────────────────────────────────────────

def build_agent(checkpointer=None):
    """
    Assembles the ReAct agent using create_agent, passing SQL tools,
    system prompt, LLM from llm.py, and state checkpointer from supabase.py.
    """
    tools = [execute_sql_query, get_database_schema]
    model = llm_module.get_llm()

    if checkpointer is None:
        checkpointer = supabase.get_checkpointer()

    agent = create_agent(
        model=model,
        tools=tools,
        system_prompt=SYSTEM_PROMPT,
        checkpointer=checkpointer,
    )
    return agent


# Singleton agent instance
_agent = None


def get_agent():
    global _agent
    if _agent is None:
        _agent = build_agent()
    return _agent


def chat(message: str, session_id: str = "default") -> dict:
    """
    Sends a message to the ReAct agent and returns a parsed response dict.
    Returned dict always has: type, message, and optionally products[].
    Uses session_id for multi-turn state persistence.
    """
    agent = get_agent()
    config = {"configurable": {"thread_id": session_id}}
    result = agent.invoke({"messages": [("user", message)]}, config=config)
    final_msg = result["messages"][-1].content

    # Try to parse as JSON (structured product/text response)
    try:
        # Handle cases where the LLM wraps JSON in markdown code fences
        cleaned = final_msg.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            cleaned = "\n".join(lines[1:-1])
        parsed = json.loads(cleaned)
        return parsed
    except (json.JSONDecodeError, ValueError):
        # Fallback: plain text response
        return {"type": "text", "message": final_msg}
