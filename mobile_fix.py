"""
Mobile Access Configuration
Final solution to enable mobile QR code access to the Heart Sound Analyzer.
"""

import subprocess
import socket
import time
import sys
import os
from pathlib import Path

def check_admin_rights():
    """Check if running with admin privileges."""
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def get_local_ip():
    """Get the local IP address."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "localhost"

def configure_firewall():
    """Configure Windows Firewall to allow Streamlit ports."""
    if not check_admin_rights():
        print("⚠️ Need Administrator privileges to configure firewall")
        print("💡 Please run as Administrator or manually add firewall rules:")
        print("   1. Open Windows Defender Firewall")
        print("   2. Click 'Allow an app or feature through Windows Defender Firewall'")
        print("   3. Click 'Change Settings' then 'Allow another app...'")
        print("   4. Browse to your Python executable")
        print("   5. Add it with both Private and Public networks checked")
        return False
    
    try:
        # Add firewall rule for Streamlit
        cmd = [
            'netsh', 'advfirewall', 'firewall', 'add', 'rule',
            'name=Heart Analyzer Streamlit',
            'dir=in', 'action=allow', 'protocol=TCP',
            'localport=8501,8502'
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Firewall configured successfully!")
            return True
        else:
            print(f"❌ Firewall configuration failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Firewall configuration error: {e}")
        return False

def start_servers():
    """Start both Streamlit servers with network binding."""
    print("🚀 Starting Heart Sound Analyzer servers...")
    
    # Kill existing processes
    try:
        subprocess.run(['taskkill', '/f', '/im', 'streamlit.exe'], 
                      capture_output=True, check=False)
        time.sleep(2)
    except:
        pass
    
    # Start main analyzer
    cmd1 = [
        sys.executable, '-m', 'streamlit', 'run', 'app.py',
        '--server.port', '8501',
        '--server.address', '0.0.0.0',
        '--server.headless', 'true',
        '--server.runOnSave', 'false'
    ]
    
    # Start mobile recorder
    cmd2 = [
        sys.executable, '-m', 'streamlit', 'run', 'mobile_recorder.py',
        '--server.port', '8502',
        '--server.address', '0.0.0.0',
        '--server.headless', 'true',
        '--server.runOnSave', 'false'
    ]
    
    try:
        # Start both processes
        main_process = subprocess.Popen(cmd1, 
                                       stdout=subprocess.PIPE, 
                                       stderr=subprocess.PIPE)
        mobile_process = subprocess.Popen(cmd2,
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE)
        
        print("⏳ Waiting for servers to start...")
        time.sleep(10)  # Give servers time to start
        
        return main_process, mobile_process
        
    except Exception as e:
        print(f"❌ Failed to start servers: {e}")
        return None, None

def test_connectivity(local_ip):
    """Test server connectivity."""
    import requests
    
    urls = {
        'Main Analyzer (localhost)': f'http://localhost:8501',
        'Mobile Recorder (localhost)': f'http://localhost:8502',
        'Main Analyzer (network)': f'http://{local_ip}:8501',  
        'Mobile Recorder (network)': f'http://{local_ip}:8502'
    }
    
    print(f"\n🔍 Testing connectivity...")
    for name, url in urls.items():
        try:
            response = requests.get(url, timeout=5)
            print(f"✅ {name}: Status {response.status_code}")
        except requests.exceptions.ConnectTimeout:
            print(f"⏰ {name}: Timeout")
        except requests.exceptions.ConnectionError:
            print(f"❌ {name}: Connection refused")
        except Exception as e:
            print(f"⚠️ {name}: {e}")

def main():
    """Main configuration function."""
    print("🫀 Heart Sound Analyzer - Mobile Access Configuration")
    print("=" * 60)
    
    # Get network info
    local_ip = get_local_ip()
    print(f"🌐 Local IP: {local_ip}")
    
    # Check if required files exist
    if not Path('app.py').exists() or not Path('mobile_recorder.py').exists():
        print("❌ Required files not found!")
        return
    
    # Configure firewall
    print("\n⚙️ Configuring network access...")
    configure_firewall()
    
    # Start servers
    main_proc, mobile_proc = start_servers()
    
    if main_proc and mobile_proc:
        # Test connectivity
        test_connectivity(local_ip)
        
        # Show final URLs
        print(f"\n🎯 Access URLs:")
        print(f"📊 Main Analyzer: http://{local_ip}:8501")
        print(f"📱 Mobile Recorder: http://{local_ip}:8502")
        
        print(f"\n📱 Mobile QR Instructions:")
        print(f"1. Open main analyzer: http://{local_ip}:8501")
        print(f"2. Scroll down to find QR code")
        print(f"3. Scan QR code with phone camera")
        print(f"4. Your phone should open: http://{local_ip}:8502")
        
        print(f"\n🛠️ Troubleshooting:")
        print(f"- Ensure phone and computer are on same WiFi network")
        print(f"- If still not working, try mobile hotspot from phone")
        print(f"- Check Windows Firewall settings if connection fails")
        
        print(f"\n⏹️ Press Ctrl+C to stop servers")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping servers...")
            main_proc.terminate()
            mobile_proc.terminate()
            subprocess.run(['taskkill', '/f', '/im', 'streamlit.exe'], 
                          capture_output=True, check=False)
            print("✅ Servers stopped!")

if __name__ == "__main__":
    main()