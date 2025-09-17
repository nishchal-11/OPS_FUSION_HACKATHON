"""
Mobile Access Test Script
Tests if the mobile recorder is accessible from network devices.
"""

import requests
import socket
from qr_generator import get_local_ip, generate_mobile_recorder_url, create_mobile_recorder_qr

def test_mobile_access():
    """Test mobile recorder accessibility."""
    print("🔍 Testing Mobile Access...")
    print("=" * 50)
    
    # Get network information
    local_ip = get_local_ip()
    print(f"📡 Local IP Address: {local_ip}")
    
    # Generate URLs
    mobile_url = generate_mobile_recorder_url()
    print(f"📱 Mobile Recorder URL: {mobile_url}")
    
    # Test main analyzer
    main_url = f"http://{local_ip}:8501"
    print(f"🖥️  Main Analyzer URL: {main_url}")
    
    print("\n" + "=" * 50)
    print("📋 INSTRUCTIONS FOR MOBILE ACCESS:")
    print("=" * 50)
    
    print(f"1. 📱 On your phone, open browser and go to:")
    print(f"   {mobile_url}")
    print()
    print(f"2. 🖥️  On your computer, go to:")
    print(f"   {main_url}")
    print()
    print(f"3. 📲 Scan QR code from main app to access mobile recorder")
    print()
    
    # Test connectivity
    print("🔧 CONNECTIVITY TESTS:")
    print("-" * 30)
    
    def test_url(url, name):
        try:
            response = requests.get(url, timeout=5)
            status = "✅ ACCESSIBLE" if response.status_code == 200 else f"⚠️  Status: {response.status_code}"
            print(f"{name}: {status}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"{name}: ❌ NOT ACCESSIBLE - {str(e)}")
            return False
    
    mobile_ok = test_url(mobile_url, "Mobile Recorder")
    main_ok = test_url(main_url, "Main Analyzer")
    
    print("\n" + "=" * 50)
    if mobile_ok and main_ok:
        print("🎉 SUCCESS: Both apps are accessible!")
        print("📱 Your phone should be able to access the mobile recorder.")
        print(f"🔗 Direct mobile link: {mobile_url}")
    else:
        print("❌ ISSUES DETECTED:")
        if not mobile_ok:
            print("   - Mobile recorder not accessible")
        if not main_ok:
            print("   - Main analyzer not accessible")
        print("\n💡 TROUBLESHOOTING:")
        print("   1. Make sure both phone and computer are on same WiFi")
        print("   2. Check Windows Firewall settings")
        print("   3. Try restarting the Streamlit servers")
    
    print("=" * 50)

if __name__ == "__main__":
    test_mobile_access()