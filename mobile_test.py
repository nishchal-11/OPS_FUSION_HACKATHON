"""
Mobile Connectivity Test
Tests if the mobile recorder is accessible on the network.
"""

import requests
import socket
import time

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

def test_connectivity():
    """Test if servers are accessible."""
    local_ip = get_local_ip()
    
    print(f"🌐 Testing connectivity for IP: {local_ip}")
    
    # Test URLs
    urls = [
        f"http://localhost:8501",
        f"http://localhost:8502", 
        f"http://{local_ip}:8501",
        f"http://{local_ip}:8502"
    ]
    
    for url in urls:
        try:
            response = requests.get(url, timeout=5)
            print(f"✅ {url} - Status: {response.status_code}")
        except requests.exceptions.ConnectTimeout:
            print(f"⏰ {url} - Timeout")
        except requests.exceptions.ConnectionError:
            print(f"❌ {url} - Connection refused")
        except Exception as e:
            print(f"⚠️ {url} - Error: {e}")

if __name__ == "__main__":
    test_connectivity()