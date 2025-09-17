#!/usr/bin/env python3
"""
Heart Sound Analyzer Launcher
Starts both the main analyzer and mobile recorder applications.
"""

import subprocess
import sys
import time
import os
import signal
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are installed."""
    required_modules = [
        'streamlit', 'tensorflow', 'librosa', 'numpy', 'pandas',
        'matplotlib', 'qrcode', 'PIL', 'requests'
    ]

    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)

    if missing_modules:
        print(f"❌ Missing dependencies: {', '.join(missing_modules)}")
        print("Please run: pip install -r requirements.txt")
        return False

    print("✅ All dependencies are installed")
    return True

def start_mobile_recorder(port=8502):
    """Start the mobile recorder application."""
    print(f"🚀 Starting Mobile Recorder on port {port}...")

    try:
        cmd = [
            sys.executable, "-m", "streamlit", "run", "mobile_recorder.py",
            "--server.port", str(port),
            "--server.headless", "true",
            "--server.address", "0.0.0.0"
        ]

        process = subprocess.Popen(
            cmd,
            cwd=os.getcwd(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        print(f"✅ Mobile Recorder started (PID: {process.pid})")
        return process

    except Exception as e:
        print(f"❌ Failed to start Mobile Recorder: {e}")
        return None

def start_main_analyzer(port=8501):
    """Start the main analyzer application."""
    print(f"🚀 Starting Main Analyzer on port {port}...")

    try:
        cmd = [
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", str(port),
            "--server.headless", "true",
            "--server.address", "0.0.0.0"
        ]

        process = subprocess.Popen(
            cmd,
            cwd=os.getcwd(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        print(f"✅ Main Analyzer started (PID: {process.pid})")
        return process

    except Exception as e:
        print(f"❌ Failed to start Main Analyzer: {e}")
        return None

def wait_for_servers(processes, timeout=30):
    """Wait for servers to start up."""
    print("⏳ Waiting for servers to initialize...")

    start_time = time.time()
    while time.time() - start_time < timeout:
        all_ready = True

        for name, (process, port) in processes.items():
            if process.poll() is not None:  # Process has terminated
                print(f"❌ {name} process terminated unexpectedly")
                return False

        # Check if servers are responding (basic check)
        try:
            import requests
            for name, (process, port) in processes.items():
                try:
                    response = requests.get(f"http://localhost:{port}/health", timeout=1)
                    if response.status_code == 200:
                        print(f"✅ {name} is responding on port {port}")
                    else:
                        all_ready = False
                except:
                    all_ready = False

            if all_ready:
                print("🎉 All servers are ready!")
                return True

        except ImportError:
            # requests not available, just wait
            pass

        time.sleep(2)

    print("⚠️ Timeout waiting for servers to start")
    return False

def cleanup_processes(processes):
    """Clean up running processes."""
    print("🧹 Cleaning up processes...")

    for name, (process, port) in processes.items():
        try:
            if process.poll() is None:  # Still running
                print(f"Stopping {name}...")
                if os.name == 'nt':  # Windows
                    process.terminate()
                else:  # Unix/Linux
                    os.kill(process.pid, signal.SIGTERM)
                    time.sleep(1)
                    if process.poll() is None:
                        os.kill(process.pid, signal.SIGKILL)
        except Exception as e:
            print(f"Error stopping {name}: {e}")

def main():
    """Main launcher function."""
    print("=" * 60)
    print("🫀 HEART SOUND ANALYZER LAUNCHER")
    print("=" * 60)

    # Check dependencies
    if not check_dependencies():
        return 1

    # Define server configurations
    servers = {
        "Main Analyzer": (8501, start_main_analyzer),
        "Mobile Recorder": (8502, start_mobile_recorder)
    }

    processes = {}

    try:
        # Start servers
        for name, (port, start_func) in servers.items():
            process = start_func(port)
            if process is None:
                print(f"❌ Failed to start {name}")
                cleanup_processes(processes)
                return 1
            processes[name] = (process, port)

        print()
        print("📋 Server Information:")
        print("-" * 30)
        for name, (process, port) in processes.items():
            print(f"{name}: http://localhost:{port}")
        print()

        # Wait for servers to be ready
        if wait_for_servers(processes):
            print()
            print("🎯 ACCESS URLs:")
            print("-" * 30)
            print("📊 Main Analyzer: http://localhost:8501")
            print("📱 Mobile Recorder: http://localhost:8502")
            print()
            print("📱 Mobile Access:")
            print("-" * 30)

            # Get network IP for mobile access
            try:
                import socket
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                network_ip = s.getsockname()[0]
                s.close()
                print(f"📱 Mobile Analyzer: http://{network_ip}:8501")
                print(f"📱 Mobile Recorder: http://{network_ip}:8502")
            except:
                print("📱 (Network IP detection failed)")

            print()
            print("💡 Instructions:")
            print("- Open the Main Analyzer in your browser")
            print("- Scan the QR code with your phone for mobile recording")
            print("- Press Ctrl+C to stop all servers")
            print()

            # Keep running until interrupted
            try:
                while True:
                    time.sleep(1)
                    # Check if any process has died
                    for name, (process, port) in processes.items():
                        if process.poll() is not None:
                            print(f"⚠️ {name} process has stopped")
                            return 1
            except KeyboardInterrupt:
                print("\n🛑 Shutdown requested by user")
                cleanup_processes(processes)
                return 0

        else:
            print("❌ Servers failed to start properly")
            cleanup_processes(processes)
            return 1

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        cleanup_processes(processes)
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)