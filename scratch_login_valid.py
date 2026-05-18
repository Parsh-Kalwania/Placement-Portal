import requests
response = requests.post('http://127.0.0.1:8000/api/token/', json={'username': 'teststudent', 'password': 'password123'})
print("Status:", response.status_code)
print("Text:", response.text)
