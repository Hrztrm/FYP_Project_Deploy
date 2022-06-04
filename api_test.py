import requests

endpoint = "http://localhost:8000/login_api/"
content = {
    "username":"Ikmal",
    "password":"CHOCOLATE123"
}
try:
    get_response = requests.post(endpoint, content)
except:
    print("Failed")
    exit (0)
json_get_response = get_response.json()
#print(get_response.text)
print(json_get_response)
print(type(json_get_response))
for a in json_get_response:
    print(a['id'])
    print(a['Name'])
    print(a['Password'])
#Or using in cmd
#http POST 127.0.0.1:8000/login_api/ username=Ikmal password=CHOCOLATE123