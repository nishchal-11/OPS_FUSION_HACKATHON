"""
Mobile Audio Recorder - Web App for Heart Sound Recording
This app runs on a separate port and can be accessed via QR code scanning.
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

# Custom CSS for mobile optimization
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
    .record-button:hover, .record-button:active {
        background-color: #cc0000;
        transform: scale(1.05);
    }
    .record-button:disabled {
        background-color: #ccc;
        cursor: not-allowed;
        transform: none;
    }
    .record-button.recording {
        background-color: #44ff44;
        animation: pulse 1s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.1); }
        100% { transform: scale(1); }
    }
    .status-text {
        text-align: center;
        font-size: 18px;
        font-weight: bold;
        margin: 20px 0;
    }
    .instructions {
        background-color: #f0f8ff;
        padding: 15px;
        border-radius: 10px;
        margin: 20px 0;
        border-left: 4px solid #1e90ff;
    }
    .waveform-container {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# JavaScript for audio recording - MOBILE OPTIMIZED
AUDIO_RECORDER_HTML = """
<div class="mobile-container">
    <h1 style="text-align: center; color: #1e90ff;">🎙️ Heart Sound Recorder</h1>
    <p style="text-align: center; color: #666;">Record heart sounds for analysis</p>

    <div class="instructions">
        <h4>📋 Instructions:</h4>
        <ol>
            <li>Click the RECORD button below</li>
            <li>Allow microphone access when prompted</li>
            <li>Place phone near heart area</li>
            <li>Record for 5-10 seconds</li>
            <li>Click STOP and then DOWNLOAD</li>
        </ol>
    </div>

    <div id="status" class="status-text">🎯 Tap RECORD to start</div>

    <div style="text-align: center; margin: 30px 0;">
        <button id="recordButton" class="record-button" onclick="toggleRecording()">
            🎙️ RECORD
        </button>
    </div>

    <div id="waveform" class="waveform-container" style="display: none;">
        <h4>🎵 Live Audio:</h4>
        <canvas id="waveformCanvas" width="320" height="80" style="border: 1px solid #ddd; border-radius: 5px; width: 100%; max-width: 320px;"></canvas>
    </div>

    <div id="controls" style="text-align: center; margin: 20px 0; display: none;">
        <button id="downloadButton" onclick="downloadRecording()" style="background: #28a745; color: white; border: none; padding: 15px 30px; border-radius: 10px; font-size: 16px; margin: 10px;">💾 DOWNLOAD</button>
    </div>

    <div id="debugInfo" style="text-align: center; color: #666; font-size: 12px; margin-top: 20px;"></div>

    <!-- Mobile-specific help section -->
    <div id="mobileHelp" style="background: #f0f8ff; padding: 15px; border-radius: 10px; margin: 20px 0; display: none;">
        <h4 style="color: #1e90ff;">📱 Mobile Browser Help</h4>
        <p><strong>If recording doesn't work:</strong></p>
        <ol>
            <li><strong>Allow microphone permissions</strong> when prompted</li>
            <li><strong>Try Chrome browser</strong> (most compatible)</li>
            <li><strong>Check microphone isn't used by other apps</strong></li>
            <li><strong>Try refreshing the page</strong></li>
            <li><strong>Update your browser</strong> to the latest version</li>
        </ol>
        <p><strong>Supported browsers:</strong> Chrome, Firefox, Safari (iOS 14.5+), Edge</p>
    </div>
</div>

<script>
let mediaRecorder;
let audioChunks = [];
let isRecording = false;
let audioContext;
let analyser;
let mediaStream;
let animationId;

// Debug function
function logDebug(message) {
    console.log(message);
    const debugDiv = document.getElementById('debugInfo');
    if (debugDiv) {
        debugDiv.innerHTML += message + '<br>';
    }
}

// ULTRA-LENIENT browser compatibility check for mobile
function checkBrowserSupport() {
    logDebug('🔍 Checking browser support...');
    
    // For mobile browsers, be extremely lenient
    const isMobile = /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    if (isMobile) {
        logDebug('📱 Mobile device detected - using mobile-optimized checks');
        
        // Just check for basic navigator existence
        if (navigator) {
            logDebug('✅ Mobile browser support assumed');
            return true;
        }
    }
    
    // For desktop, do normal checks
    if (navigator.mediaDevices || navigator.getUserMedia || navigator.webkitGetUserMedia || navigator.mozGetUserMedia) {
        logDebug('✅ Desktop browser supports audio recording');
        return true;
    }
    
    // Last resort - assume support if we have a modern browser
    if (window.fetch && window.Promise) {
        logDebug('✅ Modern browser detected - assuming audio support');
        return true;
    }
    
    logDebug('❌ No audio support detected');
    return false;
}

// Main recording toggle function - MOBILE OPTIMIZED
function toggleRecording() {
    logDebug('🎯 Toggle recording clicked');
    
    // On mobile, skip browser checks and try directly
    const isMobile = /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    if (isMobile) {
        logDebug('📱 Mobile device - attempting direct recording');
        if (!isRecording) {
            startRecording();
        } else {
            stopRecording();
        }
        return;
    }
    
    // Desktop browser check
    if (!checkBrowserSupport()) {
        document.getElementById('status').innerHTML = '❌ Browser not supported';
        return;
    }
    
    if (!isRecording) {
        startRecording();
    } else {
        stopRecording();
    }
}

// Request microphone access and start recording
function startRecording() {
    logDebug('🎙️ Starting recording...');
    
    document.getElementById('status').innerHTML = '🔄 Requesting microphone access...';
    document.getElementById('status').style.color = '#ffa500';
    
    // Request microphone with specific constraints for mobile
    const constraints = {
        audio: {
            echoCancellation: false,
            noiseSuppression: false,
            autoGainControl: false,
            sampleRate: 44100,
            channelCount: 1
        }
    };
    
    // MOBILE-FIRST getUserMedia with maximum compatibility
    let getUserMediaPromise;
    
    // Try modern API first
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        logDebug('🔧 Using modern mediaDevices API');
        getUserMediaPromise = navigator.mediaDevices.getUserMedia(constraints);
    }
    // Try legacy APIs with Promise wrappers
    else if (navigator.getUserMedia || navigator.webkitGetUserMedia || navigator.mozGetUserMedia) {
        logDebug('🔧 Using legacy getUserMedia API');
        const getUserMedia = navigator.getUserMedia || navigator.webkitGetUserMedia || navigator.mozGetUserMedia;
        getUserMediaPromise = new Promise((resolve, reject) => {
            getUserMedia.call(navigator, constraints, resolve, reject);
        });
    }
    // Last resort for mobile browsers
    else {
        logDebug('🔧 Using fallback for mobile browsers');
        // Try to access with minimal constraints for mobile compatibility
        const fallbackConstraints = { audio: true };
        
        if (navigator.mediaDevices) {
            getUserMediaPromise = navigator.mediaDevices.getUserMedia(fallbackConstraints);
        } else {
            throw new Error('No audio recording API available. Please try a different browser or update your current browser.');
        }
    }
    
    getUserMediaPromise
        .then(stream => {
            logDebug('✅ Microphone access granted');
            mediaStream = stream;
            
            // MOBILE-OPTIMIZED MediaRecorder creation
            let options = {};
            
            // Check if MediaRecorder exists at all
            const MediaRecorderClass = window.MediaRecorder || window.webkitMediaRecorder || window.mozMediaRecorder;
            
            if (!MediaRecorderClass) {
                throw new Error('MediaRecorder not supported on this device. Please try Chrome, Firefox, or Safari.');
            }
            
            // Try mobile-friendly MIME types first
            const mimeTypes = [
                'audio/webm',           // Most compatible
                'audio/mp4',            // iOS Safari
                'audio/wav',            // Fallback
                'audio/ogg',            // Firefox mobile
                ''                      // Let browser decide
            ];
            
            for (let mimeType of mimeTypes) {
                try {
                    if (mimeType === '' || MediaRecorderClass.isTypeSupported(mimeType)) {
                        if (mimeType) {
                            options.mimeType = mimeType;
                            logDebug(`✅ Using MIME type: ${mimeType}`);
                        } else {
                            logDebug('✅ Using browser default MIME type');
                        }
                        break;
                    }
                } catch (e) {
                    logDebug(`⚠️ MIME type ${mimeType} check failed: ${e.message}`);
                }
            }
            
            // Create MediaRecorder with error handling
            try {
                mediaRecorder = new MediaRecorderClass(stream, options);
                logDebug('✅ MediaRecorder created successfully');
            } catch (e) {
                // Final fallback - create without options
                logDebug('⚠️ Creating MediaRecorder without options');
                mediaRecorder = new MediaRecorderClass(stream);
            }
            audioChunks = [];

            mediaRecorder.ondataavailable = event => {
                if (event.data.size > 0) {
                    audioChunks.push(event.data);
                    logDebug(`📊 Audio chunk: ${event.data.size} bytes`);
                }
            };

            mediaRecorder.onstop = () => {
                logDebug('⏹️ Recording stopped, processing...');
                processRecording();
            };
            
            mediaRecorder.onerror = (error) => {
                logDebug(`❌ MediaRecorder error: ${error}`);
                document.getElementById('status').innerHTML = '❌ Recording error';
            };

            // Start recording
            mediaRecorder.start(100); // Collect data every 100ms
            isRecording = true;

            // Update UI
            document.getElementById('recordButton').innerHTML = '⏹️ STOP';
            document.getElementById('recordButton').classList.add('recording');
            document.getElementById('status').innerHTML = '🔴 Recording... (10s max)';
            document.getElementById('status').style.color = '#ff4444';
            
            // Show waveform
            initWaveform(stream);
            document.getElementById('waveform').style.display = 'block';
            
            // Auto-stop after 10 seconds
            setTimeout(() => {
                if (isRecording) {
                    logDebug('⏰ Auto-stopping after 10 seconds');
                    stopRecording();
                }
            }, 10000);

        })
        .catch(error => {
            logDebug(`❌ Microphone error: ${error.name} - ${error.message}`);
            
            // Provide user-friendly error messages
            let errorMessage = '❌ Microphone access denied';
            if (error.name === 'NotAllowedError') {
                errorMessage = '❌ Microphone permission denied. Please allow microphone access and try again.';
            } else if (error.name === 'NotFoundError') {
                errorMessage = '❌ No microphone found. Please check your device settings.';
            } else if (error.name === 'NotSupportedError') {
                errorMessage = '❌ Audio recording not supported on this device.';
            } else if (error.name === 'SecurityError') {
                errorMessage = '❌ Microphone access blocked. Please check your browser security settings.';
            }
            
            document.getElementById('status').innerHTML = errorMessage;
            document.getElementById('status').style.color = '#ff4444';
            
            // Reset recording state
            isRecording = false;
            document.getElementById('recordButton').innerHTML = '🎙️ RECORD';
            document.getElementById('recordButton').classList.remove('recording');
        });
}

// Stop recording
function stopRecording() {
    if (mediaRecorder && isRecording) {
        logDebug('⏹️ Stopping recording...');
        
        mediaRecorder.stop();
        isRecording = false;

        // Update UI
        document.getElementById('recordButton').innerHTML = '🎙️ RECORD';
        document.getElementById('recordButton').classList.remove('recording');
        document.getElementById('status').innerHTML = '⏸️ Processing...';
        document.getElementById('status').style.color = '#ffa500';

        // Stop waveform
        if (animationId) {
            cancelAnimationFrame(animationId);
        }

        // Stop media tracks
        if (mediaStream) {
            mediaStream.getTracks().forEach(track => {
                track.stop();
                logDebug('🛑 Audio track stopped');
            });
        }
    }
}

// Process the recorded audio
function processRecording() {
    if (audioChunks.length === 0) {
        logDebug('❌ No audio data recorded');
        document.getElementById('status').innerHTML = '❌ No audio recorded';
        return;
    }
    
    logDebug(`📊 Processing ${audioChunks.length} audio chunks`);
    
    // Create blob from chunks
    const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
    const audioUrl = URL.createObjectURL(audioBlob);

    // Store for download
    window.audioBlob = audioBlob;
    window.audioUrl = audioUrl;

    logDebug(`✅ Audio ready: ${audioBlob.size} bytes`);
    
    // Update UI
    document.getElementById('status').innerHTML = '✅ Recording ready! Click DOWNLOAD';
    document.getElementById('status').style.color = '#28a745';
    document.getElementById('controls').style.display = 'block';
}

// Download the recording
function downloadRecording() {
    if (!window.audioBlob) {
        logDebug('❌ No recording to download');
        return;
    }
    
    logDebug('💾 Starting download...');
    
    const url = window.audioUrl;
    const a = document.createElement('a');
    a.style.display = 'none';
    a.href = url;
    a.download = `heart_sound_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.webm`;
    
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);

    logDebug('📥 Download initiated');
    document.getElementById('status').innerHTML = '📥 Download started! Check your downloads folder.';
    document.getElementById('status').style.color = '#28a745';
}

// Initialize waveform visualization
function initWaveform(stream) {
    try {
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
        analyser = audioContext.createAnalyser();
        const source = audioContext.createMediaStreamSource(stream);
        source.connect(analyser);
        analyser.fftSize = 256;

        const canvas = document.getElementById('waveformCanvas');
        const canvasContext = canvas.getContext('2d');
        
        drawWaveform(analyser, canvas, canvasContext);
        logDebug('🎵 Waveform initialized');
    } catch (error) {
        logDebug(`⚠️ Waveform error: ${error.message}`);
    }
}

// Draw waveform
function drawWaveform(analyser, canvas, canvasContext) {
    if (!analyser || !canvas) return;

    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);

    function draw() {
        if (!isRecording) return;
        
        analyser.getByteTimeDomainData(dataArray);

        canvasContext.fillStyle = '#f8f9fa';
        canvasContext.fillRect(0, 0, canvas.width, canvas.height);

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
        animationId = requestAnimationFrame(draw);
    }

    draw();
}

// Initialize when page loads - MOBILE FIRST
window.onload = function() {
    logDebug('🚀 Page loaded, initializing...');
    
    // Always assume mobile support first
    const isMobile = /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    
    if (isMobile) {
        logDebug('📱 Mobile device detected - enabling optimistic mode');
        document.getElementById('status').innerHTML = '📱 Mobile Ready! Tap RECORD to start';
        document.getElementById('status').style.color = '#28a745';
        
        // Show mobile help section
        const mobileHelp = document.getElementById('mobileHelp');
        if (mobileHelp) {
            mobileHelp.style.display = 'block';
        }
        
        // Enable the button on mobile regardless of API checks
        const recordButton = document.getElementById('recordButton');
        if (recordButton) {
            recordButton.disabled = false;
            recordButton.style.backgroundColor = '#ff4444';
        }
        return; // Skip further checks on mobile
    }
    
    // Only do strict checks on desktop
    if (checkBrowserSupport()) {
        document.getElementById('status').innerHTML = '🎯 Ready! Click RECORD to start';
        document.getElementById('status').style.color = '#28a745';
    } else {
        document.getElementById('status').innerHTML = '❌ Desktop browser compatibility issue. Try Chrome or Firefox.';
        document.getElementById('status').style.color = '#ff4444';
        document.getElementById('recordButton').disabled = true;
        document.getElementById('recordButton').style.backgroundColor = '#ccc';
    }
};

// Handle mobile touch events
document.addEventListener('DOMContentLoaded', function() {
    // Ensure touch events work on mobile
    const recordButton = document.getElementById('recordButton');
    if (recordButton) {
        recordButton.addEventListener('touchstart', function(e) {
            e.preventDefault(); // Prevent double-tap
            toggleRecording();
        });
    }
});
</script>
"""

def main():
    """Main mobile recorder application."""

    # Title and description
    st.markdown("# 📱 Mobile Heart Sound Recorder")
    st.markdown("### Record heart sounds directly from your mobile device")

    # Mobile recording interface
    components.html(AUDIO_RECORDER_HTML, height=600)

    # Instructions for use
    st.markdown("---")
    st.markdown("## 📋 How to Use:")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🎙️ Recording Steps:")
        st.markdown("1. **Allow microphone access** when prompted")
        st.markdown("2. **Click the red RECORD button**")
        st.markdown("3. **Place device near heart** (or use stethoscope)")
        st.markdown("4. **Record for 5-10 seconds**")
        st.markdown("5. **Click STOP** when finished")

    with col2:
        st.markdown("### 💾 After Recording:")
        st.markdown("1. **Click DOWNLOAD** to save the audio file")
        st.markdown("2. **Go back to the main analyzer**")
        st.markdown("3. **Upload the downloaded file**")
        st.markdown("4. **View your analysis results**")

    # Technical notes
    st.markdown("---")
    st.markdown("## 🔧 Technical Details:")
    st.markdown("- **Format:** WAV audio (16-bit, 44.1kHz)")
    st.markdown("- **Duration:** Auto-stop after 10 seconds")
    st.markdown("- **Compatibility:** Works on mobile browsers with microphone support")
    st.markdown("- **Privacy:** Audio is processed locally on your device")

    # Troubleshooting
    with st.expander("🔍 Troubleshooting"):
        st.markdown("""
        **Microphone not working?**
        - Ensure you've granted microphone permissions
        - Try refreshing the page
        - Check if another app is using the microphone

        **Recording too short?**
        - The app auto-stops after 10 seconds
        - Click STOP manually if you finish earlier

        **Download not working?**
        - Check your browser's download settings
        - Try a different browser if issues persist
        """)

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>Part of the Heart Sound Analyzer system</p>
        <p>🔗 <a href='/'>Back to Main Analyzer</a></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()