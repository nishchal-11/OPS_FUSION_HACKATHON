"""
Simple Mobile URL Generator
Get the URLs you need for mobile access
"""

import socket

def get_local_ip():
    """Get the local IP address for mobile access."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "192.168.99.173"

def main():
    local_ip = get_local_ip()
    
    print("MOBILE ACCESS URLS")
    print("=" * 40)
    print(f"Network IP: {local_ip}")
    print()
    
    print("COPY THESE URLS TO YOUR PHONE:")
    print("-" * 40)
    print(f"Mobile App:     http://{local_ip}:8503")
    print(f"Audio Recorder: http://{local_ip}:8502")  
    print(f"Desktop App:    http://{local_ip}:8501")
    print()
    
    print("HOW TO USE ON MOBILE:")
    print("-" * 40)
    print("1. Connect phone to same WiFi as computer")
    print("2. Copy the Mobile App URL above")
    print("3. Send URL to phone via WhatsApp/SMS/Email")
    print("4. Open URL in mobile browser (Chrome recommended)")
    print("5. Bookmark for easy access!")
    print()
    
    print("RECOMMENDED FOR DEMO:")
    print("-" * 40)
    print(f"USE THIS URL: http://{local_ip}:8503")
    print("- Ultra-fast TFLite inference (14ms)")
    print("- Mobile-optimized interface")
    print("- Touch-friendly design")
    print("- Perfect for hackathon presentations!")

if __name__ == "__main__":
    main()