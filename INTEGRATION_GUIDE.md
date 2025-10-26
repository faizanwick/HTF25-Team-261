# VoiceCode Integration Guide

## Overview
This guide explains how the frontend and backend are integrated in the VoiceCode Voice-Enabled Code Assistant project.

## Architecture

### Frontend (template/index.html)
- **Technology**: HTML5, CSS3, JavaScript (Vanilla)
- **Styling**: Tailwind CSS with custom glassmorphism effects
- **Features**: 
  - Modern IDE-like interface
  - Real-time voice command processing
  - File management
  - Code editor with syntax highlighting
  - WebSocket communication

### Backend (FastAPI)
- **Framework**: FastAPI with Python 3.8+
- **Features**:
  - RESTful API endpoints
  - WebSocket support for real-time communication
  - File management system
  - Voice command processing
  - CORS enabled for frontend integration

## Integration Points

### 1. Static File Serving
- The FastAPI server serves the HTML frontend at the root URL (`/`)
- Static files are mounted at `/static/`
- CORS middleware allows cross-origin requests

### 2. API Endpoints

#### Voice Commands (`/voice/`)
- `POST /voice/process` - Process voice commands
- `GET /voice/status` - Get voice recognition status
- `POST /voice/toggle` - Toggle voice recognition on/off
- `GET /voice/commands` - Get available voice commands

#### File Management (`/code/`)
- `GET /code/files` - List all files
- `GET /code/files/{file_path}` - Read file content
- `POST /code/files` - Create new file
- `PUT /code/files/{file_path}` - Update file content
- `DELETE /code/files/{file_path}` - Delete file
- `POST /code/run/{file_path}` - Execute Python files

#### WebSocket (`/ws/`)
- `WebSocket /ws/ws` - Real-time communication for voice commands

### 3. Frontend-Backend Communication

#### REST API Calls
```javascript
// Voice command processing
const response = await fetch(`${apiBaseUrl}/voice/process`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ command: command, language: language })
});

// File operations
const response = await fetch(`${apiBaseUrl}/code/files/${filename}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content: content })
});
```

#### WebSocket Communication
```javascript
// Initialize WebSocket connection
const websocket = new WebSocket(`${protocol}//${window.location.host}/ws/ws`);

// Send voice command
websocket.send(JSON.stringify({
    type: 'voice_command',
    command: 'create a function'
}));

// Receive responses
websocket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    if (data.type === 'voice_response') {
        handleVoiceResponse(data);
    }
};
```

## Running the Application

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation
1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
python run_server.py
```

3. Open your browser and navigate to:
   - Main application: http://localhost:8000
   - API documentation: http://localhost:8000/docs

### Development
- The server runs with auto-reload enabled
- Frontend changes require browser refresh
- Backend changes are automatically reloaded

## Features

### Voice Commands
- "Create a function" - Generates function templates
- "Add a loop" - Creates loop structures
- "Add a print statement" - Inserts print/console.log
- "Create an if statement" - Adds conditional logic
- "Fix syntax errors" - Analyzes code for issues
- "Add comments" - Inserts comment blocks

### File Management
- Create, read, update, delete files
- Auto-save functionality (every 30 seconds)
- Syntax highlighting for multiple languages
- File type detection and appropriate templates

### Real-time Communication
- WebSocket connection for instant voice command processing
- Automatic reconnection on connection loss
- Real-time status updates

## Security Considerations

### File System
- All file operations are restricted to the `workspace/` directory
- Path traversal attacks are prevented
- File execution is limited to Python files with timeout

### CORS
- Currently configured to allow all origins (`*`)
- In production, specify your frontend domain

### Code Execution
- Python files are executed in isolated temporary directories
- Execution timeout prevents infinite loops
- Limited to Python files only

## Troubleshooting

### Common Issues

1. **WebSocket Connection Failed**
   - Check if the server is running
   - Verify the WebSocket URL in the frontend code
   - Check browser console for errors

2. **File Operations Not Working**
   - Ensure the `workspace/` directory exists
   - Check file permissions
   - Verify API endpoint URLs

3. **Voice Commands Not Processing**
   - Check WebSocket connection status
   - Verify voice recognition is enabled
   - Check browser microphone permissions

### Debug Mode
- Enable browser developer tools
- Check console for JavaScript errors
- Monitor network requests in browser dev tools
- Check server logs for backend errors

## Future Enhancements

### Planned Features
- Real voice recognition integration (currently simulated)
- Advanced code analysis and suggestions
- Multi-language support expansion
- User authentication and project management
- Collaborative editing features
- Advanced IDE features (debugging, intellisense)

### Technical Improvements
- Database integration for persistent storage
- Redis for session management
- Docker containerization
- Production deployment configuration
- Performance optimization
- Error handling improvements

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test the integration
5. Submit a pull request

## License

This project is part of the HTF25-Team-261 submission for Hacktoberfest 2025.
