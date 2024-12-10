from pydantic import BaseModel
from datetime import date


class StockCreate(BaseModel):
    name: str
    ticker: str
    inception_date: date

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "name": "Apple",
                "ticker": "AAPL",
                "inception_date": "1976-04-01"
            }
        }


class StockResponse(StockCreate):
    id: int


class StockPriceCreate(BaseModel):
    date: date
    open: float
    high: float
    low: float
    close: float
    adj_close: float
    volume: int

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "date": "2023-01-01",
                "open": 145.3,
                "high": 147.0,
                "low": 144.5,
                "close": 146.2,
                "adj_close": 146.0,
                "volume": 1234567
            }
        }


class StockPriceResponse(StockPriceCreate):
    id: int
    stock_id: int


class ProfitInput(BaseModel):
    ticker: str
    start_date: str
    end_date: str

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "ticker": "AAPL",
                "start_date": "12/08/2000",
                "end_date": "12/18/2000"
            }
        }
