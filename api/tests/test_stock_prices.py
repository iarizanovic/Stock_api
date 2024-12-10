from main import app
from fastapi.testclient import TestClient
from fastapi import status

client = TestClient(app)


# Tests successful creation of stock price data for a specific date
def test_create_stock_price_success():
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


# Tests attempting to create stock price data for a non-existent stock
def test_create_stock_price_stock_not_found():
    request_data = {
      "date": "2023-01-01",
      "open": 145.3,
      "high": 147,
      "low": 144.5,
      "close": 146.2,
      "adj_close": 146,
      "volume": 1234567
    }
    response = client.post('/prices/AAPL65', json=request_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
      "detail": "Stock not found"
    }


# Tests attempting to create stock price data for a date that already exists
def test_create_stock_price_date_already_exists():
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


# Tests retrieving stock price data for a specific date
def test_get_stock_price_by_date():
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


# Tests returning an error when the date format is invalid
def test_get_stock_price_invalid_date_format():
    response = client.get("/prices/AAPL/07/24/20#00")
    assert response.status_code == status.HTTP_406_NOT_ACCEPTABLE
    assert response.json() == {
      "detail": "Date has wrong format"
    }


# Tests returning an error when the stock or date is not found
def test_get_stock_price_stock_or_date_not_found():
    response = client.get("/prices/AAPL65/07/24/2000")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
      "detail": "Stock or date not found"
    }


# Tests successful update of stock price data for a specific date
def test_update_stock_price_success():
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


# Tests attempting to update stock price data for a non-existent stock
def test_update_stock_price_stock_not_found():
    request_data = {
      "date": "2023-01-01",
      "open": 145.3,
      "high": 147,
      "low": 144.5,
      "close": 146.2,
      "adj_close": 146,
      "volume": 1
    }
    response = client.put("/prices/AAPL65/07/24/2000", json=request_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
      "detail": "Stock not found"
    }


# Tests returning an error when trying to update stock price data with an invalid date format
def test_update_stock_price_invalid_date_format():
    request_data = {
      "date": "2023-01-01",
      "open": 145.3,
      "high": 147,
      "low": 144.5,
      "close": 146.2,
      "adj_close": 146,
      "volume": 1
    }
    response = client.put("/prices/AAPL/07/24/20#00", json=request_data)
    assert response.status_code == status.HTTP_406_NOT_ACCEPTABLE
    assert response.json() == {
      "detail": "Date has wrong format"
    }



# Tests attempting to update stock price data for a date that already exists
def test_update_stock_price_date_already_exists():
    request_data = {
      "date": "2000-01-03",
      "open": 145.3,
      "high": 147,
      "low": 144.5,
      "close": 146.2,
      "adj_close": 146,
      "volume": 1
    }
    response = client.put("/prices/AAPL/01/01/2023", json=request_data)
    assert response.status_code == status.HTTP_406_NOT_ACCEPTABLE
    assert response.json() == {
      "detail": "New date already exists"
    }


# Tests successfully deleting stock price data for a specific date
def test_delete_stock_price_success():
    response = client.delete("/prices/AAPL/01/01/2023")
    assert response.status_code == status.HTTP_202_ACCEPTED


# Tests attempting to delete stock price data for a non-existent stock
def test_delete_stock_price_stock_not_found():
    response = client.delete("/prices/AAPL65/01/01/2023")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
      "detail": "Stock not found"
    }


# Tests returning an error when trying to delete stock price data with an invalid date format
def test_delete_stock_price_invalid_date_format():
    response = client.delete("/prices/AAPL/01/01/20#23")
    assert response.status_code == status.HTTP_406_NOT_ACCEPTABLE
    assert response.json() == {
      "detail": "Date has wrong format"
    }


# Tests attempting to delete stock price data for a non-existent date
def test_delete_stock_price_date_not_found():
    response = client.delete("/prices/AAPL/01/01/2023")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
      "detail": "Date not found"
    }
