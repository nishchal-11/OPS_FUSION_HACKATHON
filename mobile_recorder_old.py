"""
Mobile Audio Recorder - ABSOLUTE MINIMAL VERSION
Works on ANY mobile browser with microphone support.
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

# ABSOLUTE MINIMAL HTML - NO CHECKS, JUST MICROPHONE
MINIMAL_RECORDER_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Heart Sound Recorder</title>
</head>
<body style="font-family: Arial, sans-serif; max-width: 400px; margin: 0 auto; padding: 20px; background: #f0f0f0;">
    
    <h1 style="text-align: center; color: #1e90ff;">🎙️ Heart Sound Recorder</h1>
    <p style="text-align: center; color: #666;">Record heart sounds for analysis</p>

    <div style="background: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); margin: 20px 0;">
        <h3 style="color: #333;">📋 Instructions:</h3>
        <ol style="color: #666;">
            <li><strong>Tap RECORD</strong> - Browser will ask for microphone</li>
            <li><strong>Allow microphone access</strong> when popup appears</li>
            <li><strong>Record for 5-10 seconds</strong></li>
            <li><strong>Tap STOP</strong> when finished</li>
            <li><strong>Download your recording</strong></li>
        </ol>
    </div>

    <div id="status" style="text-align: center; background: white; padding: 15px; border-radius: 10px; margin: 20px 0; font-weight: bold; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        🎯 Ready! Tap RECORD to start
    </div>

    <div id="timer" style="display: none; text-align: center; margin: 20px 0;">
        <div style="background: #ff4444; color: white; padding: 15px; border-radius: 20px; display: inline-block; font-weight: bold; font-size: 18px;">
            🔴 RECORDING: <span id="time">0:00</span>
        </div>
    </div>

    <div style="text-align: center; margin: 30px 0;">
        <button id="recordBtn" onclick="record()" 
                style="background: #ff4444; color: white; border: none; border-radius: 50%; width: 120px; height: 120px; font-size: 16px; font-weight: bold; cursor: pointer; box-shadow: 0 6px 12px rgba(0,0,0,0.2); transition: all 0.3s;">
            🎙️<br>RECORD
        </button>
    </div>

    <div id="download" style="display: none; text-align: center; margin: 20px 0;">
        <button onclick="download()" 
                style="background: #28a745; color: white; border: none; padding: 15px 25px; border-radius: 10px; font-size: 16px; cursor: pointer; box-shadow: 0 4px 8px rgba(0,0,0,0.2);">
            💾 DOWNLOAD RECORDING
        </button>
    </div>

    <div id="log" style="background: white; padding: 10px; border-radius: 5px; margin: 20px 0; font-size: 12px; color: #666; max-height: 200px; overflow-y: auto;"></div>

<script>
let recorder;
let chunks = [];
let stream;
let recording = false;
let startTime;
let timer;

function log(msg) {
    console.log(msg);
    const logDiv = document.getElementById('log');
    logDiv.innerHTML += new Date().toLocaleTimeString() + ': ' + msg + '<br>';
    logDiv.scrollTop = logDiv.scrollHeight;
}

function updateStatus(msg, color) {
    const status = document.getElementById('status');
    status.innerHTML = msg;
    status.style.color = color || '#333';
}

// FORCE MICROPHONE - TRY EVERY POSSIBLE METHOD
function record() {
    if (recording) {
        stopRecording();
        return;
    }

    log('🎙️ Starting microphone request...');
    updateStatus('🔄 Requesting microphone...', '#ff8800');
    
    // Try to get microphone using ALL possible methods
    getMicrophone();
}

function getMicrophone() {
    log('📱 Attempting microphone access...');
    
    // Method 1: Modern Promise-based API
    if (window.navigator && navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        log('✅ Trying modern getUserMedia');
        navigator.mediaDevices.getUserMedia({ audio: true })
            .then(gotStream)
            .catch(err => {
                log('❌ Modern API failed: ' + err.message);
                tryLegacy();
            });
        return;
    }
    
    // Method 2: Legacy callback-based API
    tryLegacy();
}

function tryLegacy() {
    log('⚠️ Trying legacy APIs...');
    
    // Get legacy getUserMedia function
    const getUserMedia = navigator.getUserMedia || 
                        navigator.webkitGetUserMedia || 
                        navigator.mozGetUserMedia || 
                        navigator.msGetUserMedia;
    
    if (getUserMedia) {
        log('✅ Found legacy getUserMedia');
        getUserMedia.call(navigator, { audio: true }, gotStream, gotError);
    } else {
        log('❌ No getUserMedia API found');
        // Try one more desperate attempt
        tryDesperateMethod();
    }
}

function tryDesperateMethod() {
    log('🆘 Trying desperate fallback...');
    
    // Check if MediaRecorder exists at all
    if (typeof MediaRecorder !== 'undefined') {
        log('✅ MediaRecorder exists, trying direct approach...');
        
        // Try to create a fake stream and see if browser asks for permission
        try {
            // Sometimes the API exists but is hidden - try to trigger it
            if (navigator.mediaDevices) {
                navigator.mediaDevices.getUserMedia({ audio: true })
                    .then(gotStream)
                    .catch(err => {
                        log('❌ Desperate attempt failed: ' + err.message);
                        showError('No microphone API available on this browser');
                    });
            } else {
                showError('MediaDevices API not available');
            }
        } catch (e) {
            log('❌ Desperate method crashed: ' + e.message);
            showError('Browser does not support audio recording');
        }
    } else {
        log('❌ MediaRecorder not supported');
        showError('Audio recording not supported on this device');
    }
}

function gotStream(audioStream) {
    log('✅ MICROPHONE ACCESS GRANTED!');
    stream = audioStream;
    
    try {
        // Create MediaRecorder
        recorder = new MediaRecorder(stream);
        chunks = [];
        
        recorder.ondataavailable = function(e) {
            if (e.data.size > 0) {
                chunks.push(e.data);
                log('📊 Got audio chunk: ' + e.data.size + ' bytes');
            }
        };
        
        recorder.onstop = function() {
            log('⏹️ Recording stopped');
            processAudio();
        };
        
        // Start recording
        recorder.start(100);
        recording = true;
        startTime = Date.now();
        
        log('🔴 RECORDING STARTED');
        startRecording();
        
        // Auto-stop after 10 seconds
        setTimeout(() => {
            if (recording) {
                log('⏰ Auto-stopping after 10 seconds');
                stopRecording();
            }
        }, 10000);
        
    } catch (e) {
        log('❌ MediaRecorder error: ' + e.message);
        updateStatus('❌ Recording setup failed', '#ff0000');
        stream.getTracks().forEach(track => track.stop());
    }
}

function gotError(err) {
    log('❌ Microphone error: ' + err.name + ' - ' + err.message);
    
    let msg;
    if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
        msg = '❌ Please allow microphone access and try again!';
    } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
        msg = '❌ No microphone found on this device';
    } else if (err.name === 'NotSupportedError') {
        msg = '❌ Audio recording not supported on this browser';
    } else {
        msg = '❌ Microphone access failed: ' + err.message;
    }
    
    showError(msg);
}

function showError(msg) {
    updateStatus(msg, '#ff0000');
    log('❌ Error: ' + msg);
}

function startRecording() {
    const btn = document.getElementById('recordBtn');
    const timerDiv = document.getElementById('timer');
    
    btn.innerHTML = '⏹️<br>STOP';
    btn.style.background = '#28a745';
    btn.style.animation = 'pulse 1s infinite';
    
    updateStatus('🔴 RECORDING - Tap STOP when finished', '#ff0000');
    timerDiv.style.display = 'block';
    
    startTimer();
}

function startTimer() {
    timer = setInterval(() => {
        if (!recording) return;
        
        const elapsed = Math.floor((Date.now() - startTime) / 1000);
        const mins = Math.floor(elapsed / 60);
        const secs = elapsed % 60;
        
        document.getElementById('time').textContent = 
            mins + ':' + secs.toString().padStart(2, '0');
    }, 100);
}

function stopRecording() {
    if (!recording) return;
    
    log('⏹️ Stopping recording...');
    
    recording = false;
    
    if (timer) clearInterval(timer);
    if (recorder) recorder.stop();
    if (stream) stream.getTracks().forEach(track => track.stop());
    
    const btn = document.getElementById('recordBtn');
    btn.innerHTML = '🎙️<br>RECORD';
    btn.style.background = '#ff4444';
    btn.style.animation = 'none';
    
    updateStatus('⏸️ Processing recording...', '#ff8800');
    document.getElementById('timer').style.display = 'none';
}

function processAudio() {
    if (chunks.length === 0) {
        log('❌ No audio data recorded');
        updateStatus('❌ No audio recorded', '#ff0000');
        return;
    }
    
    log('📊 Processing ' + chunks.length + ' audio chunks...');
    
    try {
        const blob = new Blob(chunks, { type: 'audio/webm' });
        window.audioBlob = blob;
        window.audioURL = URL.createObjectURL(blob);
        
        log('✅ Audio processed: ' + blob.size + ' bytes');
        updateStatus('✅ Recording ready! Tap DOWNLOAD', '#28a745');
        document.getElementById('download').style.display = 'block';
        
    } catch (e) {
        log('❌ Processing failed: ' + e.message);
        updateStatus('❌ Processing failed', '#ff0000');
    }
}

function download() {
    if (!window.audioBlob) {
        updateStatus('❌ No recording available', '#ff0000');
        return;
    }
    
    log('💾 Starting download...');
    
    try {
        const a = document.createElement('a');
        a.href = window.audioURL;
        a.download = 'heart_sound_' + new Date().toISOString().slice(0, 19).replace(/:/g, '-') + '.webm';
        a.click();
        
        updateStatus('📥 Download started! Check Downloads folder', '#28a745');
        log('✅ Download initiated');
        
    } catch (e) {
        log('❌ Download failed: ' + e.message);
        updateStatus('❌ Download failed', '#ff0000');
    }
}

// Add pulse animation
const style = document.createElement('style');
style.textContent = `
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
`;
document.head.appendChild(style);

// Initialize
window.addEventListener('load', () => {
    log('🚀 Mobile recorder loaded');
    updateStatus('🎯 Ready! Tap RECORD to start', '#28a745');
});
</script>

</body>
</html>
"""

def main():
    """Absolute minimal mobile recorder."""
    
    st.markdown("# 📱 Heart Sound Recorder - MINIMAL VERSION")
    st.markdown("### 🔧 Works on ANY mobile browser with microphone support")

    # Display the minimal recorder
    components.html(MINIMAL_RECORDER_HTML, height=700, scrolling=True)

    st.markdown("---")
    st.error("🔧 **DEBUGGING VERSION**: Absolute minimal implementation")
    st.info("📱 **This version tries every possible microphone API**")

if __name__ == "__main__":
    main()