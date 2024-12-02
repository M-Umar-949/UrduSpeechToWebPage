import requests

# Replace with the printed Public URL from Colab (ensure it ends with /transcribe)
url = "https://9a1a-34-106-118-81.ngrok-free.app/transcribe"

# Path to your local audio file
file_path = "C:\\Users\\Dell\\Desktop\\nlpproject\\UrduSpeechToWebPage\\backend\\recording.mp3"

# Open the file and send it via POST request
with open(file_path, 'rb') as f:
    files = {'file': (file_path, f, 'audio/mpeg')}
    response = requests.post(url, files=files)

    # Check the response
    if response.status_code == 200:
        data = response.json()
        transcription = data.get('transcription', '')
        print("\nTranscription Received:\n", transcription)
        
        # Save the transcription to a local file
        with open("transcription.txt", "w", encoding='utf-8') as txt_file:
            txt_file.write(transcription)
        print("\nTranscription saved to 'transcription.txt' locally!")
    else:
        print(f"Error {response.status_code}: {response.text}")
