"""
Mobile Access Launcher - Easy Mobile URL Generation
Creates shareable links for mobile access to Heart Sound Analyzer
"""

import socket
import webbrowser
import qrcode
from PIL import Image
import io
import base64

def get_local_ip():
    """Get the local IP address for mobile access."""
    try:
        # Connect to a remote address to determine local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "192.168.99.173"  # fallback

def create_mobile_links():
    """Generate mobile access links."""
    local_ip = get_local_ip()
    
    links = {
        "Mobile Analyzer": f"http://{local_ip}:8503",
        "Audio Recorder": f"http://{local_ip}:8502", 
        "Desktop App": f"http://{local_ip}:8501"
    }
    
    return links, local_ip

def generate_shareable_text(links):
    """Generate text that can be easily shared via WhatsApp/SMS."""
    text = """🫀 Heart Sound Analyzer - Mobile Access

📱 Mobile Analyzer (Recommended):
{mobile}

🎙️ Audio Recorder:
{recorder}

🖥️ Desktop Version:
{desktop}

📋 Instructions:
1. Connect phone to same WiFi
2. Copy URL and open in mobile browser
3. Chrome browser recommended
4. Allow microphone for recording

🚀 Features: Ultra-fast AI analysis, mobile recording, 91% model optimization!""".format(
        mobile=links["Mobile Analyzer"],
        recorder=links["Audio Recorder"], 
        desktop=links["Desktop App"]
    )
    
    return text

def create_simple_qr(url, title):
    """Create a simple QR code for mobile access."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=8,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    return img

def main():
    """Main mobile access launcher."""
    print("📱 MOBILE ACCESS LAUNCHER")
    print("=" * 50)
    
    # Get mobile links
    links, local_ip = create_mobile_links()
    
    print(f"🌐 Network IP: {local_ip}")
    print()
    
    # Display all links
    print("📱 MOBILE ACCESS URLS:")
    print("-" * 30)
    for name, url in links.items():
        print(f"{name:.<20} {url}")
    
    print()
    print("📋 EASY SHARING OPTIONS:")
    print("-" * 30)
    
    # Generate shareable text
    shareable_text = generate_shareable_text(links)
    
    # Save to file for easy sharing
    with open("mobile_access.txt", "w") as f:
        f.write(shareable_text)
    
    print("✅ Shareable text saved to: mobile_access.txt")
    print()
    
    # Show shareable content
    print("📄 COPY THIS TEXT TO SHARE:")
    print("=" * 50)
    print(shareable_text)
    print("=" * 50)
    
    # Options menu
    print()
    print("🚀 QUICK ACTIONS:")
    print("1. Press ENTER to open Mobile Analyzer")
    print("2. Type 'r' to open Audio Recorder") 
    print("3. Type 'd' to open Desktop App")
    print("4. Type 'q' to create QR codes")
    print("5. Type 'x' to exit")
    
    while True:
        choice = input("\n👉 Choose action: ").lower().strip()
        
        if choice == "" or choice == "1":
            print("🚀 Opening Mobile Analyzer...")
            webbrowser.open(links["Mobile Analyzer"])
            break
            
        elif choice == "r" or choice == "2":
            print("🎙️ Opening Audio Recorder...")
            webbrowser.open(links["Audio Recorder"])
            break
            
        elif choice == "d" or choice == "3":
            print("🖥️ Opening Desktop App...")
            webbrowser.open(links["Desktop App"])
            break
            
        elif choice == "q" or choice == "4":
            print("📱 Creating QR codes...")
            
            # Create QR codes for each app
            for name, url in links.items():
                qr_img = create_simple_qr(url, name)
                filename = f"qr_{name.lower().replace(' ', '_')}.png"
                qr_img.save(filename)
                print(f"✅ QR code saved: {filename}")
            
            print("📱 QR codes created! Share the PNG files.")
            break
            
        elif choice == "x":
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Try again.")
    
    print()
    print("🎯 Mobile Access Ready!")
    print(f"📱 Recommended: {links['Mobile Analyzer']}")

if __name__ == "__main__":
    main()