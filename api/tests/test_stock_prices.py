from main import app
from fastapi.testclient import TestClient
from fastapi import status

client = TestClient(app)


# Test case to create stock price data for a specific stock (AAPL) on a given date.
def test_create_stock_prices():
    request_data = {
      "date": "2023-01-01",
      "open": 145.3,
      "high": 147,
      "low": 144.5,
      "close": 146.2,
      "adj_close": 146,
      "volume": 1234567
    }
    response = client.post('/prices/AAPL', json=request_data)
    assert response.status_code == status.HTTP_201_CREATED


# Test case to attempt creating stock price data for a specific stock (AAPL) on a date that already exists.
def test_create_stock_prices2():
    request_data = {
      "date": "2023-01-01",
      "open": 145.3,
      "high": 147,
      "low": 144.5,
      "close": 146.2,
      "adj_close": 146,
      "volume": 1234567
    }
    response = client.post('/prices/AAPL', json=request_data)
    assert response.status_code == status.HTTP_406_NOT_ACCEPTABLE
    assert response.json() == {
      "detail": "Date already exists"
    }


# Test case to retrieve the stock price for a given stock (AAPL) on a specific date (2000-07-24).
def test_get_stock_prices():
    response = client.get("/prices/AAPL/07/24/2000")
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert response_json["date"] == "2000-07-24"
    assert response_json["open"] == 0.938616
    assert response_json["high"] == 0.944196
    assert response_json["low"] == 0.848214
    assert response_json["close"] == 0.86942
    assert response_json["adj_close"] == 0.7513
    assert response_json["volume"] == 412171200
    assert response_json["stock_id"] == 2


# Test case to retrieve the stock price for a given stock (AAPL) with wrong date format.
def test_get_stock_prices_wrong_time():
    response = client.get("/prices/AAPL/07/24/20#00")
    assert response.status_code == status.HTTP_406_NOT_ACCEPTABLE
    assert response.json() == {
  "detail": "Date has wrong format"
}


# Test case to update the stock price data for a specific stock (AAPL) on a given date.
def test_update_stock_prices():
    request_data = {
      "date": "2023-01-01",
      "open": 145.3,
      "high": 147,
      "low": 144.5,
      "close": 146.2,
      "adj_close": 146,
      "volume": 1
    }
    response = client.put("/prices/AAPL/01/01/2023", json=request_data)
    assert response.status_code == status.HTTP_202_ACCEPTED


# Test case to delete the stock price data for a specific stock (AAPL) on a given date.
def test_delete_stock_prices():
    response = client.delete("/prices/AAPL/01/01/2023")
    assert response.status_code == status.HTTP_202_ACCEPTED
