# Test Task SDET python trading-platform-xm
Automation testing using Python 3
Example of successful run https://youtu.be/lXe_h-Zf19g

    trading-platform-xm/
    ├── docker-compose.yaml
    ├── Dockerfile
    ├── Dockerfile-tests
    ├── Pipfile
    ├── Pipfile.lock
    ├── pytest.ini
    ├── README.md
    ├── reports
    ├── tests
    │   ├── conftest.py
    │   ├── test_data
    │   │   └── stocks.json
    │   ├── test_performance.py
    │   └── test_trading_api_server.py
    └── trading_app
        ├── models.py
        ├── trading_api_server.py
        └── utils.py

## Trading Platform API

### Overview

This project simulates a trading platform API with WebSocket status support. The API is built using FastAPI and Dockerised for easy deployment.

### Requirements

- Docker
- Docker Compose (optional)
- Clone repository:
  - ```
    # pip install pipenv
    # pipenv shell
    ```
- Install Pipfile requirements by running command:
  - ```pipenv install```
- Install Docker Desktop & Run it

### Running the Application

1. **Build the Docker image:**

    ````
    docker build -t trading-platform-xm-api .
    ````

2. **When you want to run standalone the Trading API Docker container:**

    ````
    docker run -d -p 8000:8000 trading-platform-xm-api
    ````

3. **Build the Test Docker image:**

    ````
    docker build -t trading-platform-xm-tests .
    ````

4. **Run the Docker Compose**

    ````
    docker-compose up --build
    ````

    - Copy report file:
      ```commandline
      docker cp trading-platform-xm-tests:/tests/reports/report.html ./reports/report.html
      ```


5. **Shut Down the Docker Compose and Clean Up images**
    ````
    docker-compose down && docker rmi $(docker images -q)
    ````

6. **Access the API documentation:**
Open your browser and navigate to http://localhost:8000/docs to view the automatically generated API documentation provided by Swagger.


    Endpoints:
    - POST /orders: Create a new order.
    - GET /orders/{order_id}: Get order details by order_id.
    - DELETE /orders/{order_id}: Delete an order by order_id.
    - ws://localhost:8000/ws/orders: WebSocket endpoint for real-time status updates.

7. **Making API Requests**
Use tools like curl, Postman, or directly through the Swagger UI.

Example curl Commands

- Create an Order:
    ````
    curl -X POST http://localhost:8000/orders -H "Content-Type: application/json" -d '{"stocks":"AAPL", "quantity": 15, "price":100}'
    ````

- Get an Order:
    ````
    curl -X GET "http://localhost:8000/orders/{order_id}"
    ````

- Get all Orders:
    ````
    curl -X GET "http://localhost:8000/orders"
    ````

- Delete an Order:
    ````
    curl -X DELETE "http://localhost:8000/orders/{order_id}"
    ````

### Running the Tests

1. **Run the API tests**:
   ```
    pytest tests/test_trading_api_server.py --html=reports/report.html
   ```

2. **Run the performance tests**:
    ```
    pytest tests/test_performance.py --html=reports/report_performance.html
   ```
