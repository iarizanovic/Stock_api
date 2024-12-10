from datetime import datetime, timedelta, date
from typing import List, Dict
from fastapi import Depends, APIRouter, status, HTTPException, Path, Body
from database import get_db, Stock, StockPrice
from sqlalchemy.orm import Session
from schemas import ProfitInput


router = APIRouter(
    prefix="/profit",
    tags=["Profit"],
    responses={404: {"description": "Not found"}}
)


def calc_profit_multi_tread(prices: List[StockPrice]) -> float:
    """
    Calculate the maximum profit using a multi-trade strategy.

    This function calculates the maximum profit that can be obtained by performing multiple
    trades, where a stock is bought when its price is expected to rise, and sold when its price
    decreases. It iterates through the prices and calculates the total profit from all successful trades.

    :param prices: A list of stock price objects for a given period.
    :return: The maximum multi-trade profit.
    """
    max_multi_trade_profit: float = 0
    bought_price: float = 0
    for i in range(len(prices) - 1):
        if prices[i].close == prices[i + 1].close:
            continue

        # Buy
        if bought_price == 0:
            if prices[i].close < prices[i + 1].close:
                bought_price = prices[i].close
        # Sell
        elif prices[i].close > prices[i + 1].close:
            max_multi_trade_profit += float(prices[i].close) - bought_price
            bought_price = 0
    # Sell last day
    if bought_price != 0 and bought_price < prices[-1].close:
        max_multi_trade_profit += prices[-1].close - bought_price

    return max_multi_trade_profit


def calc_profit(prices: List[StockPrice]) -> Dict:
    """
    Calculate the profit from a series of stock prices using both single and multi-trade strategies.

    This function calculates the profit for both single trade (buy once, sell once) and multi-trade
    strategies (buy and sell multiple times) for the given list of stock prices.

    :param prices: A list of StockPrice objects sorted by date.
    :return: A dictionary with profit details for a single trade and multi-trade profit.
    """
    # Check if there is no prices for the given range
    if not prices:
        return {"detail": "No price data available for the given range"}

    result = {
        "buy_date": prices[0].date,
        "sell_date": prices[0].date,
        "buy_close": float('inf'),
        "sell_close": .0,
        "profit": .0,
        "max_multi_trade_profit": .0,
        "stocks_with_better_profit": ""
    }

    # Calculate profit with single trade
    counter: int = 0
    for price_buy in prices[:-1]:
        counter += 1
        if price_buy.close < result["buy_close"]:
            # Find max profit
            for price_sell in prices[counter:]:
                new_profit = price_sell.close - price_buy.close
                if new_profit > result["profit"]:
                    # Save if new profit is better
                    result["buy_date"] = price_buy.date
                    result["sell_date"] = price_sell.date
                    result["buy_close"] = price_buy.close
                    result["sell_close"] = price_sell.close
                    result["profit"] = new_profit

    # Calculate profit with multi trade
    result["max_multi_trade_profit"] = calc_profit_multi_tread(prices)

    return result


def get_profit_result(stock_id: int, start_date: date, end_date: date,
                      db: Session, multi_trade_only: bool = False) -> Dict[str, Dict]:
    """
    Fetch prices for the main, pre, and post periods, and calculate the profit for each period.

    The function retrieves stock prices for three periods: main, pre, and post. It
    calculates both single trade and multi-trade profits for each period and returns
    the results.

    :param stock_id: The ID of the stock.
    :param start_date: The start date for the profit calculation.
    :param end_date: The end date for the profit calculation.
    :param db: The database session used to query stock prices.
    :param multi_trade_only: If True, only returns multi-trade profits. Default is False.
    :return: A dictionary with profit results for the main, pre, and post periods.
    """
    # Get the prices for the Main Period
    prices = db.query(StockPrice).filter(
        StockPrice.stock_id == stock_id,
        StockPrice.date >= start_date,
        StockPrice.date <= end_date
    ).order_by(StockPrice.date).all()

    # Get the prices for the Pre Period
    delta_days = len(prices)
    prices_pre = db.query(StockPrice).filter(
        StockPrice.stock_id == stock_id,
        StockPrice.date <= start_date - timedelta(days=1)
    ).order_by(StockPrice.date.desc()).limit(delta_days).all()
    prices_pre = sorted(prices_pre, key=lambda x: x.date)

    # Get the prices for the Post Period
    prices_post = db.query(StockPrice).filter(
        StockPrice.stock_id == stock_id,
        StockPrice.date >= end_date + timedelta(days=1),
    ).order_by(StockPrice.date).limit(delta_days).all()

    if not multi_trade_only:
        return {
            "main_period": calc_profit(prices),
            "pre_period": calc_profit(prices_pre),
            "post_period": calc_profit(prices_post)
        }
    else:
        return {
            "main_period": {"max_multi_trade_profit": calc_profit_multi_tread(prices)},
            "pre_period": {"max_multi_trade_profit": calc_profit_multi_tread(prices_pre)},
            "post_period": {"max_multi_trade_profit": calc_profit_multi_tread(prices_post)}
        }


@router.post("/", status_code=status.HTTP_200_OK)
def calculate_profit(profit_input: ProfitInput = Body(...),
                     db: Session = Depends(get_db)):
    stock = db.query(Stock).filter(Stock.ticker == profit_input.ticker).first()
    if not stock:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stock not found")

    # Parse the start and end date
    try:
        start_date = datetime.strptime(profit_input.start_date, "%m/%d/%Y").date()
        end_date = datetime.strptime(profit_input.end_date, "%m/%d/%Y").date()
    except:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Date has wrong format")

    # Get the results of specified stock
    result = get_profit_result(stock.id, start_date, end_date, db)

    # Get the stocks with better profit in same periods
    all_other_stocks = db.query(Stock).filter(Stock.ticker != profit_input.ticker).all()
    for other_stock in all_other_stocks:
        other_res = get_profit_result(other_stock.id, start_date, end_date, db, True)
        for period in ['main_period', 'pre_period', 'post_period']:
            if (result[period].get("max_multi_trade_profit") and
                    result[period]["max_multi_trade_profit"] < other_res[period]["max_multi_trade_profit"]):
                result[period]["stocks_with_better_profit"] += other_stock.name + ", "

    return result
