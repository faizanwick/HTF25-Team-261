#!/usr/bin/env python3
"""
VoiceCode Server Startup Script
Run this script to start the Voice-Enabled Code Assistant server
"""

import uvicorn
import os
import sys

def main():
    print("🚀 Starting VoiceCode - Voice-Enabled Code Assistant")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("app/main.py"):
        print("❌ Error: app/main.py not found. Please run this script from the project root directory.")
        sys.exit(1)
    
    # Create workspace directory if it doesn't exist
    workspace_dir = "workspace"
    if not os.path.exists(workspace_dir):
        os.makedirs(workspace_dir)
        print(f"📁 Created workspace directory: {workspace_dir}")
    
    print("🌐 Server will be available at: http://localhost:8000")
    print("📖 API documentation: http://localhost:8000/docs")
    print("🎤 Voice commands will be processed via WebSocket")
    print("=" * 50)
    
    try:
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
