from pydantic import BaseModel


# Order models
class OrderInput(BaseModel):
    stocks: str  # Currency pair symbol
    quantity: float  # Quantity of the currency pair to be traded


class OrderOutput(OrderInput):
    id: str  # Unique identifier for the order
    status: str  # Order status (pending, executed, canceled)


class Error(BaseModel):
    code: int  # Error code
    message: str  # Error message
