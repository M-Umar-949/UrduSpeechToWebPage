import React, { useState, useRef } from 'react';
import axios from 'axios';
import { Mic, Square, Play, Pause, Upload } from 'lucide-react';

const RecordPage = () => {
  const [recordingStarted, setRecordingStarted] = useState(false);
  const [audioUrl, setAudioUrl] = useState(null);
  const [submitted, setSubmitted] = useState(false);
  const [generatedWebpage, setGeneratedWebpage] = useState('');
  const [isPlaying, setIsPlaying] = useState(false);
  const [audioPaused, setAudioPaused] = useState(false);
  const [uploadStatus, setUploadStatus] = useState('');
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const audioRef = useRef(null);
  const [audioBlob, setAudioBlob] = useState(null);

  const startRecording = () => {
    navigator.mediaDevices.getUserMedia({ audio: true })
      .then(stream => {
        const mediaRecorder = new MediaRecorder(stream);
        mediaRecorderRef.current = mediaRecorder;
        audioChunksRef.current = [];

        mediaRecorder.addEventListener("dataavailable", event => {
          audioChunksRef.current.push(event.data);
        });

        mediaRecorder.addEventListener("stop", () => {
          const blob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
          const audioUrl = URL.createObjectURL(blob);
          setAudioUrl(audioUrl);
          setAudioBlob(blob);
          
          setGeneratedWebpage(`
            <!DOCTYPE html>
            <html lang="en">
            <head>
              <meta charset="UTF-8">
              <title>Generated Webpage</title>
              <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
                h1 { color: #333; }
                p { line-height: 1.6; }
              </style>
            </head>
            <body>
              <h1>Welcome to My Generated Webpage</h1>
            </body>
            </html>
          `);
          setSubmitted(true);

          // Stop the media stream tracks
          stream.getTracks().forEach(track => track.stop());
        });

        mediaRecorder.start();
        setRecordingStarted(true);
      })
      .catch(error => {
        console.error('Microphone access error:', error);
      });
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      setRecordingStarted(false);
    }
  };

  const togglePlayPause = () => {
    if (audioRef.current) {
      if (audioPaused) {
        audioRef.current.play();
        setAudioPaused(false);
        setIsPlaying(true);
      } else {
        audioRef.current.pause();
        setAudioPaused(true);
        setIsPlaying(false);
      }
    }
  };

  const uploadAudio = async () => {
    if (!audioBlob) return;

    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.wav');

    try {
      setUploadStatus('Uploading...');
      const response = await axios.post('http://localhost:8000/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      setUploadStatus('Upload successful!');
      console.log(response.data);
    } catch (error) {
      setUploadStatus('Upload failed');
      console.error('Upload error:', error);
    }
  };

  return (
    <div className="min-h-screen text-white flex">
      <div className={`${submitted ? 'w-1/2' : 'w-full'} bg-gradient-to-br from-black to-purple-950 flex flex-col items-center justify-center p-6 transition-all duration-700`}>
        <div className="flex flex-col items-center justify-center space-y-4">
          {!recordingStarted ? (
            <button
              onClick={startRecording}
              className="bg-purple-700 hover:bg-purple-600 text-white p-4 rounded-full transition-all duration-300 transform hover:scale-110"
            >
              <Mic size={64} />
            </button>
          ) : (
            <button
              onClick={stopRecording}
              className="bg-red-600 hover:bg-red-500 text-white p-4 rounded-full transition-all duration-300 transform hover:scale-110"
            >
              <Square size={64} />
            </button>
          )}

          {audioUrl && (
            <div className="flex items-center space-x-2 bg-purple-800 p-3 rounded-full">
              <audio ref={audioRef} src={audioUrl} />
              <button 
                onClick={togglePlayPause}
                className="text-white"
              >
                {isPlaying ? <Pause size={32} /> : <Play size={32} />}
              </button>
              <button 
                onClick={uploadAudio}
                className="text-white"
              >
                <Upload size={32} />
              </button>
            </div>
          )}

          {uploadStatus && (
            <div className="text-sm text-white">
              {uploadStatus}
            </div>
          )}
        </div>
      </div>

      {submitted && (
        <div className="w-1/2 bg-white overflow-auto h-screen">
          <iframe 
            srcDoc={generatedWebpage} 
            className="w-full h-full"
            title="Generated Webpage"
          />
        </div>
      )}
    </div>
  );
};

export default RecordPage;