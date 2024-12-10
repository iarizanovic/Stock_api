from main import app
from fastapi.testclient import TestClient
from fastapi import status

client = TestClient(app)


# Test case to get all stocks and check if they are returned correctly
def test_get_all_stocks():
    response = client.get("/stocks/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {
            "name": "Amazon",
            "ticker": "AMZN",
            "inception_date": "1997-05-15",
            "id": 1
        },
        {
            "name": "Apple",
            "ticker": "AAPL",
            "inception_date": "1976-04-01",
            "id": 2
        },
        {
            "name": "Facebook",
            "ticker": "META",
            "inception_date": "2004-02-04",
            "id": 3
        },
        {
            "name": "Google",
            "ticker": "GOOGL",
            "inception_date": "1998-09-04",
            "id": 4
        },
        {
            "name": "Netflix",
            "ticker": "NFLX",
            "inception_date": "1997-08-29",
            "id": 5
        }
    ]


# Test case to create a stock, expect an error for an existing stock (Apple)
def test_create_stock():
    request_data = {
      "inception_date": "1976-04-01",
      "name": "Apple",
      "ticker": "AAPL"
    }
    response = client.post('/stocks/', json=request_data)
    assert response.status_code == status.HTTP_406_NOT_ACCEPTABLE
    assert response.json() == {
      "detail": "Stock already exists"
    }


# Test case to create a new stock (Apple2), expect successful creation
def test_create_stock2():
    request_data = {
      "inception_date": "1976-04-01",
      "name": "Apple2",
      "ticker": "AAPL2"
    }
    response = client.post('/stocks/', json=request_data)
    assert response.status_code == status.HTTP_201_CREATED


# Test case to retrieve a stock by its ticker (Apple), check that the data matches
def test_get_stock():
    response = client.get("/stocks/AAPL")
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert response_json["name"] == "Apple"
    assert response_json["ticker"] == "AAPL"
    assert response_json["inception_date"] == "1976-04-01"


# Test case to update a stock (Apple2), check if the update succeeds
def test_update_stock():
    request_data = {
      "inception_date": "1976-04-01",
      "name": "Apple22",
      "ticker": "AAPL22"
    }
    response = client.put("/stocks/AAPL2", json=request_data)
    assert response.status_code == status.HTTP_202_ACCEPTED


# Test case to delete a stock (Apple22), verify successful deletion
def test_delete_stock():
    response = client.delete("/stocks/AAPL22")
    assert response.status_code == status.HTTP_202_ACCEPTED
