import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { Mic, Square, Play, Pause, Upload, Loader, RefreshCw } from 'lucide-react';

const RecordPage = () => {
  // State variables
  const [recordingStatus, setRecordingStatus] = useState('idle'); // 'idle', 'recording', 'recorded'
  const [audioUrl, setAudioUrl] = useState(null);
  const [audioBlob, setAudioBlob] = useState(null);
  const [recordingDuration, setRecordingDuration] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [uploadStatus, setUploadStatus] = useState('');
  const [generatedWebpage, setGeneratedWebpage] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  // Refs
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const audioRef = useRef(null);
  const recordingTimerRef = useRef(null);
  const streamRef = useRef(null);

  // Maximum recording duration (60 seconds)
  const MAX_RECORDING_DURATION = 60;

  // Start recording
  const startRecording = async () => {
    try {
      // Reset previous state
      audioChunksRef.current = [];
      setUploadStatus('');
      setGeneratedWebpage('');

      // Request microphone access
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;

      // Create media recorder
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;

      // Event listeners
      mediaRecorder.addEventListener('dataavailable', (event) => {
        audioChunksRef.current.push(event.data);
      });

      mediaRecorder.addEventListener('stop', handleRecordingStop);

      // Start recording and timer
      mediaRecorder.start();
      setRecordingStatus('recording');
      setRecordingDuration(0);

      // Start duration tracking
      recordingTimerRef.current = setInterval(() => {
        setRecordingDuration(prev => {
          if (prev >= MAX_RECORDING_DURATION) {
            stopRecording();
            return MAX_RECORDING_DURATION;
          }
          return prev + 1;
        });
      }, 1000);

    } catch (error) {
      console.error('Microphone access error:', error);
      setUploadStatus('Microphone access failed');
    }
  };

  // Stop recording
  const stopRecording = () => {
    if (mediaRecorderRef.current && recordingStatus === 'recording') {
      mediaRecorderRef.current.stop();
      clearInterval(recordingTimerRef.current);
      
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
    }
  };

  // Handle recording stop
  const handleRecordingStop = () => {
    // Create audio blob and URL
    const blob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
    const url = URL.createObjectURL(blob);

    // Update state
    setAudioBlob(blob);
    setAudioUrl(url);
    setRecordingStatus('recorded');
    
    // Reset recording timer
    clearInterval(recordingTimerRef.current);
    setRecordingDuration(0);
  };

  // Toggle play/pause
  const togglePlayPause = async () => {
    if (!audioRef.current) return;

    try {
      if (isPlaying) {
        await audioRef.current.pause();
        setIsPlaying(false);
      } else {
        await audioRef.current.play();
        setIsPlaying(true);
      }
    } catch (error) {
      console.error('Playback error:', error);
      setIsPlaying(false);
    }
  };

  // Handle audio end
  const handleAudioEnd = () => {
    setIsPlaying(false);
  };

  // Upload audio
  const uploadAudio = async () => {
    if (!audioBlob) {
      setUploadStatus('No audio to upload');
      return;
    }

    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.wav');

    try {
      setUploadStatus('Uploading...');
      setIsLoading(true);

      const response = await axios.post('http://localhost:8000/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      if (response.data.html_content) {
        setGeneratedWebpage(response.data.html_content);
        setUploadStatus('Upload successful!');
      } else {
        setUploadStatus('Generation failed');
      }
    } catch (error) {
      console.error('Upload error:', error);
      setUploadStatus('Upload failed');
    } finally {
      setIsLoading(false);
    }
  };

  // Reset recording
  const resetRecording = () => {
    // Clear all recording-related states
    setRecordingStatus('idle');
    setAudioUrl(null);
    setAudioBlob(null);
    setRecordingDuration(0);
    setIsPlaying(false);
    setUploadStatus('');
    setGeneratedWebpage('');
  };

  return (
    <div className="min-h-screen text-white flex">
      <div className={`${generatedWebpage ? 'w-1/2' : 'w-full'} bg-gradient-to-br from-black to-purple-950 flex flex-col items-center justify-center p-6 transition-all duration-700`}>
        <div className="flex flex-col items-center justify-center space-y-4">
          {/* Recording Progress Indicator */}
          {recordingStatus === 'recording' && (
            <div className="w-full bg-red-200 h-2 rounded-full overflow-hidden mb-4">
              <div 
                className="bg-red-600 h-full" 
                style={{width: `${(recordingDuration / MAX_RECORDING_DURATION) * 100}%`}}
              />
            </div>
          )}

          {/* Recording Controls */}
          {recordingStatus === 'idle' && (
            <button
              onClick={startRecording}
              className="bg-purple-700 hover:bg-purple-600 text-white p-4 rounded-full transition-all duration-300 transform hover:scale-110"
            >
              <Mic size={64} />
            </button>
          )}

          {recordingStatus === 'recording' && (
            <button
              onClick={stopRecording}
              className="bg-red-600 hover:bg-red-500 text-white p-4 rounded-full transition-all duration-300 transform hover:scale-110 relative"
            >
              <Square size={64} className="animate-pulse" />
              <div className="absolute top-0 left-0 w-full h-full border-4 border-red-500 rounded-full animate-ping"></div>
            </button>
          )}

          {/* Playback and Upload Controls */}
          {recordingStatus === 'recorded' && (
            <div className="flex flex-col items-center space-y-4">
              <div className="flex items-center space-x-6">
                {/* Play/Pause Button */}
                <button
                  onClick={togglePlayPause}
                  className="bg-purple-700 hover:bg-purple-600 text-white px-6 py-4 rounded-full transition-all duration-300 shadow-md flex flex-col items-center justify-center w-32"
                >
                  {isPlaying ? <Pause size={32} /> : <Play size={32} />}
                  <span className="mt-2 text-base font-medium">
                    {isPlaying ? 'Pause' : 'Play'}
                  </span>
                </button>

                {/* Upload Button */}
                <button
                  onClick={uploadAudio}
                  className="bg-purple-700 hover:bg-purple-600 text-white px-6 py-4 rounded-full transition-all duration-300 shadow-md flex flex-col items-center justify-center w-32"
                >
                  <Upload size={32} />
                  <span className="mt-2 text-base font-medium">Upload</span>
                </button>

                {/* Reset Button */}
                <button
                  onClick={resetRecording}
                  className="bg-gray-600 hover:bg-gray-500 text-white px-6 py-4 rounded-full transition-all duration-300 shadow-md flex flex-col items-center justify-center w-32"
                >
                  <RefreshCw size={32} />
                  <span className="mt-2 text-base font-medium">Reset</span>
                </button>
              </div>

              {/* Hidden Audio Element */}
              <audio
                ref={audioRef}
                src={audioUrl}
                onEnded={handleAudioEnd}
              />
            </div>
          )}

          {/* Status Message */}
          {uploadStatus && (
            <div className={`text-sm mt-4 ${
              uploadStatus.includes('failed') ? 'text-red-500' : 'text-green-500'
            }`}>
              {uploadStatus}
            </div>
          )}
        </div>
      </div>

      {/* Webpage Display Section */}
      {generatedWebpage && (
        <div className="w-1/2 bg-white overflow-auto h-screen">
          {isLoading ? (
            <div className="flex items-center justify-center h-full">
              <Loader size={64} className="animate-spin text-purple-700" />
              <h1 className="ml-4 text-xl font-bold text-purple-700">
                Generating webpage...
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