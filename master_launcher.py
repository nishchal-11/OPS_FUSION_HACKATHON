"""
Master Launcher - Fixed Version for Heart Sound Analyzer
Launches both main analyzer and mobile recorder with proper network access.
"""

import subprocess
import time
import sys
import socket
import requests
from pathlib import Path

def get_local_ip():
    """Get the local IP address for network access."""
    try:
        # Connect to a remote server to get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "localhost"

def check_port(port):
    """Check if a port is already in use."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(('localhost', port))
        return True  # Port is in use
    except:
        return False  # Port is available

def kill_streamlit_processes():
    """Kill any existing Streamlit processes."""
    try:
        subprocess.run(['taskkill', '/f', '/im', 'streamlit.exe'], 
                      capture_output=True, check=False)
        print("🧹 Cleared existing Streamlit processes")
        time.sleep(2)
    except Exception as e:
        print(f"⚠️ Could not kill processes: {e}")

def start_app(app_name, port):
    """Start a Streamlit app with proper network binding."""
    cmd = [
        sys.executable, '-m', 'streamlit', 'run', app_name,
        '--server.port', str(port),
        '--server.address', '0.0.0.0',
        '--server.headless', 'true'
    ]
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print(f"🚀 Starting {app_name} on port {port}...")
        return process
    except Exception as e:
        print(f"❌ Failed to start {app_name}: {e}")
        return None

def wait_for_server(port, timeout=30):
    """Wait for server to become available."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f'http://localhost:{port}', timeout=5)
            if response.status_code == 200:
                return True
        except:
            pass
        time.sleep(1)
    return False

def main():
    """Main launcher function."""
    print("🫀 Heart Sound Analyzer - Master Launcher")
    print("=" * 50)
    
    # Get network info
    local_ip = get_local_ip()
    print(f"🌐 Local IP: {local_ip}")
    
    # Clean up existing processes
    kill_streamlit_processes()
    
    # Check if files exist
    if not Path('app.py').exists():
        print("❌ app.py not found!")
        return
    
    if not Path('mobile_recorder.py').exists():
        print("❌ mobile_recorder.py not found!")
        return
    
    # Start applications
    print("\n🚀 Starting applications...")
    
    # Start main analyzer
    main_process = start_app('app.py', 8501)
    if main_process:
        print("⏳ Waiting for main analyzer...")
        if wait_for_server(8501):
            print("✅ Main analyzer ready!")
        else:
            print("❌ Main analyzer failed to start")
    
    # Start mobile recorder
    mobile_process = start_app('mobile_recorder.py', 8502)
    if mobile_process:
        print("⏳ Waiting for mobile recorder...")
        if wait_for_server(8502):
            print("✅ Mobile recorder ready!")
        else:
            print("❌ Mobile recorder failed to start")
    
    # Show access URLs
    print("\n🎯 Access URLs:")
    print(f"📊 Main Analyzer: http://localhost:8501")
    print(f"📱 Mobile Recorder: http://localhost:8502")
    
    if local_ip != "localhost":
        print(f"\n🌐 Network Access (for mobile):")
        print(f"📊 Main Analyzer: http://{local_ip}:8501")
        print(f"📱 Mobile Recorder: http://{local_ip}:8502")
    
    print("\n🎉 Both applications are running!")
    print("📱 Scan QR code from main analyzer to access mobile recorder")
    print("⏹️ Press Ctrl+C to stop all servers")
    
    try:
        # Keep processes running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping servers...")
        if main_process:
            main_process.terminate()
        if mobile_process:
            mobile_process.terminate()
        kill_streamlit_processes()
        print("✅ All servers stopped!")

if __name__ == "__main__":
    main()