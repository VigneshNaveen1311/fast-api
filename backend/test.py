import requests

#test code to check reverse proxy post method

r = requests.post(
    "http://localhost:8000/add_user",
    json={"name": "Vignesh"}
)

print(r.status_code)
print(r.text)


import redis
r = redis.Redis(host='localhost', port=6379, db=0)
r.set('foo', 'bar')
print(r.get('foo'))