import requests

# URL of your FastAPI endpoint (ngrok URL)
url = "https://769b-34-168-16-214.ngrok-free.app/transcribe"

# Path to your audio file
file_path = "/home/umar/Documents/NLP/UrduSpeechToWebPage/backend/recording.mp3"

# Open the file in binary mode and send it as part of the POST request
with open(file_path, 'rb') as f:
    files = {'file': (file_path, f, 'audio/mpeg')}
    
    response = requests.post(url, files=files)

    # Check the response status code
    print(f"Status Code: {response.status_code}")

    # If the response is JSON, try to parse it
    if response.status_code == 200:
        try:
            print("Response JSON:", response.json())
        except ValueError:
            print("Response is not JSON:", response.text)
    else:
        print("Error response:", response.text)
