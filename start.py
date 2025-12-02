#!/usr/bin/env python3
"""Cross-platform startup script for Hospitality Bot."""
import subprocess
import sys
import time
import signal
import os
from pathlib import Path

def check_env_file():
    """Check if .env.local exists."""
    if not Path(".env.local").exists():
        print("⚠️  Warning: .env.local not found. Please create it from .env.local.example")
        print("   Some features may not work without proper configuration.")
        return False
    return True

def cleanup_processes(processes):
    """Cleanup all processes on exit."""
    print("\n🛑 Shutting down...")
    for proc in processes:
        try:
            proc.terminate()
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        except Exception:
            pass

def main():
    """Main startup function."""
    print("🚀 Starting Hospitality Bot...")
    
    # Check environment file
    check_env_file()
    
    processes = []
    
    def signal_handler(sig, frame):
        cleanup_processes(processes)
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Start FastAPI server
        print("📡 Starting FastAPI server...")
        api_process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        processes.append(api_process)
        print(f"   FastAPI server started (PID: {api_process.pid})")
        print("   API available at: http://localhost:8000")
        print("   API docs at: http://localhost:8000/docs")
        
        # Wait a bit for API to start
        time.sleep(2)
        
        # Start LiveKit agent
        print("🤖 Starting LiveKit agent...")
        agent_process = subprocess.Popen(
            [sys.executable, "entrypoint.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        processes.append(agent_process)
        print(f"   LiveKit agent started (PID: {agent_process.pid})")
        
        print("")
        print("✅ Both services are running!")
        print("")
        print("Press Ctrl+C to stop all services")
        print("")
        
        # Wait for processes
        while True:
            # Check if processes are still alive
            for proc in processes:
                if proc.poll() is not None:
                    print(f"⚠️  Process {proc.pid} exited unexpectedly")
                    cleanup_processes(processes)
                    sys.exit(1)
            time.sleep(1)
            
    except KeyboardInterrupt:
        cleanup_processes(processes)
    except Exception as e:
        print(f"❌ Error: {e}")
        cleanup_processes(processes)
        sys.exit(1)

if __name__ == "__main__":
    main()

