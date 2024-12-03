import os
import sounddevice as sd
import scipy.io.wavfile as wav
from pydub import AudioSegment
import requests
import threading
import time

# Endpoint URL from ngrok (replace with your URL)
FASTAPI_ENDPOINT = "https://0be7-34-143-195-15.ngrok-free.app/transcribe"

RECORDING_FILE_WAV = "recording.wav"
RECORDING_FILE_MP3 = "recording.mp3"
is_recording = False
recording_thread = None

def record_audio(duration=10, samplerate=44100):
    """Record audio from the microphone."""
    global is_recording
    print("Recording started...")
    is_recording = True
    recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
    sd.wait()
    wav.write(RECORDING_FILE_WAV, samplerate, recording)
    print("Recording stopped.")
    is_recording = False

def convert_wav_to_mp3():
    """Convert the WAV file to MP3 format."""
    try:
        audio = AudioSegment.from_wav(RECORDING_FILE_WAV)
        audio.export(RECORDING_FILE_MP3, format="mp3")
        print(f"Audio converted to MP3 format: {RECORDING_FILE_MP3}")
        return RECORDING_FILE_MP3
    except Exception as e:
        print(f"Conversion error: {e}")
        return None

def send_audio_for_transcription(file_path):
    """Send the recorded audio to the FastAPI transcription endpoint."""
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (file_path, f, 'audio/mpeg')}
            response = requests.post(FASTAPI_ENDPOINT, files=files)
            
            if response.status_code == 200:
                data = response.json()
                transcription = data.get('transcription', '')
                print("\nTranscription Received:\n", transcription)

                # Save transcription to a file
                with open("transcription.txt", "w", encoding="utf-8") as txt_file:
                    txt_file.write(transcription)
                print("Transcription saved to 'transcription.txt'.")
            else:
                print(f"Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"Error sending audio: {e}")

def start_recording():
    """Start audio recording in a separate thread."""
    global recording_thread
    recording_thread = threading.Thread(target=record_audio)
    recording_thread.start()

def stop_recording_and_transcribe():
    """Stop recording, convert audio to MP3, and send for transcription."""
    global is_recording, recording_thread
    
    if is_recording:
        print("Recording in progress. Waiting to complete...")
        recording_thread.join()
    
    converted_file = convert_wav_to_mp3()
    if converted_file:
        send_audio_for_transcription(converted_file)

if __name__ == "__main__":
    print("Press 's' to start recording and 'e' to stop and transcribe.")

    while True:
        user_input = input("Enter command: ").strip().lower()
        if user_input == 's':
            if is_recording:
                print("Recording is already in progress.")
            else:
                start_recording()
        elif user_input == 'e':
            stop_recording_and_transcribe()
        elif user_input == 'q':
            print("Exiting...")
            break
        else:
            print("Invalid input. Press 's' to start, 'e' to stop, or 'q' to quit.")
