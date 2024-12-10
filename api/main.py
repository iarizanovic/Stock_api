from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from routers import api_stocks, api_stock_prices, api_profit
from database import init_db

app = FastAPI()


# Init the DB
@app.on_event("startup")
async def startup_event():
    init_db()


# Redirect root path to /docs
@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse(url="/docs")


# Routers
app.include_router(api_stocks.router)
app.include_router(api_stock_prices.router)
app.include_router(api_profit.router)
