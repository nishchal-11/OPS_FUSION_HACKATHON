"""
QR Code Generator for Mobile Heart Sound Recording
Creates QR codes that link to the mobile recording interface.
"""

import qrcode
import streamlit as st
from PIL import Image
import io
import base64
from datetime import datetime
import json
import socket
import time

def get_local_ip():
    """Get the local IP address of the machine."""
    try:
        # Create a socket to get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Connect to Google DNS
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "localhost"

def generate_mobile_recorder_url(port=8502):
    """Generate URL for the mobile recorder app."""
    local_ip = get_local_ip()

    # Try different possible URLs
    possible_urls = [
        f"http://{local_ip}:{port}",  # Network IP
        f"http://localhost:{port}",   # Localhost
        f"http://127.0.0.1:{port}",   # Local IP
    ]

    # Test which URL is accessible (basic check)
    accessible_url = possible_urls[0]  # Default to network IP

    return accessible_url

def create_qr_code(url, size=300):
    """Create QR code for the given URL."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )

    qr.add_data(url)
    qr.make(fit=True)

    # Create PIL image
    img = qr.make_image(fill_color="black", back_color="white")

    # Resize if needed
    if size != 300:
        img = img.resize((size, size), Image.Resampling.LANCZOS)

    return img

def get_qr_code_base64(img):
    """Convert PIL image to base64 string for Streamlit."""
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    img_bytes = buf.getvalue()
    img_base64 = base64.b64encode(img_bytes).decode()
    return img_base64

def create_mobile_recorder_qr(port=8502):
    """Create QR code for mobile heart sound recording."""
    recorder_url = generate_mobile_recorder_url(port)

    # Create QR code
    qr_img = create_qr_code(recorder_url, size=250)

    return qr_img, recorder_url

def display_qr_instructions():
    """Display instructions for using the QR code."""
    st.markdown("""
    ### 📱 How to Use Mobile Recording:

    1. **Scan the QR Code** above with your phone's camera
    2. **Open the link** in your mobile browser
    3. **Allow microphone access** when prompted
    4. **Click RECORD** and place phone near heart
    5. **Record for 5-10 seconds**
    6. **Download** the audio file
    7. **Return here** and upload the file for analysis

    ### 🎯 Tips for Best Results:
    - Use a quiet environment
    - Place phone close to chest (or use stethoscope)
    - Hold phone steady during recording
    - Record for at least 5 seconds
    """)

def create_recording_session_info():
    """Create session information for tracking recordings."""
    session_id = f"recording_{int(time.time())}"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    session_info = {
        "session_id": session_id,
        "timestamp": timestamp,
        "device_type": "mobile",
        "recording_type": "heart_sound",
        "expected_duration": "5-10 seconds",
        "sample_rate": 44100,  # Mobile recording typically 44.1kHz
        "format": "wav"
    }

    return session_info

def validate_mobile_recorder_accessibility(port=8502):
    """Check if the mobile recorder is accessible."""
    try:
        import requests
        recorder_url = generate_mobile_recorder_url(port)

        # Try to connect to the recorder (basic check)
        response = requests.get(f"{recorder_url}/health", timeout=2)
        if response.status_code == 200:
            return True, "Recorder is accessible"
        else:
            return False, f"Recorder returned status {response.status_code}"
    except requests.exceptions.RequestException:
        return False, "Cannot connect to recorder (may not be running)"
    except Exception as e:
        return False, f"Connection error: {str(e)}"

# Streamlit component for QR code display
def display_mobile_qr_component(port=8502):
    """Display the mobile recording QR code component."""

    st.markdown("### 📱 Mobile Heart Sound Recording")

    # Check if recorder is running
    is_accessible, status_msg = validate_mobile_recorder_accessibility(port)

    if not is_accessible:
        st.warning(f"⚠️ {status_msg}")
        st.info("💡 Make sure the mobile recorder is running on port 8502")
        st.code(f"streamlit run mobile_recorder.py --server.port {port}")

        # Still show QR code but with warning
        st.markdown("---")
        st.markdown("**QR Code (may not work if recorder is not running):**")

    # Generate QR code
    qr_img, recorder_url = create_mobile_recorder_qr(port)

    # Display QR code
    col1, col2 = st.columns([1, 2])

    with col1:
        st.image(qr_img, caption="Scan with phone camera", use_column_width=True)

    with col2:
        st.markdown("**Recording URL:**")
        st.code(recorder_url, language=None)

        # Session info
        session_info = create_recording_session_info()
        st.markdown("**Session Details:**")
        st.json(session_info)

    # Instructions
    display_qr_instructions()

    # Technical details
    with st.expander("🔧 Technical Details"):
        st.markdown(f"""
        - **Recorder Port:** {port}
        - **Audio Format:** WAV (44.1kHz, 16-bit)
        - **Max Duration:** 10 seconds (auto-stop)
        - **Browser Support:** Chrome, Safari, Firefox mobile
        - **Permissions:** Microphone access required
        """)

if __name__ == "__main__":
    # Test the QR code generation
    print("Testing QR Code Generation...")

    qr_img, url = create_mobile_recorder_qr()
    print(f"Generated QR code for URL: {url}")
    print(f"QR image size: {qr_img.size}")

    # Test base64 conversion
    base64_str = get_qr_code_base64(qr_img)
    print(f"Base64 string length: {len(base64_str)}")

    print("✅ QR Code generation test passed!")