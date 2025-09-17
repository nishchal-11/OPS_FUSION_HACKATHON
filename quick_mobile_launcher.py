"""
Quick Mobile Fix Launcher
Starts both Streamlit apps with proper network binding for mobile access.
"""

import subprocess
import time
import sys
import socket
import requests
from threading import Thread

def get_local_ip():
    """Get the local IP address."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "192.168.20.28"  # Fallback to known IP

def start_mobile_recorder():
    """Start mobile recorder app."""
    print("🎙️ Starting Mobile Recorder...")
    cmd = [
        sys.executable, "-m", "streamlit", "run", "mobile_recorder.py",
        "--server.port", "8502",
        "--server.address", "0.0.0.0",
        "--server.headless", "true"
    ]
    return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def start_main_analyzer():
    """Start main analyzer app."""
    print("🖥️ Starting Main Analyzer...")
    cmd = [
        sys.executable, "-m", "streamlit", "run", "app.py",
        "--server.port", "8501",
        "--server.address", "0.0.0.0",
        "--server.headless", "true"
    ]
    return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def test_connectivity(url, max_attempts=10):
    """Test if URL is accessible."""
    for i in range(max_attempts):
        try:
            response = requests.get(url, timeout=3)
            if response.status_code == 200:
                return True
        except:
            pass
        time.sleep(2)
        print(f"   Attempt {i+1}/{max_attempts}...")
    return False

def main():
    print("🚀 MOBILE HEART SOUND ANALYZER LAUNCHER")
    print("=" * 50)
    
    # Get network info
    local_ip = get_local_ip()
    print(f"📡 Network IP: {local_ip}")
    
    # Start both apps
    mobile_process = start_mobile_recorder()
    main_process = start_main_analyzer()
    
    print("\n⏳ Waiting for servers to start...")
    time.sleep(5)
    
    # Test connectivity
    mobile_url = f"http://{local_ip}:8502"
    main_url = f"http://{local_ip}:8501"
    
    print(f"\n🔍 Testing Mobile Recorder ({mobile_url})...")
    mobile_ok = test_connectivity(mobile_url)
    
    print(f"\n🔍 Testing Main Analyzer ({main_url})...")
    main_ok = test_connectivity(main_url)
    
    print("\n" + "=" * 50)
    print("📋 RESULTS:")
    print("=" * 50)
    
    if mobile_ok:
        print(f"✅ Mobile Recorder: {mobile_url}")
    else:
        print(f"❌ Mobile Recorder: FAILED")
    
    if main_ok:
        print(f"✅ Main Analyzer: {main_url}")
    else:
        print(f"❌ Main Analyzer: FAILED")
    
    if mobile_ok and main_ok:
        print("\n🎉 SUCCESS! Both apps are running!")
        print(f"📱 Mobile Link: {mobile_url}")
        print(f"🖥️  Desktop Link: {main_url}")
        print("\n📋 MOBILE INSTRUCTIONS:")
        print("1. Connect your phone to the same WiFi network")
        print(f"2. Open your phone's browser and go to: {mobile_url}")
        print("3. Grant microphone permission when asked")
        print("4. Record heart sounds and download the audio file")
        print(f"5. Upload the file at: {main_url}")
        
        print("\n⚠️  Keep this terminal open to keep servers running!")
        print("Press Ctrl+C to stop both servers.")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping servers...")
            mobile_process.terminate()
            main_process.terminate()
            print("✅ Servers stopped.")
    else:
        print(f"\n❌ Some servers failed to start!")
        mobile_process.terminate()
        main_process.terminate()

if __name__ == "__main__":
    main()