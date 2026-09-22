"""
main.py
FastAPI backend server for the Fashion Brand SQL ReAct Agent.
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

import mysql_db
import supabase
import agent as ag

app = FastAPI(
    title="Fashion Brand AI API",
    description="Natural-language SQL ReAct agent for the fashion catalog",
    version="1.0.0",
)

# Allow the frontend (served on any origin during development) to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ──────────────────────────────────────────────────────────────
# Request / Response schemas
# ──────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"


class ChatResponse(BaseModel):
    type: str                          # "text" | "products"
    message: str
    products: list[dict] = []


class ProductListResponse(BaseModel):
    products: list[dict]


# ──────────────────────────────────────────────────────────────
# Routes
# ──────────────────────────────────────────────────────────────

@app.get("/health/mysql")
def health_mysql():
    """Health check endpoint specifically for the MySQL database."""
    try:
        mysql_db.check_connection()
        return {"status": "ok", "service": "mysql"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"MySQL unreachable: {e}")


@app.get("/health/supabase")
def health_supabase():
    """Health check endpoint specifically for Supabase / PostgreSQL."""
    try:
        supabase.check_postgres_connection()
        return {"status": "ok", "service": "supabase"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Supabase unreachable: {e}")


@app.get("/health")
def health():
    """
    Unified health check verifying both MySQL and Supabase connectivity.
    Returns individual statuses and an overall status.
    """
    mysql_status = {"status": "ok"}
    try:
        mysql_db.check_connection()
    except Exception as e:
        mysql_status = {"status": "error", "error": str(e)}

    supabase_status = {"status": "ok"}
    try:
        supabase.check_postgres_connection()
    except Exception as e:
        supabase_status = {"status": "error", "error": str(e)}

    all_healthy = mysql_status["status"] == "ok" and supabase_status["status"] == "ok"
    response_content = {
        "status": "ok" if all_healthy else "degraded",
        "mysql": mysql_status,
        "supabase": supabase_status,
    }
    return JSONResponse(
        status_code=200 if all_healthy else 503,
        content=response_content,
    )


@app.get("/products", response_model=ProductListResponse)
def list_products(
    category: str | None = None,
    max_price: float | None = None,
    season: str | None = None,
):
    """
    Returns products with optional filters:
    - category: e.g. Dresses, Bags, Footwear
    - max_price: upper price bound
    - season: catalog season name (Spring, Summer, Autumn, Winter)
    """
    try:
        sql = """
            SELECT DISTINCT
                p.id, p.name, p.brand, p.category, p.subcategory,
                p.price, p.discount_pct, p.stock,
                p.color, p.size_range, p.image_url, p.description
            FROM products p
        """
        conditions = []
        if season:
            sql += " JOIN catalog_products cp ON p.id = cp.product_id JOIN catalogs c ON cp.catalog_id = c.id"
            conditions.append(f"c.season = '{season}'")
        if category:
            conditions.append(f"p.category = '{category}'")
        if max_price is not None:
            conditions.append(f"p.price <= {max_price}")
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        sql += " ORDER BY p.id"

        products = mysql_db.run_query(sql)
        return {"products": products}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/catalogs")
def list_catalogs():
    """Returns all seasonal catalogs."""
    try:
        catalogs = mysql_db.run_query("SELECT * FROM catalogs ORDER BY year DESC, id")
        return {"catalogs": catalogs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/categories")
def list_categories():
    """Returns distinct product categories."""
    try:
        rows = mysql_db.run_query("SELECT DISTINCT category FROM products ORDER BY category")
        return {"categories": [r["category"] for r in rows]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    """
    Main chat endpoint. Sends the user's message to the LangGraph
    ReAct agent and returns a structured response.
    """
    try:
        result = ag.chat(req.message, session_id=req.session_id)
        return ChatResponse(
            type=result.get("type", "text"),
            message=result.get("message", ""),
            products=result.get("products", []),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ──────────────────────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
