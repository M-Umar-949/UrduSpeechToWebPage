import requests

# Replace this URL with the ngrok URL printed in Colab
ngrok_url = "https://7718-34-19-90-48.ngrok-free.app"

# Test the root endpoint
response = requests.get(ngrok_url)
print("Root Endpoint Response:", response.json())

# Test the custom greeting endpoint
name = "Umar"
response = requests.get(f"{ngrok_url}/hello/{name}")
print("Custom Greeting Response:", response.json())
