from fastapi import FastAPI, HTTPException, Request, Response
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


async def forward_requests(url: str, method, headers, body):
    # print("Reached forward_requests: ", url)
    # await asyncio.sleep(10) #turning off a server mid request to check redundant server call
    print("Trying connection to ", url)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                content=body
            )
    except httpx.ConnectError:
        print("Request ", url, " Failed")
        raise HTTPException(status_code=503)
    
    return response


@app.api_route("/", methods=["GET"])
@app.api_route("/{catchall:path}",methods=["GET","POST"])
async def reverse_proxy(request:Request, catchall:str = ""):
    
    retries = sum(servers.values())
    body = await request.body()
    headers = dict(request.headers)
    headers.pop("host", None) #dont want to forward localhost
    print("BODY =", body, flush = True)
    print("HEADERS =", headers, flush = True)
    while retries>0:
        instance = get_next_server()
        print(request.url, flush = True)
        try:
            # response = await forward_requests(instance+catchall)
            response = await forward_requests(
                url=instance+catchall,
                method=request.method,
                headers=headers,
                body=body
            )
            return Response(
                content=response.content,
                status_code=response.status_code
            )
        except HTTPException as e:
            if e.status_code == 503:
                servers[instance] = False
                retries -= 1
                continue

            raise #when its not 503 raise the exception
    
    raise HTTPException(
        status_code=503,
        detail="No healthy backend servers"
    )
