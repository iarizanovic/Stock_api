from fastapi import Depends, APIRouter, status, HTTPException, Body, Path
from typing import List
from database import get_db, Stock, StockPrice
from sqlalchemy.orm import Session
from schemas import StockCreate, StockResponse

router = APIRouter(
    prefix="/stocks",
    tags=["Stocks"],
    responses={404: {"description": "Not found"}}
)


# Get all Stocks
@router.get("/", response_model=List[StockResponse], status_code=status.HTTP_200_OK)
def get_all_stocks(db: Session = Depends(get_db)):
    return db.query(Stock).all()


# Create new Stock
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_stock(stock: StockCreate = Body(...),
                 db: Session = Depends(get_db)):
    # Add the Stock
    db_stock = Stock(
        name=stock.name,
        ticker=stock.ticker,
        inception_date=stock.inception_date
    )
    db.add(db_stock)

    # Commit the changes
    try:
        db.commit()
    except:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail='Stock already exists')


# Get Stock data
@router.get("/{ticker}", response_model=StockResponse, status_code=status.HTTP_200_OK)
def get_stock(ticker: str = Path(..., example="AAPL"),
              db: Session = Depends(get_db)):
    # Find Stock
    stock = db.query(Stock).filter(Stock.ticker == ticker).first()
    if not stock:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stock not found")

    return stock


# Update Stock data
@router.put("/{ticker}", status_code=status.HTTP_202_ACCEPTED)
def update_stock(ticker: str = Path(..., example="AAPL"),
                 stock_updated: StockCreate = Body(...),
                 db: Session = Depends(get_db)):
    # Find Stock
    stock = db.query(Stock).filter(Stock.ticker == ticker).first()
    if not stock:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stock not found")

    # Check if new ticker already exists
    if stock.ticker != stock_updated.ticker and db.query(Stock).filter(Stock.ticker == stock_updated.ticker).first():
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="New ticker already exists")

    # Update the stock
    stock.name = stock_updated.name
    stock.ticker = stock_updated.ticker
    stock.inception_date = stock_updated.inception_date

    # Commit the changes
    db.add(stock)
    db.commit()


# Delete Stock data
@router.delete("/{ticker}", status_code=status.HTTP_202_ACCEPTED)
def delete_stock(ticker: str = Path(..., example="AAPL"),
                 db: Session = Depends(get_db)):
    # Find Stock
    stock = db.query(Stock).filter(Stock.ticker == ticker).first()
    if not stock:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stock not found")

    # Delete Stock and stock prices
    db.query(StockPrice).filter(StockPrice.stock_id == stock.id).delete()
    db.query(Stock).filter(Stock.ticker == ticker).delete()
    db.commit()
