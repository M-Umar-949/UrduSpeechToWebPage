import os
import logging
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
import threading 
file_lock = threading.Lock()
import aiofiles

# Import the HTMLGenerator from the separate module
from generator import HTMLGenerator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# FastAPI Application
app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Specify the frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global HTML Generator
html_generator = HTMLGenerator()

# Colab server URL for transcription
COLAB_URL = os.getenv("COLAB_TRANSCRIPTION_URL", "https://your-default-ngrok-url.ngrok-free.app/transcribe")

@app.post("/upload")
async def upload_audio(audio: UploadFile = File(...)):
    try:
        if not audio.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        allowed_extensions = ['.wav', '.mp3', '.ogg']
        if not any(audio.filename.lower().endswith(ext) for ext in allowed_extensions):
            raise HTTPException(status_code=400, detail="Only WAV, MP3, and OGG files are supported")

        filepath = os.path.join(html_generator.upload_folder, 'recording.wav')
        
        async with aiofiles.open(filepath, 'wb') as buffer:
            await buffer.write(await audio.read())
        
        logger.info(f"File saved locally: {filepath}")

        with file_lock:
            with open(filepath, 'rb') as f:
                files = {'file': ('recording.wav', f, 'audio/wav')}
                response = requests.post(COLAB_URL, files=files, timeout=30)

                if response.status_code == 200:
                    data = response.json()
                    transcription = data.get('transcription', '')
                    transcription=transcription+".The code should be in json html key"
                    transcription_file = os.path.join(html_generator.upload_folder, "transcription.txt")
                    with open(transcription_file, "w", encoding='utf-8') as txt_file:
                        txt_file.write(transcription)

                    html_output = html_generator.generate_html_from_transcription(transcription)
                    return JSONResponse({
                        "message": "File uploaded, transcribed, and HTML generated successfully",
                        "transcription": transcription,
                        "html_content": html_output
                    })
                else:
                    raise HTTPException(status_code=response.status_code, detail=response.text)
    except Exception as e:
        logger.error(f"Error during upload: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()