import asyncio
import json
import time
import uuid

import pytest
import pytest_asyncio
from httpx import AsyncClient
from websockets import connect


@pytest.mark.asyncio
async def test_create_order(async_client, stock):
    response = await async_client.post(
        "/orders",
        json={
            "stocks": stock["name"],
            "quantity": stock["quantity"],
            "price": stock["price"],
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data


@pytest.mark.asyncio
async def test_get_order(async_client, create_order, stock):
    order_id = create_order["id"]

    get_response = await async_client.get(f"/orders/{order_id}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["id"] == order_id
    assert data["stocks"] == stock["name"]
    assert data["status"] == "PENDING"


@pytest.mark.asyncio
async def test_delete_existing_order(async_client, create_order):
    order_id = create_order["id"]

    delete_response = await async_client.delete(f"/orders/{order_id}")
    assert delete_response.status_code == 204


@pytest.mark.asyncio
async def test_delete_executed_order(async_client, create_order):
    order_id = create_order["id"]

    await asyncio.sleep(5)

    delete_response = await async_client.delete(f"/orders/{order_id}")
    assert delete_response.status_code == 400


@pytest.mark.asyncio
async def test_delete_non_existing_order(async_client):
    order_id = str(uuid.uuid4())
    get_response = await async_client.delete(f"/orders/{order_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_list_orders(async_client, stock):
    # Create a few orders
    for i in range(3):
        await async_client.post(
            "/orders",
            json={
                "stocks": stock["name"],
                "quantity": stock["quantity"],
                "price": stock["price"],
            },
        )

    response = await async_client.get("/orders")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3


@pytest.mark.asyncio
async def test_websocket_order_executed(async_client, create_order):
    order_id = create_order["id"]

    host_and_port = f"{str(async_client.base_url.host)}:{async_client.base_url.port}"
    uri = f"ws://{host_and_port}/ws/orders"
    async with connect(uri) as websocket:
        order_state = []
        executed = False
        # Loop to imitate "processing time" to have 100% executed status
        while not executed:
            message = await websocket.recv()
            json_message = json.loads(message)
            test_order = [item for item in json_message if item["id"] == order_id][0]
            order_state.append(test_order)
            if test_order["status"] == "EXECUTED":
                executed = True
                await websocket.close()
        assert order_state[0]["status"] == "PENDING"
        assert order_state[-1]["status"] == "EXECUTED"


@pytest.mark.asyncio
async def test_websocket_order_cancelled(async_client, create_order):
    order_id = create_order["id"]

    await async_client.delete(f"/orders/{order_id}")

    host_and_port = f"{str(async_client.base_url.host)}:{async_client.base_url.port}"
    uri = f"ws://{host_and_port}/ws/orders"
    async with connect(uri) as websocket:
        order_state = []
        cancelled = False
        # Poll the order status to see it cancelled
        while not cancelled:
            message = await websocket.recv()
            json_message = json.loads(message)
            test_order = [item for item in json_message if item["id"] == order_id][0]
            order_state.append(test_order)
            if test_order["status"] == "CANCELLED":
                cancelled = True
                await websocket.close()

        assert order_state[-1]["status"] == "CANCELLED"
