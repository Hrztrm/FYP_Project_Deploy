import requests

endpoint = "http://localhost:8000/login_api/"
content = {
    "username":"Ikmal",
    "password":"CHOCOLATE123"
}
get_response = requests.post(endpoint, content)

print(get_response.text)
print(get_response.json())

#Or using in cmd
#http POST 127.0.0.1:8000/login_api/ username=Ikmal password=CHOCOLATE123