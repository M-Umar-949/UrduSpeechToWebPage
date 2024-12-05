import React, { useState, useRef } from 'react';
import axios from 'axios';
import { Mic, Square, Play, Pause, Upload, Loader } from 'lucide-react'; // Import Loader icon

const RecordPage = () => {
  const [recordingStarted, setRecordingStarted] = useState(false);
  const [audioUrl, setAudioUrl] = useState(null); // Stores the last recorded audio
  const [submitted, setSubmitted] = useState(false);
  const [generatedWebpage, setGeneratedWebpage] = useState('');
  const [isPlaying, setIsPlaying] = useState(false);
  const [uploadStatus, setUploadStatus] = useState('');
  const [isLoading, setIsLoading] = useState(false); // State to track loading status
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const audioRef = useRef(null); // Ref for the audio element
  const [audioBlob, setAudioBlob] = useState(null);

  const startRecording = () => {
    navigator.mediaDevices.getUserMedia({ audio: true })
      .then((stream) => {
        const mediaRecorder = new MediaRecorder(stream);
        mediaRecorderRef.current = mediaRecorder;
        audioChunksRef.current = [];

        mediaRecorder.addEventListener('dataavailable', (event) => {
          audioChunksRef.current.push(event.data);
        });

        mediaRecorder.addEventListener('stop', () => {
          const blob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
          const audioUrl = URL.createObjectURL(blob);
          setAudioUrl(audioUrl); // Store the last recorded audio
          setAudioBlob(blob);

          // Reset to default generated page and show loading spinner
          setGeneratedWebpage(``);
          setIsLoading(true); // Start loading
          setSubmitted(true);

          // Stop the media stream tracks
          stream.getTracks().forEach((track) => track.stop());
        });

        mediaRecorder.start();
        setRecordingStarted(true);
      })
      .catch((error) => {
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
      if (isPlaying) {
        audioRef.current.pause(); // Pause audio
        setIsPlaying(false);
      } else {
        audioRef.current.play(); // Play audio
        setIsPlaying(true);
      }
    }
  };

  const handleAudioEnd = () => {
    setIsPlaying(false); // Revert to Play button when audio ends
  };

  const uploadAudio = async () => {
    if (!audioBlob) return;

    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.wav');

    try {
      setUploadStatus('Uploading...');
      setIsLoading(true); // Show loading spinner
      const response = await axios.post('http://localhost:8000/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      // Check if HTML content is in the response
      if (response.data.html_content) {
        setGeneratedWebpage(response.data.html_content);
        setUploadStatus('Upload and generation successful!');
      } else {
        setUploadStatus('Generation failed');
      }
    } catch (error) {
      setUploadStatus('Upload failed');
      console.error('Upload error:', error);
    } finally {
      setIsLoading(false); // Hide loading spinner
    }
  };

  return (
    <div className="min-h-screen text-white flex">
      <div
        className={`${
          submitted ? 'w-1/2' : 'w-full'
        } bg-gradient-to-br from-black to-purple-950 flex flex-col items-center justify-center p-6 transition-all duration-700`}
      >
        <div className="flex flex-col items-center justify-center space-y-4">
          {/* Microphone Button */}
          {!recordingStarted ? (
            <>
              <button
                onClick={startRecording}
                className="bg-purple-700 hover:bg-purple-600 text-white p-4 rounded-full transition-all duration-300 transform hover:scale-110"
              >
                <Mic size={64} />
              </button>
              <p className="text-gray-300 font-mono text-lg">
                Click the microphone to start recording <br />
                <span className="text-xl font-noto-sans">مایک پر کلک کریں ریکارڈنگ شروع کرنے کے لیے</span>
              </p>
            </>
          ) : (
            <>
              <button
                onClick={stopRecording}
                className="bg-red-600 hover:bg-red-500 text-white p-4 rounded-full transition-all duration-300 transform hover:scale-110 relative"
              >
                <Mic size={64} className="animate-pulse" />
                <div className="absolute top-0 left-0 w-full h-full border-4 border-red-500 rounded-full animate-ping"></div>
              </button>
              <p className="text-red-400 font-mono text-lg">
                Recording in progress... <br />
                <span className="text-xl font-noto-sans">ریکارڈنگ جاری ہے...</span>
              </p>
            </>
          )}

          {/* Playback and Upload Buttons */}
          {audioUrl && (
            <div className="flex flex-col items-center space-y-4">
              <div className="flex items-center space-x-6">
                {/* Play Button */}
                <button
                  onClick={togglePlayPause}
                  className="bg-purple-700 hover:bg-purple-600 text-white px-6 py-4 rounded-full transition-all duration-300 shadow-md flex flex-col items-center justify-center w-32"
                >
                  {isPlaying ? <Pause size={32} /> : <Play size={32} />}
                  <span className="mt-2 text-base font-medium">
                    Play <br />
                    <span className="text-sm font-noto-sans">پلے</span>
                  </span>
                </button>

                {/* Upload Button */}
                <button
                  onClick={uploadAudio}
                  className="bg-purple-700 hover:bg-purple-600 text-white px-6 py-4 rounded-full transition-all duration-300 shadow-md flex flex-col items-center justify-center w-32"
                >
                  <Upload size={32} />
                  <span className="mt-2 text-base font-medium">
                    Upload <br />
                    <span className="text-sm font-noto-sans">اپ لوڈ</span>
                  </span>
                </button>
              </div>
              <audio
                ref={audioRef}
                src={audioUrl}
                onEnded={handleAudioEnd} // Reset Play button after audio ends
              />
            </div>
          )}

          {/* Status Message */}
          {uploadStatus && (
            <div className="text-sm text-white mt-4">{uploadStatus}</div>
          )}
        </div>
      </div>

      {/* Webpage Display Section */}
      {submitted && (
        <div className="w-1/2 bg-white overflow-auto h-screen">
          {isLoading ? (
            // Show loading spinner if webpage is being generated
            <div className="flex items-center justify-center h-full">
              <Loader size={64} className="animate-spin text-purple-700" />
              <h1 className="ml-4 text-xl font-bold text-purple-700">
                Generating webpage... <br />
                <span className="text-xl font-noto-sans">ویب صفحہ تیار ہو رہا ہے...</span>
              </h1>
            </div>
          ) : (
            <iframe
              srcDoc={generatedWebpage}
              className="w-full h-full"
              title="Generated Webpage"
            />
          )}
        </div>
      )}
    </div>
  );
};

export default RecordPage;
