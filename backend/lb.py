from fastapi import FastAPI, HTTPException, Request
import httpx
import itertools
import asyncio

app = FastAPI()

servers = {
    "http://127.0.0.1:8001/": True,
    "http://127.0.0.1:8002/": True,
    "http://127.0.0.1:8003/": True,
}

async def check_server(server):
    print("Checking!", server, flush=True)
    await asyncio.sleep(5)
    try:
        async with httpx.AsyncClient() as client:
            print("Checking", server, flush=True)
            
            response = await client.get(f"{server}health")
            print("Status:", response.status_code, flush=True)

        servers[server] = response.status_code == 200
    except Exception as e:
        print("Health check failed:", server, repr(e), flush=True)
        servers[server] = False



async def health_check():
    while True:
        await asyncio.sleep(60)

        tasks = [check_server(server) for server in servers]
        await asyncio.gather(*tasks)

        

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(health_check())


urls = itertools.cycle(servers)


def get_next_server():
    print("Healthy count =", sum(servers.values()), flush=True)
    instance = next(urls)
    if sum(servers.values()) > 0:
        while servers[instance] != True:
            print("Trying server:", instance, flush=True)
            instance = next(urls)
    else:
        raise HTTPException(
            status_code=503,
            detail="No healthy backend servers available"
        )
    
    return instance


async def forward_requests(url: str):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
    except httpx.ConnectError:
        print("Request ", url, " Failed")
        raise HTTPException(status_code=503)
    
    return response


@app.api_route("/", methods=["GET"])
@app.api_route("/{catchall:path}",methods=["GET"])
async def reverse_proxy(request:Request, catchall:str = ""):
    instance = get_next_server()
    print(request.url, flush = True)
    try:
        response = await forward_requests(instance+catchall)
        return response.json()
    except HTTPException as e:
        if e.status_code == 503:
            servers[instance] = False
        raise
