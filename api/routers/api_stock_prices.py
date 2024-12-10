from datetime import datetime
from fastapi import Depends, APIRouter, status, HTTPException, Path, Body
from typing import List
from database import get_db, Stock, StockPrice
from sqlalchemy.orm import Session
from schemas import StockPriceCreate, StockPriceResponse

router = APIRouter(
    prefix="/prices",
    tags=["Stock Prices"],
    responses={404: {"description": "Not found"}}
)


# Get all Prices for one Stock
@router.get("/{ticker}", response_model=List[StockPriceResponse], status_code=status.HTTP_200_OK)
def get_all_stock_prices(ticker: str = Path(..., example="AAPL"),
                         db: Session = Depends(get_db)):
    # Find Stock
    stock = db.query(Stock).filter(Stock.ticker == ticker).first()
    if not stock:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stock not found")

    # Get prices for specified Stock
    return stock.prices


# Add Stock Prices
@router.post("/{ticker}", status_code=status.HTTP_201_CREATED)
def add_stock_price(ticker: str = Path(..., example="AAPL"),
                    price: StockPriceCreate = Body(...),
                    db: Session = Depends(get_db)):
    # Check if stock exists
    stock = db.query(Stock).filter(Stock.ticker == ticker).first()
    if not stock:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stock not found")

    # Check if date already exists
    stock_price = (
        db.query(StockPrice)
        .filter(StockPrice.stock_id == stock.id)
        .filter(StockPrice.date == price.date)
        .first()
    )
    if stock_price:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Date already exists")

    # Add Stock Price
    db_price = StockPrice(
        stock_id=stock.id,
        date=price.date,
        open=price.open,
        high=price.high,
        low=price.low,
        close=price.close,
        adj_close=price.adj_close,
        volume=price.volume
    )
    db.add(db_price)
    db.commit()


# Get Stock Price
@router.get("/{ticker}/{month}/{day}/{year}", response_model=StockPriceResponse, status_code=status.HTTP_200_OK)
def get_stock_price(ticker: str = Path(..., example="AAPL"),
                    month: str = Path(..., example="7"),
                    day: str = Path(..., example="24"),
                    year: str = Path(..., example="2000"),
                    db: Session = Depends(get_db)):
    # Parse the date
    try:
        parsed_date = datetime.strptime(f"{month}/{day}/{year}", "%m/%d/%Y").date()
    except:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Date has wrong format")

    # Find Stock Price
    stock_price = (
        db.query(StockPrice)
        .join(Stock, Stock.id == StockPrice.stock_id)
        .filter(Stock.ticker == ticker)
        .filter(StockPrice.date == parsed_date)
        .first()
    )

    # Check if stock and price exist on specified date
    if not stock_price:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stock or date not found")

    # Get price for specified Stock
    return stock_price


# Update Stock data
@router.put("/{ticker}/{month}/{day}/{year}", status_code=status.HTTP_202_ACCEPTED)
def update_stock_price(ticker: str = Path(..., example="AAPL"),
                       month: str = Path(..., example="6"),
                       day: str = Path(..., example="24"),
                       year: str = Path(..., example="2000"),
                       stock_price_updated: StockPriceCreate = Body(...),
                       db: Session = Depends(get_db)):
    # Find Stock
    stock = db.query(Stock).filter(Stock.ticker == ticker).first()
    if not stock:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stock not found")

    # Parse the date
    try:
        parsed_date = datetime.strptime(f"{month}/{day}/{year}", "%m/%d/%Y").date()
    except:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Date has wrong format")

    # Check if price exists on specified date
    stock_price = (
        db.query(StockPrice)
        .filter(StockPrice.stock_id == stock.id)
        .filter(StockPrice.date == parsed_date)
        .first()
    )
    if not stock_price:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Date not found")

    # Check if new date already exists
    if (stock_price.date != stock_price_updated.date and
        db.query(StockPrice).filter(StockPrice.stock_id == stock.id)
                .filter(StockPrice.date == stock_price_updated.date).first()):
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="New date already exists")

    # Update the stock price
    stock_price.date = stock_price_updated.date
    stock_price.open = stock_price_updated.open
    stock_price.high = stock_price_updated.high
    stock_price.low = stock_price_updated.low
    stock_price.close = stock_price_updated.close
    stock_price.adj_close = stock_price_updated.adj_close
    stock_price.volume = stock_price_updated.volume

    # Commit the changes
    db.add(stock_price)
    db.commit()


# Delete Stock data
@router.delete("/{ticker}/{month}/{day}/{year}", status_code=status.HTTP_202_ACCEPTED)
def delete_stock_price(ticker: str = Path(..., example="AAPL"),
                       month: str = Path(..., example="6"),
                       day: str = Path(..., example="24"),
                       year: str = Path(..., example="2000"),
                       db: Session = Depends(get_db)):
    # Find Stock
    stock = db.query(Stock).filter(Stock.ticker == ticker).first()
    if not stock:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stock not found")

    # Parse the date
    try:
        parsed_date = datetime.strptime(f"{month}/{day}/{year}", "%m/%d/%Y").date()
    except:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Date has wrong format")

    # Check if price exists on specified date
    stock_price = (
        db.query(StockPrice)
        .filter(StockPrice.stock_id == stock.id)
        .filter(StockPrice.date == parsed_date)
        .first()
    )
    if not stock_price:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Date not found")

    # Delete Stock price
    db.query(StockPrice).filter(StockPrice.stock_id == stock.id).filter(StockPrice.date == parsed_date).delete()
    db.commit()

