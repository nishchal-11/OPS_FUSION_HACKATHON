"""
Mobile Audio Recorder - FORCE MICROPHONE VERSION
Absolutely no browser checks - just immediately requests microphone permission.
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

# ABSOLUTELY MINIMAL JavaScript - FORCE MICROPHONE IMMEDIATELY
FORCE_MICROPHONE_HTML = """
<div style="max-width: 400px; margin: 0 auto; padding: 20px; font-family: Arial, sans-serif;">
    <h1 style="text-align: center; color: #1e90ff;">🎙️ Heart Sound Recorder</h1>
    <p style="text-align: center; color: #666;">Click RECORD to start - microphone permission will be requested</p>

    <div style="background: #e3f2fd; padding: 15px; border-radius: 10px; margin: 20px 0;">
        <h4>📋 Quick Steps:</h4>
        <ol>
            <li><strong>Click RECORD button</strong></li>
            <li><strong>Allow microphone</strong> when browser asks</li>
            <li><strong>Record 5-10 seconds</strong></li>
            <li><strong>Click STOP</strong></li>
            <li><strong>Download your recording</strong></li>
        </ol>
    </div>

    <div id="status" style="text-align: center; font-size: 18px; font-weight: bold; margin: 20px 0; padding: 15px; border-radius: 10px; background: #f8f9fa;">
        🎯 Ready! Tap RECORD to start
    </div>

    <div id="recordingTimer" style="display: none; text-align: center; margin: 15px 0;">
        <div style="background: #ff4444; color: white; padding: 10px 20px; border-radius: 25px; display: inline-block; font-weight: bold; font-size: 18px; animation: pulse 1s infinite;">
            🔴 RECORDING: <span id="timerText">0:00</span>
        </div>
    </div>

    <div style="text-align: center; margin: 30px 0;">
        <button id="recordButton" onclick="handleRecord()" 
                style="background-color: #ff4444; color: white; border: none; border-radius: 50%; width: 140px; height: 140px; font-size: 18px; font-weight: bold; cursor: pointer; box-shadow: 0 4px 8px rgba(0,0,0,0.2); transition: all 0.3s ease;">
            🎙️ RECORD
        </button>
    </div>

    <div id="levelIndicator" style="display: none; text-align: center; margin: 20px 0;">
        <p style="margin: 5px 0; font-weight: bold; color: #333;">📊 Audio Level:</p>
        <div style="background: #e0e0e0; border-radius: 10px; height: 25px; width: 90%; margin: 10px auto; position: relative;">
            <div id="levelBar" style="background: linear-gradient(90deg, #28a745, #ffc107, #dc3545); height: 100%; border-radius: 10px; width: 0%; transition: width 0.1s ease;"></div>
        </div>
    </div>

    <div id="controls" style="text-align: center; margin: 20px 0; display: none;">
        <button onclick="downloadRecording()" 
                style="background: #28a745; color: white; border: none; padding: 15px 30px; border-radius: 10px; font-size: 16px; margin: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.2);">
            💾 DOWNLOAD RECORDING
        </button>
    </div>

    <div id="debugInfo" style="text-align: center; color: #666; font-size: 11px; margin-top: 20px; padding: 10px; background: #f8f9fa; border-radius: 5px;"></div>
</div>

<style>
@keyframes pulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.1); }
    100% { transform: scale(1); }
}
.recording {
    background-color: #28a745 !important;
    animation: pulse 1s infinite;
}
</style>

<script>
let mediaRecorder;
let audioChunks = [];
let isRecording = false;
let mediaStream;
let recordingStartTime;
let timerInterval;
let audioContext;
let analyser;
let animationId;

function log(message) {
    console.log(message);
    const debugDiv = document.getElementById('debugInfo');
    if (debugDiv) {
        debugDiv.innerHTML += new Date().toLocaleTimeString() + ': ' + message + '<br>';
        debugDiv.scrollTop = debugDiv.scrollHeight;
    }
}

function updateStatus(message, color) {
    const status = document.getElementById('status');
    if (status) {
        status.innerHTML = message;
        status.style.color = color || '#333';
    }
}

// FORCE MICROPHONE REQUEST - NO CHECKS AT ALL
function handleRecord() {
    if (isRecording) {
        stopRecording();
        return;
    }

    log('🎙️ FORCING microphone request...');
    updateStatus('🔄 Requesting microphone access...', '#ffa500');
    
    // IMMEDIATE microphone request with basic constraints
    const constraints = { audio: true };
    
    // Try ALL possible methods simultaneously
    requestMicrophone(constraints);
}

function requestMicrophone(constraints) {
    log('📱 Attempting microphone access...');
    
    // Method 1: Modern API
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        log('✅ Trying modern mediaDevices API');
        navigator.mediaDevices.getUserMedia(constraints)
            .then(handleMicrophoneSuccess)
            .catch(error => {
                log('❌ Modern API failed: ' + error.message);
                tryLegacyAPI(constraints);
            });
        return;
    }
    
    // Method 2: Legacy APIs
    tryLegacyAPI(constraints);
}

function tryLegacyAPI(constraints) {
    log('⚠️ Trying legacy APIs...');
    
    const getUserMedia = navigator.getUserMedia || 
                        navigator.webkitGetUserMedia || 
                        navigator.mozGetUserMedia;
    
    if (getUserMedia) {
        log('✅ Found legacy getUserMedia');
        getUserMedia.call(navigator, constraints, 
            handleMicrophoneSuccess, 
            handleMicrophoneError
        );
    } else {
        log('❌ No getUserMedia found');
        handleMicrophoneError(new Error('No microphone API available'));
    }
}

function handleMicrophoneSuccess(stream) {
    log('✅ MICROPHONE ACCESS GRANTED!');
    mediaStream = stream;
    
    try {
        // Create MediaRecorder
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];
        
        mediaRecorder.ondataavailable = event => {
            if (event.data.size > 0) {
                audioChunks.push(event.data);
                log('📊 Audio chunk: ' + event.data.size + ' bytes');
            }
        };
        
        mediaRecorder.onstop = () => {
            log('⏹️ Recording stopped');
            processRecording();
        };
        
        // Start recording
        mediaRecorder.start(100);
        isRecording = true;
        recordingStartTime = Date.now();
        
        log('🔴 RECORDING STARTED');
        startRecordingUI();
        
        // Auto-stop after 10 seconds
        setTimeout(() => {
            if (isRecording) {
                log('⏰ Auto-stopping');
                stopRecording();
            }
        }, 10000);
        
    } catch (e) {
        log('❌ MediaRecorder error: ' + e.message);
        updateStatus('❌ Recording setup failed', '#ff4444');
        stream.getTracks().forEach(track => track.stop());
    }
}

function handleMicrophoneError(error) {
    log('❌ Microphone error: ' + error.name + ' - ' + error.message);
    
    let message;
    if (error.name === 'NotAllowedError') {
        message = '❌ Please allow microphone access and try again!';
    } else if (error.name === 'NotFoundError') {
        message = '❌ No microphone found on this device';
    } else {
        message = '❌ Microphone access failed: ' + error.message;
    }
    
    updateStatus(message, '#ff4444');
}

function startRecordingUI() {
    const recordButton = document.getElementById('recordButton');
    const timer = document.getElementById('recordingTimer');
    const levelIndicator = document.getElementById('levelIndicator');
    
    recordButton.innerHTML = '⏹️ STOP';
    recordButton.className = 'recording';
    
    updateStatus('🔴 RECORDING - Tap STOP when finished', '#ff4444');
    
    timer.style.display = 'block';
    levelIndicator.style.display = 'block';
    
    startTimer();
    startLevelMonitor();
}

function startTimer() {
    timerInterval = setInterval(() => {
        if (!isRecording) return;
        
        const elapsed = Math.floor((Date.now() - recordingStartTime) / 1000);
        const minutes = Math.floor(elapsed / 60);
        const seconds = elapsed % 60;
        
        const timerText = document.getElementById('timerText');
        if (timerText) {
            timerText.textContent = minutes + ':' + seconds.toString().padStart(2, '0');
        }
    }, 100);
}

function startLevelMonitor() {
    try {
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
        analyser = audioContext.createAnalyser();
        const source = audioContext.createMediaStreamSource(mediaStream);
        source.connect(analyser);
        
        analyser.fftSize = 256;
        
        function updateLevel() {
            if (!isRecording) return;
            
            const bufferLength = analyser.frequencyBinCount;
            const dataArray = new Uint8Array(bufferLength);
            analyser.getByteFrequencyData(dataArray);
            
            const average = dataArray.reduce((sum, value) => sum + value, 0) / bufferLength;
            const level = Math.min(100, (average / 255) * 100);
            
            const levelBar = document.getElementById('levelBar');
            if (levelBar) {
                levelBar.style.width = Math.max(level, 5) + '%';
            }
            
            animationId = requestAnimationFrame(updateLevel);
        }
        
        updateLevel();
    } catch (e) {
        log('⚠️ Level monitor failed: ' + e.message);
    }
}

function stopRecording() {
    if (!isRecording) return;
    
    log('⏹️ Stopping recording...');
    
    mediaRecorder.stop();
    isRecording = false;
    
    if (timerInterval) clearInterval(timerInterval);
    if (animationId) cancelAnimationFrame(animationId);
    
    if (mediaStream) {
        mediaStream.getTracks().forEach(track => track.stop());
    }
    
    const recordButton = document.getElementById('recordButton');
    recordButton.innerHTML = '🎙️ RECORD';
    recordButton.className = '';
    
    updateStatus('⏸️ Processing recording...', '#ffa500');
    
    document.getElementById('recordingTimer').style.display = 'none';
    document.getElementById('levelIndicator').style.display = 'none';
}

function processRecording() {
    if (audioChunks.length === 0) {
        log('❌ No audio data');
        updateStatus('❌ No audio recorded', '#ff4444');
        return;
    }
    
    log('📊 Processing ' + audioChunks.length + ' chunks');
    
    const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
    window.audioBlob = audioBlob;
    window.audioUrl = URL.createObjectURL(audioBlob);
    
    log('✅ Processed: ' + audioBlob.size + ' bytes');
    
    updateStatus('✅ Recording ready! Click DOWNLOAD', '#28a745');
    document.getElementById('controls').style.display = 'block';
}

function downloadRecording() {
    if (!window.audioBlob) {
        updateStatus('❌ No recording available', '#ff4444');
        return;
    }
    
    log('💾 Starting download...');
    
    const a = document.createElement('a');
    a.href = window.audioUrl;
    a.download = 'heart_sound_' + new Date().toISOString().slice(0, 19).replace(/:/g, '-') + '.webm';
    a.click();
    
    updateStatus('📥 Download started! Check Downloads folder', '#28a745');
    log('✅ Download initiated');
}

// Initialize immediately
window.addEventListener('load', function() {
    log('🚀 Page loaded - ready to record');
    updateStatus('🎯 Ready! Tap RECORD for microphone permission', '#28a745');
});
</script>
"""

def main():
    """Ultra-simplified mobile recorder that forces microphone request."""
    
    st.markdown("# 📱 Heart Sound Recorder - FORCE MICROPHONE")
    st.markdown("### 🔧 This version immediately requests microphone access")

    # Mobile recording interface
    components.html(FORCE_MICROPHONE_HTML, height=600)

    st.markdown("---")
    st.error("🔧 **DEBUGGING VERSION**: No browser checks - direct microphone request")
    st.info("📱 **This should work on your mobile device and request microphone permission**")

if __name__ == "__main__":
    main()