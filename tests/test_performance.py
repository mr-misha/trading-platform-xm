import asyncio
import statistics
import time

import httpx
import pytest
from conftest import server


@pytest.mark.asyncio
async def test_api_performance_async():
    """
    Test the performance of the API by placing multiple orders asynchronously.

    Steps:
    1. Place 100 orders concurrently.
    2. Collect response times for each request.
    3. Calculate and print average response time and standard deviation.
    """
    num_requests = 100
    orders = [
        {"stocks": f"STOCK-{i}", "quantity": i + 1, "price": 1}
        for i in range(num_requests)
    ]
    response_times = []

    async def post_order(order):
        async with httpx.AsyncClient() as client:
            start_time = time.time()
            response = await client.post(f"http://{server}/orders", json=order)
            end_time = time.time()
            response_times.append(end_time - start_time)
            assert response.status_code == 201, f"Order failed: {response.json()}"

    # Execute all requests asynchronously
    await asyncio.gather(*(post_order(order) for order in orders))

    # Calculate performance metrics
    avg_response_time = statistics.mean(response_times)
    std_dev_response_time = statistics.stdev(response_times)
    max_response_time = max(response_times)
    min_response_time = min(response_times)

    # Output performance metrics
    print("\nPerformance Metrics:")
    print(f"Total Requests: {num_requests}")
    print(f"Average Response Time: {avg_response_time:.3f} seconds")
    print(f"Standard Deviation: {std_dev_response_time:.3f} seconds")
    print(f"Max Response Time: {max_response_time:.3f} seconds")
    print(f"Min Response Time: {min_response_time:.3f} seconds")

    # Assert performance thresholds
    assert (
        avg_response_time < 3
    ), f"Average response time is '{avg_response_time}' which exceeds 3 seconds"
    assert (
        max_response_time < 5
    ), f"Maximum response time is '{max_response_time}' which exceeds 3 seconds"
