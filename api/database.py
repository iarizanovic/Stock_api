from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Date, Float
from sqlalchemy.orm import sessionmaker, declarative_base, relationship, Session
import os

# SQLite
DB_FILE_PATH = './stock_data.db'
DATABASE_URL = f'sqlite:///{DB_FILE_PATH}'
engine = create_engine(DATABASE_URL, connect_args={'check_same_thread': False})

# Create the session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """
    Create and yield a database session.

    This function is used by FastAPI's dependency injection system to provide a session
    that connects to the SQLite database. It ensures that the session is properly closed
    after use.

    :return: A session object that connects to the database.
    """
    # Init the database
    init_db()

    # Start the session
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def add_stocks(db: Session):
    """
    Add predefined stocks to the database.

    This function inserts several predefined stocks into the database, along with their
    ticker symbols and inception dates. The stock data is hardcoded in the function.

    :param db: The database session used to commit the stock data to the database.
    """
    company_data = {
        "Amazon": {"ticker": "AMZN", "inception_date": "1997-05-15"},
        "Apple": {"ticker": "AAPL", "inception_date": "1976-04-01"},
        "Facebook": {"ticker": "META", "inception_date": "2004-02-04"},
        "Google": {"ticker": "GOOGL", "inception_date": "1998-09-04"},
        "Netflix": {"ticker": "NFLX", "inception_date": "1997-08-29"},
    }

    for name, info in company_data.items():
        stock = Stock(
            name=name,
            ticker=info["ticker"],
            inception_date=datetime.strptime(info["inception_date"], "%Y-%m-%d").date()
        )
        db.add(stock)
        db.commit()
        print(f"Stock '{name}' added to the database.")


def import_csv_to_stock_prices(csv_file_path: str, company_name: str, db: Session):
    """
    Import stock prices from a CSV file and store them in the database.

    This function reads a CSV file containing stock price data, validates that the required
    columns are present, and imports the data into the `stock_prices` table of the database
    for the given company.

    :param csv_file_path: The path to the CSV file containing the stock price data.
    :param company_name: The name of the company whose stock prices are being imported.
    :param db: The database session used to insert the stock price data into the database.
    """
    # Read the CSV file
    df = pd.read_csv(csv_file_path)

    # Check if all columns exists
    required_columns = {"Date", "Open", "High", "Low", "Close", "Adj Close", "Volume"}
    if not required_columns.issubset(df.columns):
        print(f"CSV file {csv_file_path} is missing required columns: {required_columns}")
        return

    # Check if Stock exists
    stock = db.query(Stock).filter(Stock.name == company_name).first()
    if not stock:
        return

    # Drop NaN rows
    df.dropna(inplace=True)

    # Add data into DB
    for _, row in df.iterrows():
        stock_price = StockPrice(
            stock_id=stock.id,
            date=datetime.strptime(row["Date"], "%Y-%m-%d").date(),
            open=row["Open"],
            high=row["High"],
            low=row["Low"],
            close=row["Close"],
            adj_close=row["Adj Close"],
            volume=int(row["Volume"]),
        )
        db.add(stock_price)

    # Commit the changes
    db.commit()


def init_db():
    """
    Initialize the database by creating tables and importing stock data.

    This function checks if the database already exists. If it doesn't, it creates the tables
    and populates the database with predefined stock data and stock prices from CSV files
    located in the "csv_files" directory.

    This function is intended to be used to set up the database during the initial setup.
    """
    # Check if DB file exists
    if os.path.exists(DB_FILE_PATH):
        return

    # Create DB
    Base.metadata.create_all(bind=engine)

    # Fill DB
    csv_directory = "./csv_files"
    with SessionLocal() as db:
        # Add Stocks info
        add_stocks(db)

        # Add CSV files into base
        for file in os.listdir(csv_directory):
            # Avoid non CSV files
            if not file.endswith(".csv"):
                continue

            # Derive the company name from the file name
            company_name = os.path.splitext(file)[0]
            file_path = os.path.join(csv_directory, file)

            # Import the CSV into its own table
            print(f"Importing data for {company_name} from {file_path}...")
            import_csv_to_stock_prices(file_path, company_name, db)


class Stock(Base):
    """
    A model representing a stock in the database.

    This class defines the schema for the "stocks" table in the database. Each stock has
    a name, ticker symbol, and inception date. The `prices` relationship defines a one-to-many
    relationship between the `Stock` and `StockPrice` models.

    Attributes:
        id: The primary key of the stock record.
        name: The name of the company (e.g., "Amazon").
        ticker: The ticker symbol for the stock (e.g., "AMZN").
        inception_date: The date when the stock was first publicly traded.
        prices: A relationship to the `StockPrice` model, representing the stock's price history.
    """
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    ticker = Column(String, unique=True, index=True, nullable=False)
    inception_date = Column(Date, nullable=False)

    prices = relationship("StockPrice", back_populates="stock")


class StockPrice(Base):
    """
    A model representing stock price data in the database.

    This class defines the schema for the "stock_prices" table in the database. Each record
    represents the stock price for a given stock on a specific date, including the opening,
    closing, high, low, adjusted closing prices, and volume of trades.

    Attributes:
        id: The primary key for the stock price entry.
        stock_id: The foreign key referencing the stock this price belongs to.
        date: The date when the stock price was recorded.
        open: The opening price of the stock on the given date.
        high: The highest price the stock reached on the given date.
        low: The lowest price the stock reached on the given date.
        close: The closing price of the stock on the given date.
        adj_close: The adjusted closing price, accounting for splits, dividends, etc.
        volume: The trading volume for the stock on the given date.
        stock: The relationship to the `Stock` model, which provides the stock this price belongs to.
    """
    __tablename__ = "stock_prices"

    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    date = Column(Date, nullable=False)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    adj_close = Column(Float, nullable=False)
    volume = Column(Integer, nullable=False)

    stock = relationship("Stock", back_populates="prices")
