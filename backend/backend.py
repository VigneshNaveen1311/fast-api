from fastapi import FastAPI
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