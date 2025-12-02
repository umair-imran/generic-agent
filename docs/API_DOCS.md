# API Documentation

Complete API reference for the Hospitality Bot backend.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API does not require authentication. In production, you should add authentication middleware.

## Endpoints

### Health Check

**GET** `/health`

Check if the API and agent are healthy.

**Response:**
```json
{
  "status": "healthy",
  "agent_status": "running",
  "config_loaded": true,
  "service": "hospitality-agent-api"
}
```

---

### Get Status

**GET** `/status`

Get detailed status information about the agent.

**Response:**
```json
{
  "status": "running",
  "active_rooms": [],
  "uptime": null,
  "configuration": {
    "llm": {
      "type": "openai",
      "model": "gpt-4o-mini",
      "temperature": 0.2
    },
    "stt": {
      "type": "deepgram",
      "model": "nova-3",
      "language": "en"
    },
    "tts": {
      "type": "cartesia",
      "model": "sonic-2",
      "language": "en",
      "voice": "6f84f4b8-58a2-430c-8c79-688dad597532"
    }
  }
}
```

---

### Get Configuration

**GET** `/config`

Get current agent configuration (without sensitive data).

**Response:**
```json
{
  "llm": {
    "type": "openai",
    "model": "gpt-4o-mini",
    "temperature": 0.2,
    "verbose": true
  },
  "stt": {
    "type": "deepgram",
    "model": "nova-3",
    "language": "en",
    "base_url": "https://api.deepgram.com/v1/listen"
  },
  "tts": {
    "type": "cartesia",
    "model": "sonic-2",
    "language": "en",
    "voice": "6f84f4b8-58a2-430c-8c79-688dad597532",
    "base_url": "https://api.cartesia.ai"
  }
}
```

---

### Generate Access Token

**POST** `/api/token`

Generate a LiveKit access token for client connections. This is the primary endpoint for React Native integration.

**Request Body:**
```json
{
  "room_name": "room-123",
  "participant_name": "John Doe",
  "participant_identity": "user-123"  // Optional, defaults to participant_name
}
```

**Response:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "url": "wss://your-livekit-server.com",
  "room_name": "room-123",
  "participant_name": "John Doe",
  "participant_identity": "user-123"
}
```

**Example (cURL):**
```bash
curl -X POST http://localhost:8000/api/token \
  -H "Content-Type: application/json" \
  -d '{
    "room_name": "room-123",
    "participant_name": "John Doe"
  }'
```

**Example (JavaScript/React Native):**
```javascript
const response = await fetch('http://localhost:8000/api/token', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    room_name: 'room-123',
    participant_name: 'John Doe',
  }),
});

const data = await response.json();
// Use data.token and data.url to connect to LiveKit
```

---

### Create Room

**POST** `/api/room/create`

Create a new LiveKit room.

**Request Body:**
```json
{
  "room_name": "room-123",
  "empty_timeout": 300,      // Optional, default: 300 seconds
  "max_participants": 10     // Optional
}
```

**Response:**
```json
{
  "room": {
    "name": "room-123",
    "creation_time": "2024-01-01T00:00:00Z",
    "empty_timeout": 300,
    "max_participants": 10
  },
  "url": "wss://your-livekit-server.com"
}
```

---

### List Rooms

**GET** `/api/room/list`

List all active LiveKit rooms.

**Response:**
```json
{
  "rooms": [
    {
      "name": "room-123",
      "num_participants": 2,
      "creation_time": "2024-01-01T00:00:00Z",
      "empty_timeout": 300,
      "max_participants": 10
    }
  ],
  "count": 1
}
```

---

## Error Responses

All endpoints may return error responses in the following format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

**Common Status Codes:**
- `200` - Success
- `400` - Bad Request (invalid input)
- `500` - Internal Server Error
- `503` - Service Unavailable (agent not running)

## Rate Limiting

Currently, there is no rate limiting. In production, you should implement rate limiting to prevent abuse.

## CORS

CORS is enabled for all origins. In production, you should restrict this to your React Native app's origins.

## Interactive API Documentation

Visit `http://localhost:8000/docs` for interactive Swagger UI documentation where you can test all endpoints directly.

