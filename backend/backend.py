from fastapi import FastAPI, Request
import os
import http

app = FastAPI()
SERVER = os.getenv("SERVER", "Unknown")


@app.get("/hello")
def ping_server():
    return {
        "message": "Hello from backend",
        "server instance" : SERVER
    }

@app.get("/health")
def health_check():
    return http.HTTPStatus.OK

@app.post("/add_user")
async def echo(request:Request):
    raw = await request.body()
    print(raw, flush=True)
    data = await request.json()
    return data