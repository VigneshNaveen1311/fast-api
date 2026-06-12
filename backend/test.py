import requests

#test code to check reverse proxy post method

r = requests.post(
    "http://localhost:8000/add_user",
    json={"name": "Vignesh"}
)

print(r.status_code)
print(r.text)