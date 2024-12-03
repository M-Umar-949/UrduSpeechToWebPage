import requests

# Replace this with the ngrok URL from Colab
url = "https://c0df-34-125-22-152.ngrok-free.app/transcribe" 

# Path to your audio file
file_path = "/home/umar/Documents/NLP/UrduSpeechToWebPage/backend/recording.mp3"

# Open the file in binary mode and send it as part of the POST request
with open(file_path, 'rb') as f:
    files = {'file': ('recording.mp3', f, 'audio/mpeg')}
    response = requests.post(url, files=files)

# Check the response
print(f"Status Code: {response.status_code}")
if response.status_code == 200:
    print("Response JSON:", response.json())
else:
    print("Error response:", response.text)
