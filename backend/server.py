from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import os
import requests

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Colab server URL for transcription
COLAB_URL = "https://40de-34-143-195-15.ngrok-free.app/transcribe"  # Replace with your actual ngrok URL

@app.post("/upload")
async def upload_audio(audio: UploadFile = File(...)):
    # Save the uploaded file locally
    filepath = os.path.join(UPLOAD_FOLDER, 'recording.wav')
    with open(filepath, 'wb') as buffer:
        buffer.write(await audio.read())
    
    # Send the file to the Colab server for transcription
    with open(filepath, 'rb') as f:
        files = {'file': (filepath, f, 'audio/mpeg')}
        response = requests.post(COLAB_URL, files=files)
        
        # Check if the transcription was successful
        if response.status_code == 200:
            data = response.json()
            transcription = data.get('transcription', '')
            
            # Save the transcription to a local file
            transcription_file = os.path.join(UPLOAD_FOLDER, "transcription.txt")
            with open(transcription_file, "w", encoding='utf-8') as txt_file:
                txt_file.write(transcription)
            
            return {
                "message": "File uploaded and transcribed successfully",
                "transcription": transcription
            }
        else:
            return {"message": f"Error {response.status_code}: {response.text}"}
