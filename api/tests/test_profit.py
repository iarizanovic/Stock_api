from main import app
from fastapi.testclient import TestClient
from fastapi import status

client = TestClient(app)


# Tests calculating the profit for a stock (AAPL) between two valid dates
def test_calculate_profit_valid_range():
    request_data = {
      "ticker": "AAPL",
      "start_date": "12/08/2000",
      "end_date": "12/18/2000"
    }
    response = client.post('/profit/', json=request_data)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
      "main_period": {
        "buy_date": "2000-12-08",
        "sell_date": "2000-12-12",
        "buy_close": 0.268973,
        "sell_close": 0.274554,
        "profit": 0.005581000000000003,
        "max_multi_trade_profit": 0.00892900000000002,
        "stocks_with_better_profit": "Amazon, "
      },
      "pre_period": {
        "buy_date": "2000-11-30",
        "sell_date": "2000-12-01",
        "buy_close": 0.294643,
        "sell_close": 0.304688,
        "profit": 0.010045000000000026,
        "max_multi_trade_profit": 0.015625,
        "stocks_with_better_profit": "Amazon, "
      },
      "post_period": {
        "buy_date": "2000-12-19",
        "sell_date": "2000-12-22",
        "buy_close": 0.25,
        "sell_close": 0.267857,
        "profit": 0.017857000000000012,
        "max_multi_trade_profit": 0.025668999999999997,
        "stocks_with_better_profit": "Amazon, "
      }
    }


# Tests calculating profit with a very old start date and a valid end date
def test_calculate_profit_old_start_date():
    request_data = {
      "ticker": "AAPL",
      "start_date": "12/08/1000",
      "end_date": "12/18/2000"
    }
    response = client.post('/profit/', json=request_data)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
      "main_period": {
        "buy_date": "1982-07-08",
        "sell_date": "2000-03-22",
        "buy_close": 0.049107,
        "sell_close": 1.287388,
        "profit": 1.238281,
        "max_multi_trade_profit": 18.659168999999984,
        "stocks_with_better_profit": "Amazon, "
      },
      "pre_period": {
        "detail": "No price data available for the given range"
      },
      "post_period": {
        "buy_date": "2003-04-17",
        "sell_date": "2020-09-01",
        "buy_close": 0.234286,
        "sell_close": 134.179993,
        "profit": 133.945707,
        "max_multi_trade_profit": 653.4094630000001,
        "stocks_with_better_profit": ""
      }
    }


# Tests handling reversed start and end dates, which lead to invalid data
def test_calculate_profit_reversed_dates():
    request_data = {
      "ticker": "AAPL",
      "start_date": "12/08/2000",
      "end_date": "12/18/1000"
    }
    response = client.post('/profit/', json=request_data)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
      "main_period": {
        "detail": "No price data available for the given range"
      },
      "pre_period": {
        "detail": "No price data available for the given range"
      },
      "post_period": {
        "detail": "No price data available for the given range"
      }
    }


# Tests handling incorrect date format when calculating profit for a stock
def test_calculate_profit_invalid_date_format():
    request_data = {
      "ticker": "AAPL",
      "start_date": "12/08/2000",
      "end_date": "12/181000"
    }
    response = client.post('/profit/', json=request_data)
    assert response.status_code == status.HTTP_406_NOT_ACCEPTABLE
    assert response.json() == {
      "detail": "Date has wrong format"
    }
