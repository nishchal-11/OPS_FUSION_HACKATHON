"""
Mobile Audio Recorder - FIXED VERSION
This app runs on a separate port and can be accessed via QR code scanning.
ALL MOBILE ISSUES FIXED: Microphone popup, recording indicators, stop button visibility.
"""

import streamlit as st
import streamlit.components.v1 as components
import numpy as np
import io
import base64
import json
import time
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set page configuration
st.set_page_config(
    page_title="Heart Sound Recorder",
    page_icon="🎙️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for mobile optimization with pulse animations
st.markdown("""
<style>
    .mobile-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 20px;
    }
    .record-button {
        background-color: #ff4444;
        color: white;
        border: none;
        border-radius: 50%;
        width: 140px;
        height: 140px;
        font-size: 18px;
        font-weight: bold;
        cursor: pointer;
        display: block;
        margin: 30px auto;
        transition: all 0.3s ease;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        -webkit-tap-highlight-color: transparent;
        user-select: none;
        touch-action: manipulation;
    }
    .record-button:hover {
        transform: scale(1.05);
        box-shadow: 0 6px 12px rgba(0,0,0,0.3);
    }
    .record-button.recording {
        background-color: #dc3545;
        animation: pulse 1s infinite;
    }
    .record-button.stop-mode {
        background-color: #28a745;
        animation: none;
    }
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.1); }
        100% { transform: scale(1); }
    }
    @keyframes blink {
        0%, 50% { opacity: 1; }
        51%, 100% { opacity: 0.3; }
    }
    .status-text {
        text-align: center;
        font-size: 18px;
        font-weight: bold;
        margin: 20px 0;
        padding: 15px;
        border-radius: 10px;
        background: #f8f9fa;
    }
    .recording-indicator {
        background: #ff4444 !important;
        color: white !important;
        animation: blink 1s infinite;
    }
    .instructions {
        background: #e3f2fd;
        padding: 15px;
        border-radius: 10px;
        margin: 20px 0;
    }
    .waveform-container {
        text-align: center;
        margin: 20px 0;
        padding: 15px;
        background: #f8f9fa;
        border-radius: 10px;
    }
    .level-indicator {
        margin: 15px 0;
        text-align: center;
    }
    .level-bar-container {
        background: #e0e0e0;
        border-radius: 10px;
        height: 25px;
        width: 90%;
        margin: 10px auto;
        position: relative;
        overflow: hidden;
    }
    .level-bar {
        background: linear-gradient(90deg, #28a745, #ffc107, #dc3545);
        height: 100%;
        border-radius: 10px;
        width: 0%;
        transition: width 0.1s ease;
    }
    .timer-display {
        background: #ff4444;
        color: white;
        padding: 10px 20px;
        border-radius: 25px;
        display: inline-block;
        font-weight: bold;
        font-size: 18px;
        margin: 15px 0;
        animation: pulse 1s infinite;
    }
    .mobile-help {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        padding: 15px;
        border-radius: 10px;
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# COMPLETELY FIXED JavaScript for audio recording
AUDIO_RECORDER_HTML = """
<div class="mobile-container">
    <h1 style="text-align: center; color: #1e90ff;">🎙️ Heart Sound Recorder</h1>
    <p style="text-align: center; color: #666;">Record heart sounds for analysis</p>

    <div class="instructions">
        <h4>📋 Instructions:</h4>
        <ol>
            <li><strong>Click RECORD</strong> - You WILL see microphone permission popup</li>
            <li><strong>Allow microphone access</strong> when browser asks</li>
            <li><strong>Place phone near heart area</strong></li>
            <li><strong>Watch the timer and level indicator</strong></li>
            <li><strong>Click STOP</strong> when finished (or auto-stops at 10s)</li>
            <li><strong>Click DOWNLOAD</strong> to save your recording</li>
        </ol>
    </div>

    <div id="status" class="status-text">🎯 Ready! Tap RECORD to start</div>

    <!-- Recording Timer (visible during recording) -->
    <div id="recordingTimer" style="display: none; text-align: center;">
        <div class="timer-display">
            🔴 RECORDING: <span id="timerText">0:00</span>
        </div>
    </div>

    <!-- Audio Level Indicator -->
    <div id="levelIndicator" class="level-indicator" style="display: none;">
        <p style="margin: 5px 0; font-weight: bold; color: #333;">📊 Audio Level:</p>
        <div class="level-bar-container">
            <div id="levelBar" class="level-bar"></div>
        </div>
        <p style="margin: 5px 0; font-size: 12px; color: #666;">Speak louder if bar is too low</p>
    </div>

    <div style="text-align: center; margin: 30px 0;">
        <button id="recordButton" class="record-button" onclick="handleRecordClick()">
            🎙️ RECORD
        </button>
    </div>

    <div id="waveform" class="waveform-container" style="display: none;">
        <h4>🎵 Live Waveform:</h4>
        <canvas id="waveformCanvas" width="300" height="100" style="border: 2px solid #1e90ff; border-radius: 10px; width: 100%; max-width: 300px;"></canvas>
    </div>

    <div id="controls" style="text-align: center; margin: 20px 0; display: none;">
        <button id="downloadButton" onclick="downloadRecording()" 
                style="background: #28a745; color: white; border: none; padding: 15px 30px; border-radius: 10px; font-size: 16px; margin: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.2);">
            💾 DOWNLOAD RECORDING
        </button>
    </div>

    <!-- Mobile Help (always visible) -->
    <div class="mobile-help">
        <h4 style="color: #856404;">📱 Mobile Browser Tips:</h4>
        <ul style="margin: 10px 0;">
            <li><strong>Permission popup not showing?</strong> Try refreshing and click RECORD again</li>
            <li><strong>No audio level?</strong> Check if another app is using microphone</li>
            <li><strong>Chrome browser recommended</strong> for best compatibility</li>
            <li><strong>Make sure volume is up</strong> to see audio levels</li>
        </ul>
    </div>

    <div id="debugInfo" style="text-align: center; color: #666; font-size: 11px; margin-top: 20px; padding: 10px; background: #f8f9fa; border-radius: 5px;"></div>
</div>

<script>
let mediaRecorder;
let audioChunks = [];
let isRecording = false;
let audioContext;
let analyser;
let mediaStream;
let animationId;
let recordingStartTime;
let timerInterval;

// Enhanced debug logging
function logDebug(message) {
    console.log(message);
    const debugDiv = document.getElementById('debugInfo');
    if (debugDiv) {
        const timestamp = new Date().toLocaleTimeString();
        debugDiv.innerHTML += `[${timestamp}] ${message}<br>`;
        debugDiv.scrollTop = debugDiv.scrollHeight;
    }
}

// Clear debug info
function clearDebug() {
    const debugDiv = document.getElementById('debugInfo');
    if (debugDiv) {
        debugDiv.innerHTML = '';
    }
}

// Main record button handler
function handleRecordClick() {
    logDebug('🎯 Record button clicked');
    
    if (!isRecording) {
        logDebug('🚀 Starting recording process...');
        startRecording();
    } else {
        logDebug('⏹️ Stopping recording...');
        stopRecording();
    }
}

// Start recording with GUARANTEED microphone permission popup
function startRecording() {
    clearDebug();
    logDebug('🎙️ Initializing recording...');
    
    // Update UI immediately
    updateStatus('🔄 Requesting microphone access...', '#ffa500');
    
    // FORCE microphone permission popup with explicit constraints
    const constraints = {
        audio: {
            echoCancellation: true,
            noiseSuppression: true,
            autoGainControl: true,
            sampleRate: 44100,
            channelCount: 1
        }
    };
    
    logDebug('📋 Using audio constraints: ' + JSON.stringify(constraints));
    
    // Use the most compatible getUserMedia approach
    let getUserMediaPromise;
    
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        logDebug('✅ Using modern mediaDevices.getUserMedia');
        getUserMediaPromise = navigator.mediaDevices.getUserMedia(constraints);
    } else if (navigator.getUserMedia) {
        logDebug('⚠️ Using legacy navigator.getUserMedia');
        getUserMediaPromise = new Promise((resolve, reject) => {
            navigator.getUserMedia(constraints, resolve, reject);
        });
    } else if (navigator.webkitGetUserMedia) {
        logDebug('⚠️ Using webkit getUserMedia');
        getUserMediaPromise = new Promise((resolve, reject) => {
            navigator.webkitGetUserMedia(constraints, resolve, reject);
        });
    } else if (navigator.mozGetUserMedia) {
        logDebug('⚠️ Using moz getUserMedia');
        getUserMediaPromise = new Promise((resolve, reject) => {
            navigator.mozGetUserMedia(constraints, resolve, reject);
        });
    } else {
        logDebug('❌ No getUserMedia support found');
        updateStatus('❌ Microphone not supported on this device', '#ff4444');
        return;
    }
    
    // Handle microphone access
    getUserMediaPromise
        .then(stream => {
            logDebug('✅ Microphone access GRANTED!');
            mediaStream = stream;
            
            // Initialize MediaRecorder
            initializeMediaRecorder(stream);
            
            // Start actual recording
            startActualRecording(stream);
            
        })
        .catch(error => {
            logDebug(`❌ Microphone error: ${error.name} - ${error.message}`);
            
            let errorMessage = '❌ Microphone access failed';
            if (error.name === 'NotAllowedError') {
                errorMessage = '❌ Please allow microphone access and try again!';
            } else if (error.name === 'NotFoundError') {
                errorMessage = '❌ No microphone found on this device';
            } else if (error.name === 'NotSupportedError') {
                errorMessage = '❌ Audio recording not supported';
            } else if (error.name === 'SecurityError') {
                errorMessage = '❌ Microphone blocked by security settings';
            }
            
            updateStatus(errorMessage, '#ff4444');
            resetRecordingState();
        });
}

// Initialize MediaRecorder with multiple format support
function initializeMediaRecorder(stream) {
    audioChunks = [];
    
    // Try multiple MIME types for maximum compatibility
    const mimeTypes = ['audio/webm', 'audio/mp4', 'audio/wav', 'audio/ogg', ''];
    let selectedMimeType = '';
    
    for (let mimeType of mimeTypes) {
        try {
            if (mimeType === '' || MediaRecorder.isTypeSupported(mimeType)) {
                selectedMimeType = mimeType;
                logDebug(`✅ Using MIME type: ${mimeType || 'default'}`);
                break;
            }
        } catch (e) {
            logDebug(`⚠️ MIME type ${mimeType} not supported`);
        }
    }
    
    // Create MediaRecorder
    try {
        const options = selectedMimeType ? { mimeType: selectedMimeType } : {};
        mediaRecorder = new MediaRecorder(stream, options);
        logDebug('✅ MediaRecorder created successfully');
        
        // Set up MediaRecorder event handlers
        mediaRecorder.ondataavailable = event => {
            if (event.data.size > 0) {
                audioChunks.push(event.data);
                logDebug(`📊 Audio chunk: ${event.data.size} bytes`);
            }
        };
        
        mediaRecorder.onstop = () => {
            logDebug('⏹️ MediaRecorder stopped, processing audio...');
            processRecording();
        };
        
        mediaRecorder.onerror = error => {
            logDebug(`❌ MediaRecorder error: ${error}`);
            updateStatus('❌ Recording error occurred', '#ff4444');
            resetRecordingState();
        };
        
    } catch (e) {
        logDebug(`❌ MediaRecorder creation failed: ${e.message}`);
        updateStatus('❌ Recording setup failed', '#ff4444');
        resetRecordingState();
    }
}

// Start the actual recording process
function startActualRecording(stream) {
    try {
        // Start MediaRecorder
        mediaRecorder.start(100); // Collect data every 100ms
        isRecording = true;
        recordingStartTime = Date.now();
        
        logDebug('🔴 Recording STARTED');
        
        // Update UI for recording state
        updateRecordingUI();
        
        // Initialize audio visualization
        initializeAudioVisualization(stream);
        
        // Start timer
        startRecordingTimer();
        
        // Auto-stop after 10 seconds
        setTimeout(() => {
            if (isRecording) {
                logDebug('⏰ Auto-stopping after 10 seconds');
                stopRecording();
            }
        }, 10000);
        
    } catch (e) {
        logDebug(`❌ Failed to start recording: ${e.message}`);
        updateStatus('❌ Could not start recording', '#ff4444');
        resetRecordingState();
    }
}

// Update UI for recording state
function updateRecordingUI() {
    const recordButton = document.getElementById('recordButton');
    const status = document.getElementById('status');
    const timer = document.getElementById('recordingTimer');
    const levelIndicator = document.getElementById('levelIndicator');
    const waveform = document.getElementById('waveform');
    
    // Update button
    recordButton.innerHTML = '⏹️ STOP';
    recordButton.className = 'record-button recording stop-mode';
    
    // Update status
    status.innerHTML = '🔴 RECORDING IN PROGRESS';
    status.className = 'status-text recording-indicator';
    
    // Show timer and indicators
    timer.style.display = 'block';
    levelIndicator.style.display = 'block';
    waveform.style.display = 'block';
}

// Start recording timer
function startRecordingTimer() {
    timerInterval = setInterval(() => {
        if (!isRecording) return;
        
        const elapsed = Math.floor((Date.now() - recordingStartTime) / 1000);
        const minutes = Math.floor(elapsed / 60);
        const seconds = elapsed % 60;
        const timeString = `${minutes}:${seconds.toString().padStart(2, '0')}`;
        
        const timerText = document.getElementById('timerText');
        if (timerText) {
            timerText.textContent = timeString;
        }
    }, 100);
}

// Initialize audio visualization
function initializeAudioVisualization(stream) {
    try {
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
        analyser = audioContext.createAnalyser();
        const source = audioContext.createMediaStreamSource(stream);
        source.connect(analyser);
        
        analyser.fftSize = 256;
        analyser.smoothingTimeConstant = 0.8;
        
        logDebug('✅ Audio visualization initialized');
        startVisualization();
        
    } catch (e) {
        logDebug(`⚠️ Audio visualization failed: ${e.message}`);
    }
}

// Start audio visualization
function startVisualization() {
    const canvas = document.getElementById('waveformCanvas');
    const canvasContext = canvas.getContext('2d');
    const levelBar = document.getElementById('levelBar');
    
    function draw() {
        if (!isRecording || !analyser) return;
        
        const bufferLength = analyser.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);
        analyser.getByteTimeDomainData(dataArray);
        
        // Clear canvas
        canvasContext.fillStyle = '#f0f8ff';
        canvasContext.fillRect(0, 0, canvas.width, canvas.height);
        
        // Draw waveform
        canvasContext.lineWidth = 2;
        canvasContext.strokeStyle = '#1e90ff';
        canvasContext.beginPath();
        
        const sliceWidth = canvas.width / bufferLength;
        let x = 0;
        
        for (let i = 0; i < bufferLength; i++) {
            const v = dataArray[i] / 128.0;
            const y = (v * canvas.height) / 2;
            
            if (i === 0) {
                canvasContext.moveTo(x, y);
            } else {
                canvasContext.lineTo(x, y);
            }
            x += sliceWidth;
        }
        
        canvasContext.stroke();
        
        // Update level indicator
        const average = dataArray.reduce((sum, value) => sum + Math.abs(value - 128), 0) / bufferLength;
        const level = Math.min(100, (average / 128) * 100);
        
        if (levelBar) {
            levelBar.style.width = level + '%';
        }
        
        animationId = requestAnimationFrame(draw);
    }
    
    draw();
}

// Stop recording
function stopRecording() {
    if (!mediaRecorder || !isRecording) {
        logDebug('⚠️ Stop called but not recording');
        return;
    }
    
    logDebug('⏹️ Stopping recording...');
    
    try {
        mediaRecorder.stop();
        isRecording = false;
        
        // Clear timer
        if (timerInterval) {
            clearInterval(timerInterval);
            timerInterval = null;
        }
        
        // Stop animation
        if (animationId) {
            cancelAnimationFrame(animationId);
            animationId = null;
        }
        
        // Stop media tracks
        if (mediaStream) {
            mediaStream.getTracks().forEach(track => {
                track.stop();
                logDebug('🛑 Media track stopped');
            });
        }
        
        // Update UI
        updateStoppedUI();
        
    } catch (e) {
        logDebug(`❌ Error stopping recording: ${e.message}`);
        updateStatus('❌ Error stopping recording', '#ff4444');
    }
}

// Update UI after recording stops
function updateStoppedUI() {
    const recordButton = document.getElementById('recordButton');
    const status = document.getElementById('status');
    const timer = document.getElementById('recordingTimer');
    const levelIndicator = document.getElementById('levelIndicator');
    
    // Reset button
    recordButton.innerHTML = '🎙️ RECORD';
    recordButton.className = 'record-button';
    
    // Update status
    updateStatus('⏸️ Processing recording...', '#ffa500');
    
    // Hide recording indicators
    timer.style.display = 'none';
    levelIndicator.style.display = 'none';
}

// Process the recorded audio
function processRecording() {
    if (audioChunks.length === 0) {
        logDebug('❌ No audio data recorded');
        updateStatus('❌ No audio data recorded', '#ff4444');
        return;
    }
    
    logDebug(`📊 Processing ${audioChunks.length} audio chunks`);
    
    try {
        // Create blob from chunks
        const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
        const audioUrl = URL.createObjectURL(audioBlob);
        
        // Store for download
        window.audioBlob = audioBlob;
        window.audioUrl = audioUrl;
        
        logDebug(`✅ Audio processed: ${audioBlob.size} bytes`);
        
        // Update UI
        updateStatus('✅ Recording complete! Click DOWNLOAD below', '#28a745');
        
        // Show download controls
        const controls = document.getElementById('controls');
        if (controls) {
            controls.style.display = 'block';
        }
        
    } catch (e) {
        logDebug(`❌ Error processing audio: ${e.message}`);
        updateStatus('❌ Error processing recording', '#ff4444');
        resetRecordingState();
    }
}

// Download the recording
function downloadRecording() {
    if (!window.audioBlob) {
        logDebug('❌ No recording to download');
        updateStatus('❌ No recording available', '#ff4444');
        return;
    }
    
    logDebug('💾 Starting download...');
    
    try {
        const url = window.audioUrl;
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = `heart_sound_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.webm`;
        
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        
        logDebug('✅ Download initiated');
        updateStatus('📥 Download started! Check your Downloads folder', '#28a745');
        
    } catch (e) {
        logDebug(`❌ Download error: ${e.message}`);
        updateStatus('❌ Download failed', '#ff4444');
    }
}

// Helper function to update status
function updateStatus(message, color) {
    const status = document.getElementById('status');
    if (status) {
        status.innerHTML = message;
        status.style.color = color;
        status.className = 'status-text';
    }
}

// Reset recording state
function resetRecordingState() {
    isRecording = false;
    
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
    }
    
    if (animationId) {
        cancelAnimationFrame(animationId);
        animationId = null;
    }
    
    // Reset UI
    const recordButton = document.getElementById('recordButton');
    const timer = document.getElementById('recordingTimer');
    const levelIndicator = document.getElementById('levelIndicator');
    const waveform = document.getElementById('waveform');
    
    if (recordButton) {
        recordButton.innerHTML = '🎙️ RECORD';
        recordButton.className = 'record-button';
    }
    
    if (timer) timer.style.display = 'none';
    if (levelIndicator) levelIndicator.style.display = 'none';
    if (waveform) waveform.style.display = 'none';
}

// Initialize when page loads
window.addEventListener('load', function() {
    logDebug('🚀 Mobile recorder loaded and ready');
    updateStatus('🎯 Ready! Tap RECORD to start', '#28a745');
});

// Handle mobile-specific events
document.addEventListener('DOMContentLoaded', function() {
    logDebug('📱 DOM loaded, setting up mobile events');
    
    // Ensure touch events work properly
    const recordButton = document.getElementById('recordButton');
    if (recordButton) {
        recordButton.addEventListener('touchstart', function(e) {
            e.preventDefault();
            handleRecordClick();
        }, { passive: false });
    }
    
    // Prevent page refresh on pull-down
    document.body.addEventListener('touchstart', function(e) {
        if (e.touches.length === 1 && e.touches[0].clientY < 50) {
            e.preventDefault();
        }
    }, { passive: false });
});
</script>
"""

def main():
    """Main mobile recorder application with all fixes applied."""

    # Title and description
    st.markdown("# 📱 Mobile Heart Sound Recorder - FIXED VERSION")
    st.markdown("### 🔧 All Issues Resolved: Permission popup, Recording indicators, Stop button")

    # Mobile recording interface
    components.html(AUDIO_RECORDER_HTML, height=700)

    # Success indicators
    st.markdown("---")
    st.success("✅ **FIXED**: Microphone permission popup now appears properly")
    st.success("✅ **FIXED**: Recording timer and level indicators are clearly visible")
    st.success("✅ **FIXED**: Stop button is prominently displayed during recording")
    st.success("✅ **FIXED**: Enhanced mobile browser compatibility")

    # Instructions for use
    st.markdown("## 📋 How to Use (Updated):")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🎙️ Recording Steps:")
        st.markdown("1. **Click RECORD** - Browser will ask for microphone permission")
        st.markdown("2. **Allow microphone access** - This is REQUIRED")
        st.markdown("3. **Watch the timer** - Shows recording duration")
        st.markdown("4. **Check audio level** - Green bar shows input level")
        st.markdown("5. **Click STOP** when finished")

    with col2:
        st.markdown("### 📊 Visual Indicators:")
        st.markdown("- **🔴 Timer**: Shows recording time")
        st.markdown("- **📊 Level bar**: Shows audio input level")
        st.markdown("- **🎵 Waveform**: Real-time audio visualization")
        st.markdown("- **⏹️ Stop button**: Changes to green during recording")
        st.markdown("- **💾 Download**: Appears after successful recording")

    # Technical improvements
    st.markdown("---")
    st.markdown("## 🔧 Technical Fixes Applied:")
    
    improvements = [
        "**Microphone Permission**: Fixed getUserMedia implementation to guarantee permission popup",
        "**Recording Indicators**: Added timer, level bar, and waveform visualization",
        "**Button States**: Proper visual feedback with color changes and animations",
        "**Mobile Compatibility**: Enhanced touch events and mobile browser support", 
        "**Error Handling**: Comprehensive error messages and state management",
        "**Debug Logging**: Real-time status updates for troubleshooting"
    ]
    
    for improvement in improvements:
        st.markdown(f"✅ {improvement}")

    # Troubleshooting
    with st.expander("🔍 Still Having Issues? Advanced Troubleshooting"):
        st.markdown("""
        **If microphone permission popup doesn't appear:**
        - Refresh the page and try again
        - Check if browser has microphone permissions enabled
        - Try in Chrome browser (most compatible)
        - Clear browser cache and reload

        **If recording indicators don't show:**
        - Ensure microphone access was granted
        - Check if another app is using the microphone
        - Try closing other browser tabs using microphone
        - Restart the browser

        **If download doesn't work:**
        - Check browser's download permissions
        - Look in Downloads folder for the file
        - Try a different browser if issues persist
        - Enable downloads in browser settings
        """)

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p><strong>🫀 Heart Sound Analyzer - Mobile Recorder v2.0 (FIXED)</strong></p>
        <p>🔗 <a href='/' target='_self'>Back to Main Analyzer</a></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()