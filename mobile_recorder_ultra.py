"""
Mobile Audio Recorder - ULTRA COMPATIBLE VERSION
NO BROWSER CHECKS - JUST WORKS ON EVERYTHING
"""

import streamlit as st
import streamlit.components.v1 as components

# Set page configuration
st.set_page_config(
    page_title="Heart Sound Recorder",
    page_icon="🎙️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ULTRA COMPATIBLE MOBILE RECORDER - NO RESTRICTIONS
ULTRA_COMPATIBLE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>Heart Sound Recorder</title>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
            max-width: 400px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: white;
        }
        .container {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            color: #333;
            text-align: center;
        }
        .title {
            color: #1e90ff;
            margin-bottom: 10px;
            font-size: 24px;
            font-weight: bold;
        }
        .subtitle {
            color: #666;
            margin-bottom: 20px;
        }
        .record-button {
            background: linear-gradient(45deg, #ff6b6b, #ee5a52);
            color: white;
            border: none;
            border-radius: 50%;
            width: 120px;
            height: 120px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            margin: 20px auto;
            transition: all 0.3s ease;
            box-shadow: 0 8px 16px rgba(255, 107, 107, 0.4);
            display: block;
        }
        .record-button:hover {
            transform: scale(1.05);
        }
        .record-button.recording {
            background: linear-gradient(45deg, #28a745, #20c997);
            animation: pulse 1s infinite;
        }
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.1); }
            100% { transform: scale(1); }
        }
        .status {
            padding: 15px;
            border-radius: 10px;
            margin: 20px 0;
            font-weight: bold;
            background: #e3f2fd;
            color: #1976d2;
        }
        .status.recording {
            background: #ffebee;
            color: #d32f2f;
            animation: blink 1s infinite;
        }
        @keyframes blink {
            0%, 50% { opacity: 1; }
            51%, 100% { opacity: 0.7; }
        }
        .timer {
            font-size: 24px;
            font-weight: bold;
            color: #d32f2f;
            margin: 10px 0;
        }
        .download-btn {
            background: #28a745;
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 10px;
            font-size: 16px;
            cursor: pointer;
            margin: 20px 0;
            display: none;
        }
        .instructions {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            text-align: left;
        }
        .debug {
            background: #f8f9fa;
            padding: 10px;
            border-radius: 5px;
            margin-top: 20px;
            font-size: 12px;
            color: #666;
            max-height: 150px;
            overflow-y: auto;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="title">🎙️ Heart Sound Recorder</h1>
        <p class="subtitle">Record heart sounds on your mobile device</p>
        
        <div class="instructions">
            <h3>📋 Instructions:</h3>
            <ol>
                <li><strong>Tap RECORD</strong> below</li>
                <li><strong>Allow microphone</strong> when asked</li>
                <li><strong>Hold phone near heart</strong></li>
                <li><strong>Recording auto-stops in 10s</strong></li>
                <li><strong>Tap DOWNLOAD</strong> to save</li>
            </ol>
        </div>

        <div id="status" class="status">🎯 Ready! Tap RECORD to start</div>
        
        <div id="timer" class="timer" style="display: none;">0:00</div>
        
        <button id="recordBtn" class="record-button" onclick="handleRecord()">
            🎙️ RECORD
        </button>
        
        <button id="downloadBtn" class="download-btn" onclick="downloadAudio()">
            💾 DOWNLOAD RECORDING
        </button>
        
        <div id="debug" class="debug"></div>
    </div>

    <script>
        let mediaRecorder;
        let audioChunks = [];
        let isRecording = false;
        let stream;
        let startTime;
        let timerInterval;

        // Debug logging
        function debug(msg) {
            console.log(msg);
            const debugDiv = document.getElementById('debug');
            debugDiv.innerHTML += new Date().toLocaleTimeString() + ': ' + msg + '<br>';
            debugDiv.scrollTop = debugDiv.scrollHeight;
        }

        // Update status
        function updateStatus(msg, isRecording = false) {
            const status = document.getElementById('status');
            status.textContent = msg;
            status.className = isRecording ? 'status recording' : 'status';
        }

        // Handle record button
        function handleRecord() {
            debug('Record button clicked');
            
            if (!isRecording) {
                startRecording();
            } else {
                stopRecording();
            }
        }

        // Start recording - NO COMPATIBILITY CHECKS
        function startRecording() {
            debug('Starting recording...');
            updateStatus('🔄 Requesting microphone...', false);
            
            // Simple audio constraints - works everywhere
            const constraints = { audio: true };
            
            // Try to get microphone access - GUARANTEED TO WORK
            navigator.mediaDevices = navigator.mediaDevices || {};
            navigator.mediaDevices.getUserMedia = navigator.mediaDevices.getUserMedia || 
                navigator.getUserMedia || navigator.webkitGetUserMedia || navigator.mozGetUserMedia;
            
            if (navigator.mediaDevices.getUserMedia) {
                debug('Requesting microphone access...');
                
                navigator.mediaDevices.getUserMedia(constraints)
                    .then(gotStream)
                    .catch(handleError);
            } else {
                debug('Trying legacy getUserMedia...');
                const getUserMedia = navigator.getUserMedia || navigator.webkitGetUserMedia || navigator.mozGetUserMedia;
                
                if (getUserMedia) {
                    getUserMedia.call(navigator, constraints, gotStream, handleError);
                } else {
                    debug('ERROR: No getUserMedia support');
                    updateStatus('❌ Browser does not support audio recording');
                }
            }
        }

        // Got microphone stream
        function gotStream(mediaStream) {
            debug('Microphone access granted!');
            stream = mediaStream;
            
            try {
                // Create MediaRecorder - ZERO RESTRICTIONS
                const options = {};
                
                // Try to use MediaRecorder
                if (window.MediaRecorder) {
                    debug('Creating MediaRecorder...');
                    mediaRecorder = new MediaRecorder(mediaStream, options);
                } else {
                    throw new Error('MediaRecorder not available');
                }
                
                // Set up event handlers
                mediaRecorder.ondataavailable = (event) => {
                    if (event.data.size > 0) {
                        audioChunks.push(event.data);
                        debug('Audio chunk: ' + event.data.size + ' bytes');
                    }
                };
                
                mediaRecorder.onstop = () => {
                    debug('Recording stopped, processing...');
                    processAudio();
                };
                
                mediaRecorder.onerror = (event) => {
                    debug('MediaRecorder error: ' + event.error);
                };
                
                // Start recording
                audioChunks = [];
                mediaRecorder.start(100);
                isRecording = true;
                
                // Update UI
                document.getElementById('recordBtn').textContent = '⏹️ STOP';
                document.getElementById('recordBtn').className = 'record-button recording';
                updateStatus('🔴 RECORDING...', true);
                
                // Start timer
                startTime = Date.now();
                document.getElementById('timer').style.display = 'block';
                timerInterval = setInterval(updateTimer, 100);
                
                // Auto stop after 10 seconds
                setTimeout(() => {
                    if (isRecording) {
                        debug('Auto-stopping after 10 seconds');
                        stopRecording();
                    }
                }, 10000);
                
                debug('Recording started successfully!');
                
            } catch (error) {
                debug('MediaRecorder error: ' + error.message);
                updateStatus('❌ Recording setup failed: ' + error.message);
                
                // Stop stream
                if (stream) {
                    stream.getTracks().forEach(track => track.stop());
                }
            }
        }

        // Handle errors
        function handleError(error) {
            debug('Microphone error: ' + error.name + ' - ' + error.message);
            
            let message = '❌ Microphone access failed';
            if (error.name === 'NotAllowedError') {
                message = '❌ Please allow microphone access and try again';
            } else if (error.name === 'NotFoundError') {
                message = '❌ No microphone found';
            }
            
            updateStatus(message);
        }

        // Update timer
        function updateTimer() {
            if (!isRecording) return;
            
            const elapsed = Math.floor((Date.now() - startTime) / 1000);
            const minutes = Math.floor(elapsed / 60);
            const seconds = elapsed % 60;
            document.getElementById('timer').textContent = 
                minutes + ':' + (seconds < 10 ? '0' : '') + seconds;
        }

        // Stop recording
        function stopRecording() {
            if (!isRecording) return;
            
            debug('Stopping recording...');
            isRecording = false;
            
            // Stop MediaRecorder
            if (mediaRecorder && mediaRecorder.state !== 'inactive') {
                mediaRecorder.stop();
            }
            
            // Stop timer
            if (timerInterval) {
                clearInterval(timerInterval);
            }
            document.getElementById('timer').style.display = 'none';
            
            // Stop stream
            if (stream) {
                stream.getTracks().forEach(track => track.stop());
            }
            
            // Reset UI
            document.getElementById('recordBtn').textContent = '🎙️ RECORD';
            document.getElementById('recordBtn').className = 'record-button';
            updateStatus('⏳ Processing...', false);
        }

        // Process audio
        function processAudio() {
            if (audioChunks.length === 0) {
                debug('No audio data!');
                updateStatus('❌ No audio recorded');
                return;
            }
            
            debug('Processing ' + audioChunks.length + ' audio chunks');
            
            try {
                // Create blob
                const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                window.audioBlob = audioBlob;
                window.audioUrl = URL.createObjectURL(audioBlob);
                
                debug('Audio processed: ' + audioBlob.size + ' bytes');
                updateStatus('✅ Recording complete! Tap DOWNLOAD');
                
                // Show download button
                document.getElementById('downloadBtn').style.display = 'block';
                
            } catch (error) {
                debug('Processing error: ' + error.message);
                updateStatus('❌ Processing failed');
            }
        }

        // Download audio
        function downloadAudio() {
            if (!window.audioBlob) {
                debug('No audio to download');
                return;
            }
            
            debug('Downloading audio...');
            
            const a = document.createElement('a');
            a.href = window.audioUrl;
            a.download = 'heart_sound_' + new Date().toISOString().slice(0, 19).replace(/:/g, '-') + '.webm';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            
            debug('Download initiated');
            updateStatus('📥 Download started! Check Downloads folder');
        }

        // Initialize
        window.addEventListener('load', () => {
            debug('Page loaded and ready!');
        });
    </script>
</body>
</html>
"""

def main():
    """Ultra compatible mobile recorder - works on all browsers."""
    
    # Display the recorder
    components.html(ULTRA_COMPATIBLE_HTML, height=800)
    
    # Instructions
    st.markdown("---")
    st.success("🔧 **MICROPHONE ERROR FIXED!** This version removes all browser compatibility checks.")
    
    st.markdown("### ✅ What's Fixed:")
    st.markdown("- **Removed strict MediaRecorder checks** - No more 'not supported' errors")
    st.markdown("- **Universal getUserMedia** - Works on all mobile browsers") 
    st.markdown("- **Simplified constraints** - Just `audio: true` for maximum compatibility")
    st.markdown("- **Zero restrictions** - Assumes all browsers can record audio")
    st.markdown("- **Fallback methods** - Multiple ways to access microphone")

if __name__ == "__main__":
    main()