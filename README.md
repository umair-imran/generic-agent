# Hospitality Bot - LiveKit Voice AI Assistant

A complete voice AI assistant built with LiveKit, FastAPI, and React Native integration. This project provides a production-ready backend for real-time voice conversations with AI agents.

## 🚀 Features

- **Real-time Voice AI**: Powered by OpenAI, Deepgram, and Cartesia
- **LiveKit Integration**: WebRTC-based real-time communication
- **FastAPI Backend**: RESTful API for token generation and room management
- **React Native Ready**: CORS configured and example code provided
- **Simple Setup**: One-command startup scripts
- **Docker Support**: Optional containerized deployment

## 📋 Prerequisites

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) package manager (or pip)
- LiveKit server (Cloud or self-hosted)
- API keys for:
  - OpenAI (for LLM)
  - Deepgram (for Speech-to-Text)
  - Cartesia (for Text-to-Speech)

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd hospitality-bot
```

### 2. Install Dependencies

Using uv (recommended):
```bash
uv pip install -e .
```

Or using pip:
```bash
pip install -r pyproject.toml
```

### 3. Configure Environment

Create `.env.local` file from the example:

```bash
cp .env.local.example .env.local
```

Edit `.env.local` and add your credentials:

```bash
# LiveKit Server
LIVEKIT_URL=wss://your-livekit-server.com
LIVEKIT_API_KEY=your-api-key
LIVEKIT_API_SECRET=your-api-secret

# AI Services
OPENAI_API_KEY=your-openai-key
DEEPGRAM_API_KEY=your-deepgram-key
CARTESIA_API_KEY=your-cartesia-key

# API Server
API_HOST=0.0.0.0
API_PORT=8000
ENV=DEV
```

## 🏃 Running the Project

### Option 1: Simple Startup (Recommended)

**Linux/macOS:**
```bash
./start.sh
```

**Windows or Cross-platform:**
```bash
python start.py
```

This starts both the FastAPI server and LiveKit agent together.

### Option 2: Run Separately

**Start FastAPI server:**
```bash
python main.py api
```

**Start LiveKit agent (in another terminal):**
```bash
python main.py agent
```

### Option 3: Docker

```bash
docker-compose up
```

## 📡 API Endpoints

Once running, the API is available at `http://localhost:8000`

- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Token Generation**: POST http://localhost:8000/api/token

See [API_DOCS.md](API_DOCS.md) for complete API documentation.

## 📱 React Native Integration

See [REACT_NATIVE_SETUP.md](REACT_NATIVE_SETUP.md) for detailed React Native integration guide.

Quick start:
1. Install `livekit-react-native` package
2. Request token from `/api/token` endpoint
3. Connect to LiveKit with the token
4. Enable microphone and start conversation

Example code is available in `react-native-integration/` directory.

## 🏗️ Project Structure

```
hospitality-bot/
├── api/                    # FastAPI application
│   ├── app.py             # Main API endpoints
│   └── models.py          # Pydantic models
├── config/                 # Configuration
│   ├── config.py          # Settings classes
│   └── config.yml         # Agent configuration
├── modules/                # Agent modules
│   ├── agent.py           # HospitalityAssistant class
│   └── prompts.py        # AI prompts
├── entrypoint.py          # LiveKit agent entrypoint
├── main.py                # Main entry point
├── start.sh               # Startup script (Linux/macOS)
├── start.py               # Startup script (Cross-platform)
├── docker-compose.yml     # Docker configuration
└── react-native-integration/  # React Native examples
```

## 🔧 Configuration

### Agent Configuration

Edit `config/config.yml` to customize the AI agent:

```yaml
llm:
  type: openai
  model: gpt-4o-mini
  temperature: 0.2

stt:
  type: deepgram
  model: nova-3
  language: en

tts:
  type: cartesia
  model: sonic-2
  language: en
```

### Environment Variables

All sensitive credentials are loaded from `.env.local`:
- LiveKit server credentials
- API keys for AI services
- Server configuration

## 🧪 Testing

### Test API Health

```bash
curl http://localhost:8000/health
```

### Test Token Generation

```bash
curl -X POST http://localhost:8000/api/token \
  -H "Content-Type: application/json" \
  -d '{
    "room_name": "test-room",
    "participant_name": "Test User"
  }'
```

## 🐳 Docker Deployment

### Build and Run

```bash
docker-compose up --build
```

### Run in Background

```bash
docker-compose up -d
```

### View Logs

```bash
docker-compose logs -f
```

## 📚 Documentation

- [API_DOCS.md](API_DOCS.md) - Complete API endpoint documentation
- [REACT_NATIVE_SETUP.md](REACT_NATIVE_SETUP.md) - React Native integration guide
- [react-native-integration/](react-native-integration/) - Example React Native code

## 🔍 Troubleshooting

### Agent Not Connecting

1. Check LiveKit server URL and credentials in `.env.local`
2. Verify agent worker is running: `python main.py agent`
3. Check logs for connection errors

### API Not Starting

1. Check if port 8000 is available
2. Verify all environment variables are set
3. Check API logs for errors

### Token Generation Fails

1. Verify LiveKit credentials in `.env.local`
2. Check that `LIVEKIT_URL`, `LIVEKIT_API_KEY`, and `LIVEKIT_API_SECRET` are set
3. Ensure LiveKit server is accessible

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

[Add your license here]

## 🆘 Support

For issues and questions:
- Check the documentation files
- Review API docs at `/docs` endpoint
- Open an issue on GitHub

## 🎯 Next Steps

1. Set up your LiveKit server (Cloud or self-hosted)
2. Configure environment variables
3. Start the backend: `./start.sh`
4. Integrate with React Native (see REACT_NATIVE_SETUP.md)
5. Start building your voice AI application!

