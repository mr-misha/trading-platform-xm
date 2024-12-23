import json
import os
import random

import pytest
import pytest_asyncio
from httpx import AsyncClient

server = "api:8000" if os.path.exists("/.dockerenv") else "localhost:8000"


@pytest_asyncio.fixture(scope="function", autouse=True)
async def async_client():
    """
    Fixture to create an asynchronous HTTP client for testing.

    This fixture uses `httpx.AsyncClient` to provide a client configured with the base URL
    of the server under test. It automatically sets up and tears down the client for each
    test function to ensure a clean state.

    Yields:
        AsyncClient: An instance of `httpx.AsyncClient` for sending HTTP requests.
    """
    async with AsyncClient(base_url=f"http://{server}") as client:
        yield client


@pytest.fixture(scope="function")
def stock():
    """
    Fixture to provide a random stock entry from a predefined JSON file.

    This fixture reads the `stocks.json` file containing test stock data and selects a random stock
    from the "stocks" array. Useful for testing endpoints that require dynamic or varied stock input.

    Yields:
        dict: A dictionary representing a random stock with keys like "name", "quantity", and "price".

    Raises:
        FileNotFoundError: If the `stocks.json` file is not found.
        JSONDecodeError: If the `stocks.json` file is not a valid JSON file.
    """
    # Load the JSON file
    with open("./tests/test_data/stocks.json", "r") as file:
        data = json.load(file)
    # Select a random stock from the list
    stocks_amount = len(data["stocks"])
    rand_int = random.randint(0, stocks_amount - 1)
    yield data["stocks"][rand_int]


@pytest_asyncio.fixture(scope="function")
async def create_order(async_client, stock):
    """
    Fixture to create a new order using the provided asynchronous client and a random stock.

    This fixture sends a POST request to the `/orders` endpoint to create a new order with
    randomly selected stock data. The created order's details are yielded for use in tests.

    Args:
        async_client (AsyncClient): The asynchronous HTTP client.
        stock (dict): A dictionary containing stock details.

    Yields:
        dict: The JSON response from the order creation API, typically including details like
              order ID, stock name, quantity, price, and status.
    """
    create_response = await async_client.post(
        "/orders",
        json={
            "stocks": stock["name"],
            "quantity": stock["quantity"],
            "price": stock["price"],
        },
    )
    yield create_response.json()
