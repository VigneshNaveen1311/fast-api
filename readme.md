# FastAPI Load Balancer + Reverse Proxy + Redis Health Tracking

A mini distributed systems project built with **FastAPI**, **Redis**, and **multiple backend servers**.

This project simulates a real-world load balancer that sits in front of multiple backend servers and routes traffic intelligently.

---

# Features

## Load Balancer

* Reverse proxy built using FastAPI
* Round-robin server selection
* Automatic failover to healthy backend
* Shared health state stored in Redis

## Health Checking

Each backend exposes:

```http
GET /health
```

The load balancer periodically checks backend health.

Healthy server:

```json
200 OK
```

Unhealthy server:

* Connection failure
* Timeout
* Non-200 response

Health status is stored in Redis.

---

# Supported Proxy Features

Currently supports:

* GET
* POST

Proxy forwards:

* HTTP method
* Request body
* Request headers
* Response body
* Response status code

Example:

Client sends:

```http
POST /add_user
Content-Type: application/json
```

Proxy forwards entire request to backend.

---

# Project Structure

```bash
fast-api/
│
├── backend/
│   ├── main.py
│   ├── backend.py
│   ├── lb.py
│   └── test.py
│
├── requirements.txt
└── pyproject.toml
```

---

# Components

# 1. main.py

Learning playground for FastAPI basics.

Contains examples of:

* GET
* POST
* PUT
* DELETE
* Path params
* Query params
* Pydantic models
* Request body validation

Example:

```python
@app.post("/items/")
async def create_item(item: Item):
    item.name = item.name.capitalize()
    return item
```

---

# 2. backend.py

Backend server implementation.

Each backend instance runs separately:

* Server1 → port 8001
* Server2 → port 8002
* Server3 → port 8003

Example route:

```python
@app.get("/hello")
def ping_server():
    return {
        "message": "Hello from backend",
        "server instance": SERVER
    }
```

Health endpoint:

```python
@app.get("/health")
def health_check():
    return 200
```

POST example:

```python
@app.post("/add_user")
async def echo(request: Request):
    data = await request.json()
    return data
```

---

# 3. lb.py (Load Balancer)

Core project.

Responsibilities:

* Accept client request
* Choose backend server
* Forward request
* Retry if server is dead
* Return backend response

---

## Backend Pool

```python
servers = [
    "http://127.0.0.1:8001/",
    "http://127.0.0.1:8002/",
    "http://127.0.0.1:8003/"
]
```

---

## Round Robin

Implemented using:

```python
itertools.cycle
```

Example sequence:

```text
Server1 → Server2 → Server3 → Server1 ...
```

---

## Retry Logic

If chosen server is down:

1. Mark unhealthy
2. Save unhealthy state in Redis
3. Retry next server

Example:

```text
Request comes in
→ Server2 selected
→ Server2 down
→ Mark unhealthy
→ Retry Server3
→ Success
```

---

## Reverse Proxy Endpoint

Catch-all route:

```python
@app.api_route("/{catchall:path}")
```

This allows proxying any route:

```text
/hello
/add_user
/items/3
```

---

## Request Forwarding

Forwarded properties:

### Method

```python
request.method
```

Examples:

* GET
* POST

---

### Headers

```python
headers = dict(request.headers)
headers.pop("host", None)
```

Host is removed to avoid forwarding:

```text
localhost:8000
```

to backend.

---

### Body

```python
body = await request.body()
```

Example body:

```json
{
  "name": "Vignesh"
}
```

Forwarded using:

```python
content=body
```

---

## Response Preservation

Load balancer preserves:

* Response body
* Response status code

Example:

Backend returns:

```http
404 Not Found
```

Proxy also returns:

```http
404 Not Found
```

---

# 4. Redis

Redis stores backend health state.

Example:

```text
Key: http://127.0.0.1:8001/
Value: 1
```

Meaning:

* 1 → healthy
* 0 → unhealthy

---

## Why Redis?

Without Redis:

Restarting load balancer resets health state.

Example:

```text
Server2 died
LB marks Server2 unhealthy
LB restarts
Server2 becomes healthy again (wrong)
```

With Redis:

State survives LB restart.

---

# Running Redis with Docker

Install Docker Desktop first.

Verify:

```bash
docker --version
```

Run Redis:

```bash
docker run -p 6379:6379 -it redis:latest
```

Check Redis using Python:

```python
import redis

r = redis.Redis(host='localhost', port=6379, db=0)
r.set('foo', 'bar')
print(r.get('foo'))
```

Output:

```python
b'bar'
```

---

# Starting Backend Servers

PowerShell:

Server 1:

```powershell
$env:SERVER="Server1"; uvicorn backend.backend:app --port 8001
```

Server 2:

```powershell
$env:SERVER="Server2"; uvicorn backend.backend:app --port 8002
```

Server 3:

```powershell
$env:SERVER="Server3"; uvicorn backend.backend:app --port 8003
```

---

# Start Load Balancer

```powershell
uvicorn backend.lb:app --port 8000
```

---

# Testing

## Browser

Visit:

```text
http://localhost:8000/hello
```

Response:

```json
{
  "message": "Hello from backend",
  "server instance": "Server1"
}
```

Refresh multiple times to see round-robin.

---

## Python Test Script

`test.py`

```python
import requests

r = requests.post(
    "http://localhost:8000/add_user",
    json={"name": "Vignesh"}
)

print(r.status_code)
print(r.text)
```

Output:

```text
200
{"name":"Vignesh"}
```

---

# Failure Testing

Kill one backend:

Example:
Stop Server2.

Expected:

* Health check marks Server2 unhealthy
* Redis stores value 0
* Load balancer skips Server2

Requests continue through:

* Server1
* Server3

No downtime.

---

# Things Learned

## FastAPI

* Routing
* Request body
* Query params
* Path params
* Pydantic models

## Networking

* HTTP methods
* Headers
* Body forwarding
* Status codes

## Distributed Systems

* Reverse proxy
* Load balancing
* Round robin
* Failover
* Health checks

## Redis

* Key-value store
* Shared state
* Persistence across app restarts

---

# Future Improvements

Planned upgrades:

## HTTP Support

Add:

* PUT
* PATCH
* DELETE

---

## Smarter Health Checks

Add:

* Timeout detection
* Faster recovery
* Circuit breaker logic

---

## Redis Improvements

Use:

* TTL / expiry
* Automatic cleanup
* Pub/sub

---

## Database

Add:

* SQLite or Postgres

Use for persistent application data.

---

## Next Major Project: URL Shortener

Planned architecture:

```text
Client
  ↓
Load Balancer
  ↓
Backend Servers
  ↓
Redis Cache
  ↓
Postgres
```

Will introduce:

* Database indexing
* Cache hits/misses
* Write-through caching
* Real distributed architecture

```
```
