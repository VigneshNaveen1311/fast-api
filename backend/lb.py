from fastapi import FastAPI, HTTPException
import httpx
import itertools
import asyncio

app = FastAPI()

# servers = [
#     ["http://127.0.0.1:8001/",True],
#     ["http://127.0.0.1:8002/",True],
#     ["http://127.0.0.1:8003/",True]
# ]

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


@app.get("/")
def ping_servers():
    
    print("REQUEST RECEIVED", flush=True)
    print("Healthy count =", sum(servers.values()), flush=True)
    # raise Exception("Test")
    print(servers, flush=True)
    instance = next(urls)
    if sum(servers.values()) > 0:
        while servers[instance] != True:
            print("Trying server:", instance, flush=True)
            instance = next(urls)
    else:
        raise HTTPException(status_code=404)

    try:
        with httpx.Client() as client:
            response = client.get(instance)
    # except httpx.RequestError:
    #     raise HTTPException(status_code=503)
    except httpx.ConnectError:
        print("Instance ", instance, " Failed")
        servers[instance] = False
        raise HTTPException(status_code=503)
    except Exception as e:
        print(repr(e))
        raise
    

    return response.json()