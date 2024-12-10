# Stock API

This is a simple API for managing and querying stock data, built with FastAPI and Docker. The API provides endpoints to get, update, and delete stock information, as well as stock prices and profit calculation.


## Prerequisites

Before you begin, ensure you have **Docker** installed on your machine.


## Running the Application

Follow the steps below to get the application running locally using Docker:


### 1. Clone the Repository

Clone this repository to your local machine:
```bash
git clone https://github.com/iarizanovic/Stock_api.git
cd Stock_api
```

### 2. Build and Start the Docker Containers

Use Docker Compose to build and start the application containers.
From the root directory of the project, run the following command:
```bash
docker-compose up --build
```

This will build the Docker image, do the tests and start the `api` service, exposing the application on port `8000`.


### 3. Access the Application

Once the Docker containers are running, you can access the API at:
```bash
http://localhost:8000
```

Below is a list of available endpoints:

#### Stock Endpoints

- **GET /stocks/**: Retrieve all stocks in the database.
- **POST /stocks/**: Add a new stock to the database.
- **GET /stocks/{ticker}**: Retrieve information about a stock by its ticker (e.g., `AAPL` for Apple).
- **PUT /stocks/{ticker}**: Update an existing stock's information.
- **DELETE /stocks/{ticker}**: Delete a stock by its ticker.

#### Stock Prices Endpoints

- **GET /prices/{ticker}**: Retrieve all stock prices for a given stock by its ticker.
- **POST /prices/{ticker}**: Add stock price data for a specific stock.
- **GET /prices/{ticker}/{month}/{day}/{year}**: Retrieve stock price data for a given date (e.g., `AAPL/07/24/2000`).
- **PUT /prices/{ticker}/{month}/{day}/{year}**: Update stock price data for a specific date.
- **DELETE /prices/{ticker}/{month}/{day}/{year}**: Delete stock price data for a specific date.

#### Profit Endpoint

- **POST /profit/**: Calculate profit based on the provided data.


## Documentation

You can easily access the interactive API documentation for your application. This documentation is automatically generated and allows you to test the API endpoints directly from your browser. It provides an intuitive interface for exploring and interacting with your API.
To view the documentation, simply open the following link in your web browser:
```bash
http://localhost:8000/docs
```

## Testing

The project includes tests for the API endpoints using pytest, which will be automatically started by Docker.


## Stopping the Application

To stop the Docker containers, run the following command in the project root directory:

```bash
docker-compose down
```

## Author

Ivan Arizanovic <ivanarizanovic@yahoo.com>
