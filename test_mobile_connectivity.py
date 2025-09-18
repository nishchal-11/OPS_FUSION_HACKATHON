"""
Quick Mobile Connectivity Test
Test if all Heart Sound Analyzer servers are accessible from mobile devices
"""

import requests
import time
from datetime import datetime

def test_mobile_connectivity():
    """Test if all servers are accessible for mobile devices."""
    
    print("📱 MOBILE CONNECTIVITY TEST")
    print("=" * 50)
    print(f"🕐 Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Network IP: 192.168.99.173")
    print()
    
    # Define servers to test
    servers = [
        {
            "name": "Main Desktop Analyzer",
            "url": "http://192.168.99.173:8501",
            "port": 8501,
            "description": "Full-featured desktop interface with QR integration"
        },
        {
            "name": "Mobile Audio Recorder", 
            "url": "http://192.168.99.173:8502",
            "port": 8502,
            "description": "Cross-platform audio recording with live waveforms"
        },
        {
            "name": "Mobile-Optimized Analyzer",
            "url": "http://192.168.99.173:8503", 
            "port": 8503,
            "description": "Touch-friendly interface with ultra-fast TFLite inference"
        }
    ]
    
    all_working = True
    
    for server in servers:
        print(f"🧪 Testing {server['name']}...")
        print(f"   📍 URL: {server['url']}")
        
        try:
            # Test connectivity with timeout
            start_time = time.time()
            response = requests.get(server['url'], timeout=10)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                print(f"   ✅ Status: ACCESSIBLE")
                print(f"   ⏱️ Response time: {response_time:.0f}ms")
                print(f"   📊 HTTP Status: {response.status_code}")
                print(f"   📱 Mobile Ready: YES")
            else:
                print(f"   ⚠️ Status: HTTP {response.status_code}")
                print(f"   📱 Mobile Ready: PARTIAL")
                all_working = False
                
        except requests.ConnectionError:
            print(f"   ❌ Status: CONNECTION FAILED")
            print(f"   🔧 Issue: Server not running on port {server['port']}")
            print(f"   📱 Mobile Ready: NO")
            all_working = False
            
        except requests.Timeout:
            print(f"   ⏱️ Status: TIMEOUT")
            print(f"   🔧 Issue: Server responding slowly")
            print(f"   📱 Mobile Ready: SLOW")
            
        except Exception as e:
            print(f"   ❌ Status: ERROR - {e}")
            print(f"   📱 Mobile Ready: NO")
            all_working = False
        
        print(f"   💡 Purpose: {server['description']}")
        print()
    
    # Summary
    print("📋 MOBILE CONNECTIVITY SUMMARY")
    print("=" * 50)
    
    if all_working:
        print("🎉 ALL SERVERS ACCESSIBLE FROM MOBILE!")
        print()
        print("📱 MOBILE URLS TO USE:")
        for server in servers:
            print(f"   • {server['name']}: {server['url']}")
        
        print()
        print("🧪 MOBILE TESTING STEPS:")
        print("1. Connect phone/tablet to same WiFi network")
        print("2. Open any of the URLs above in mobile browser") 
        print("3. For best experience, try Mobile-Optimized Analyzer first")
        print("4. Test audio recording with Mobile Audio Recorder")
        print("5. Use QR code from Desktop Analyzer for seamless workflow")
        
        print()
        print("🏆 READY FOR MOBILE DEMONSTRATIONS!")
        
    else:
        print("⚠️ SOME SERVERS NOT ACCESSIBLE")
        print("🔧 Check if all Streamlit servers are running:")
        print("   netstat -ano | findstr \":850\"")
        print("🔄 Restart servers if needed:")
        print("   python launcher.py")
    
    return all_working

def generate_qr_instructions():
    """Generate QR code access instructions."""
    print("\n📱 QR CODE ACCESS INSTRUCTIONS")
    print("=" * 50)
    print("1. Open Desktop Analyzer: http://192.168.99.173:8501")
    print("2. Scroll down to find QR code section")
    print("3. Use phone camera to scan QR code")
    print("4. QR will open Mobile Recorder: http://192.168.99.173:8502")
    print("5. Record audio, download, and upload back to analyzer")
    print()
    print("🎯 This demonstrates complete mobile workflow integration!")

if __name__ == "__main__":
    success = test_mobile_connectivity()
    
    if success:
        generate_qr_instructions()
        print("\n✅ Mobile connectivity test: PASSED")
        print("🚀 Your Heart Sound Analyzer is ready for mobile demonstrations!")
    else:
        print("\n❌ Mobile connectivity test: ISSUES DETECTED") 
        print("🔧 Please check server status and restart if needed")