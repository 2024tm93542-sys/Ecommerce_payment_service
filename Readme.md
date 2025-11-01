# Payment Service

A FastAPI-based RESTful service for managing e-commerce payments with MySQL backend.

## Features

- Probabilistic payment processing (simulated)
- Idempotent refund operations
- Payment status tracking
- Pagination and filtering for payment history
- Multiple payment methods (UPI, CARD, COD)
- CSV data import utility
- Connection pooling for database operations

## Project Structure

```
ecommerce_payment_service/
├─ app/
│  ├─ __init__.py
│  ├─ main.py         # FastAPI application and route definitions
│  ├─ config.py       # Configuration settings
│  ├─ db.py          # Database connection management
│  ├─ schemas.py     # Pydantic models for request/response
│  └─ crud.py        # Database operations
├─ requirements.txt   # Project dependencies
├─ Dockerfile        # Container configuration
├─ ddl.sql          # Database schema
├─ csv_loader.py     # Data import utility
└─ README.md
```

## API Endpoints

- `POST /v1/payments/charge` - Process a new payment
  - Request body:
    ```json
    {
      "order_id": 342,
      "amount": 561.00
    }
    ```
  - Returns payment reference and status

- `POST /v1/payments/{payment_id}/refund` - Process a refund (idempotent)
  - Returns refund confirmation with amount and payment method
  - Validates payment status before refund

- `GET /v1/payments` - List payments with filtering and pagination
  - Query Parameters:
    - `page`: Page number (default: 1)
    - `per_page`: Items per page (default: 10, max: 200)
    - `order_id`: Filter by order ID
    - `method`: Filter by payment method
    - `status`: Filter by payment status
    - `amount_gt`: Filter by amount greater than
    - `amount_lt`: Filter by amount less than
    - `start_date`: Filter by date range start
    - `end_date`: Filter by date range end
    - `sort_by_created`: Sort by creation date (asc/desc)

## Setup

### Using Docker (Recommended)

1. Make sure Docker and Docker Compose are installed on your system.

2. Create a `.env` file with your MySQL password:
```bash
MYSQL_PASSWORD=your_secure_password
```

3. Build and start the services:
```bash
docker-compose up --build
```

The services will be available at:
- API: http://localhost:8001
- MySQL: localhost:3308
- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

Sample data will be automatically loaded by the data_loader service.

To stop the services:
```bash
docker-compose down
```

To reset the database (this will delete all data):
```bash
docker-compose down -v
docker-compose up --build
```

### Manual Setup (Alternative)

1. Set up a Python virtual environment:
```bash
# Create a new virtual environment
python -m venv .venv

# Activate the virtual environment
# On Windows:
.venv\Scripts\activate
# On Unix or MacOS:
source .venv/bin/activate
```

2. Install dependencies in the virtual environment:
```bash
pip install -r requirements.txt
```

3. Set up the database:
```bash
mysql -u root -p < ddl.sql
```
OR 
manually run the ddl.sql contents in MySQL Workbench/command line

4. Set up environment variables:
   - Create a `.env` file with the following content:
     ```
     MYSQL_HOST=127.0.0.1
     MYSQL_USER=root
     MYSQL_PASSWORD=your_password_here
     MYSQL_DB=ecommerce
     ```
   - Update `MYSQL_PASSWORD` with your database password

5. Load sample data (optional):
```bash
python csv_loader.py --password your_mysql_password
```

## Running the Application

### Using Docker (Recommended)
```bash
# Start all services
docker-compose up

# Or rebuild and start (after changes)
docker-compose up --build
```

The API will be available at `http://localhost:8001`
MySQL will be available at `localhost:3308`

### Manual Start
Start the FastAPI server:
```bash
python -m uvicorn app.main:app --reload --port 8001
```

The API documentation will be available at:
- Swagger UI: `http://localhost:8001/docs`
- ReDoc: `http://localhost:8001/redoc`

## Virtual Environment Management

### Activating the Environment
```bash
# On Windows:
.venv\Scripts\activate
# On Unix or MacOS:
source .venv/bin/activate
```

### Deactivating the Environment
```bash
deactivate
```

## Dependencies

- FastAPI
- Uvicorn
- MySQL Connector Python
- Pydantic
- Pydantic-Settings

## Database Schema

```sql
CREATE TABLE payments (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    amount DECIMAL(10,2),
    method VARCHAR(255) NOT NULL,
    status BOOLEAN,
    reference VARCHAR(100) UNIQUE,
    created_at TIMESTAMP,
    refunded BOOLEAN NOT NULL DEFAULT 0
);
```

## Sample API Usage

### Create a Payment
```bash
curl -X 'POST' \
  'http://127.0.0.1:8001/v1/payments/charge' \
  -H 'Content-Type: application/json' \
  -d '{
    "order_id": 342,
    "amount": 561.00
}'
```

### Process a Refund
```bash
curl -X 'POST' \
  'http://127.0.0.1:8001/v1/payments/123/refund'
```

### List Payments with Filters
```bash
curl 'http://127.0.0.1:8001/v1/payments?page=1&per_page=10&method=UPI&status=SUCCESS'
```

### Connect to MySQL
```bash
# Using docker compose
docker-compose exec db mysql -u root -p${MYSQL_PASSWORD} ecommerce

# Or from host machine
mysql -h 127.0.0.1 -P 3308 -u root -p ecommerce
``` 