import asyncio
import logging
import random
import uuid
from typing import Dict

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from models import Error, OrderInput, OrderOutput
from utils import simulate_delay

# Initialize FastAPI app (taken from openapi3.yaml)
app = FastAPI(
    title="Forex Trading Platform API",
    description="A RESTful API to simulate a Forex trading platform with WebSocket support for real-time order updates.",
    version="1.0.0",
)

# In-memory database to store orders
orders_db: Dict[str, Dict] = {}

logger = logging.getLogger("fastapi_custom_logger")


# WebSocket manager for real-time updates
class WebSocketManager:
    def __init__(self):
        # Dictionary to hold active WebSocket connections with unique IDs
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket) -> str:
        """
        Accepts a new WebSocket connection and stores it with a unique ID.

        :param websocket: The WebSocket connection to add
        :return: A unique connection ID
        """
        await websocket.accept()
        connection_id = str(uuid.uuid4())
        self.active_connections[connection_id] = websocket
        logger.info(f"New connection: {connection_id}")
        return connection_id

    async def disconnect(self, connection_id: str):
        """
        Removes a WebSocket connection from the active connections list.

        :param connection_id: The ID of the connection to remove
        """
        if connection_id in self.active_connections:
            websocket = self.active_connections.pop(connection_id)
            try:
                await websocket.close()
                logger.info(f"Disconnected: {connection_id}")
            except Exception as e:
                logger.info(
                    f"Error sending WebSocket message to closed or inactive {connection_id}: {e}"
                )

    async def broadcast_statuses(self):
        """
        Broadcast the current order statuses to all active WebSocket connections.
        Removes any connections that are no longer active.
        """
        inactive_connections = []
        for connection_id, websocket in self.active_connections.items():
            try:
                # Send the current order statuses to the client
                await websocket.send_json(list(orders_db.values()))
            except Exception as e:
                # Handle closed or inactive WebSocket connections
                logger.info(f"Error sending WebSocket message to {connection_id}: {e}")
                inactive_connections.append(connection_id)

        # Remove inactive connections
        for connection_id in inactive_connections:
            await self.disconnect(connection_id)


websocket_manager = WebSocketManager()


# Endpoints
@app.get("/orders", response_model=list[OrderOutput], summary="Retrieve all orders")
async def get_orders():
    """
    Retrieve all orders currently stored in the system.

    :return: A list of all orders with their details.
    """
    await simulate_delay()
    return list(orders_db.values())


@app.post(
    "/orders", response_model=OrderOutput, status_code=201, summary="Place a new order"
)
async def create_order(order: OrderInput):
    """
    Place a new order in the system.

    :param order: The details of the order to be created.
    :return: The created order with its unique ID and initial status.
    """
    await simulate_delay()
    order_id = str(uuid.uuid4())
    new_order = {
        "id": order_id,
        "stocks": order.stocks,
        "quantity": order.quantity,
        "status": "PENDING",
    }
    orders_db[order_id] = new_order
    asyncio.create_task(change_order_status(order_id))
    await websocket_manager.broadcast_statuses()
    return new_order


@app.get(
    "/orders/{order_id}",
    response_model=OrderOutput,
    summary="Retrieve a specific order",
)
async def get_order(order_id: str):
    """
    Retrieve the details of a specific order by its ID.

    :param order_id: The unique ID of the order to retrieve.
    :return: The details of the requested order.
    :raises HTTPException: If the order ID is not found.
    """
    await simulate_delay()
    order = orders_db.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@app.delete("/orders/{order_id}", status_code=204, summary="Cancel an order")
async def delete_order(order_id: str):
    """
    Cancel an existing order by its ID.

    :param order_id: The unique ID of the order to cancel.
    :raises HTTPException: If the order ID is not found or if the order cannot be canceled.
    """
    await simulate_delay()
    order = orders_db.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order["status"] != "PENDING":
        raise HTTPException(
            status_code=400, detail="Order can only be cancelled when status is PENDING"
        )
    order["status"] = "CANCELLED"
    await websocket_manager.broadcast_statuses()


@app.websocket(
    "/ws/orders", name="WebSocket connection for real-time order information"
)
async def websocket_endpoint(websocket: WebSocket):
    """
    Establishes a WebSocket connection to provide real-time updates on orders.

    :param websocket: The WebSocket connection object.
    """
    connection_id = await websocket_manager.connect(websocket)
    try:
        while True:
            # Send all orders to the client every second
            await websocket_manager.broadcast_statuses()
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {connection_id}")
    finally:
        await websocket_manager.disconnect(connection_id)


# Simulate status updates
async def change_order_status(order_id: str):
    """
    Simulates the status update of an order after a processing delay.

    :param order_id: The unique ID of the order to update.
    """
    await asyncio.sleep(random.uniform(1, 2))  # Simulate processing time
    order = orders_db.get(order_id)
    if order and order["status"] == "PENDING":
        order["status"] = "EXECUTED"
        await websocket_manager.broadcast_statuses()


@app.on_event("startup")
async def startup_event():
    """
    Event triggered when the application starts up.
    """
    logger.info("Server is starting...")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Event triggered when the application shuts down.
    """
    logger.info("Server is shutting down...")
