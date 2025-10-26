#!/usr/bin/env python3
"""
Start script for RAG Agent with Streamlit frontend
"""
import subprocess
import sys
import time
import os
import platform
from pathlib import Path

def kill_port_8000():
    """Kill any existing processes on port 8000"""
    print("🔍 Checking for existing processes on port 8000...")
    try:
        if platform.system() == "Windows":
            # Find processes using port 8000
            result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
            lines = result.stdout.split('\n')
            for line in lines:
                if ':8000' in line and 'LISTENING' in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        pid = parts[-1]
                        print(f"🔪 Killing process {pid} on port 8000...")
                        subprocess.run(['taskkill', '/PID', pid, '/F'], capture_output=True)
        else:
            # For Unix-like systems
            subprocess.run(['pkill', '-f', 'fastapi_backend.py'], capture_output=True)
        print("✅ Port 8000 is now free")
    except Exception as e:
        print(f"⚠️  Could not check/kill port 8000 processes: {e}")

def start_backend():
    """Start the FastAPI backend"""
    print("🚀 Starting FastAPI Backend...")
    backend_process = subprocess.Popen([
        sys.executable, "fastapi_backend.py"
    ], cwd=Path(__file__).parent / "src")
    return backend_process

def start_streamlit():
    """Start the Streamlit frontend"""
    print("🎨 Starting Streamlit Frontend...")
    streamlit_process = subprocess.Popen([
        sys.executable, "-m", "streamlit", "run", "streamlit_app.py"
    ], cwd=Path(__file__).parent)
    return streamlit_process

def main():
    print("=" * 50)
    print("📚 RAG Agent - Streamlit Frontend")
    print("=" * 50)
    
    try:
        # Kill any existing processes on port 8000
        kill_port_8000()
        
        # Start backend
        backend_proc = start_backend()
        
        # Wait a bit for backend to start
        print("⏳ Waiting for backend to initialize...")
        time.sleep(3)
        
        # Start Streamlit
        streamlit_proc = start_streamlit()
        
        print("\n✅ Services started successfully!")
        print("🔗 FastAPI Backend: http://localhost:8000")
        print("🔗 Streamlit Frontend: http://localhost:8501")
        print("\n📝 Press Ctrl+C to stop both services")
        
        # Wait for processes
        try:
            backend_proc.wait()
            streamlit_proc.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping services...")
            backend_proc.terminate()
            streamlit_proc.terminate()
            print("✅ Services stopped")
            
    except Exception as e:
        print(f"❌ Error starting services: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()