"""FastAPI application for managing and monitoring the hospitality agent."""
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from typing import Dict, Any, Optional

from config import ApplicationSettings
from utils.logger import LOGGER
from api.models import (
    TokenRequest,
    TokenResponse,
    CreateRoomRequest,
    RoomListResponse,
    RoomInfo,
    ErrorResponse
)


# Global state to track agent status
agent_status: Dict[str, Any] = {
    "status": "ready",
    "active_rooms": [],
    "uptime": None
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events."""
    # Startup
    LOGGER.info("FastAPI application starting up")
    agent_status["status"] = "running"
    yield
    # Shutdown
    LOGGER.info("FastAPI application shutting down")
    agent_status["status"] = "stopped"


# Create FastAPI app with lifespan
app = FastAPI(
    title="Hospitality Agent API",
    description="API for managing and monitoring the LiveKit hospitality agent",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware for React Native
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your React Native app origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    Returns the health status of the API and agent.
    """
    try:
        # Try to load configuration to verify it's accessible
        settings = ApplicationSettings.from_cfg('config/config.yml')
        
        return JSONResponse({
            "status": "healthy",
            "agent_status": agent_status["status"],
            "config_loaded": True,
            "service": "hospitality-agent-api"
        })
    except Exception as e:
        LOGGER.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Service unhealthy: {str(e)}"
        )


@app.get("/status")
async def get_status():
    """
    Get current agent status.
    Returns detailed status information about the agent.
    """
    try:
        settings = ApplicationSettings.from_cfg('config/config.yml')
        
        return JSONResponse({
            "status": agent_status["status"],
            "active_rooms": agent_status["active_rooms"],
            "uptime": agent_status["uptime"],
            "configuration": {
                "llm": {
                    "type": settings.llm.type,
                    "model": settings.llm.model,
                    "temperature": settings.llm.temperature,
                },
                "stt": {
                    "type": settings.stt.type,
                    "model": settings.stt.model,
                    "language": settings.stt.language,
                },
                "tts": {
                    "type": settings.tts.type,
                    "model": settings.tts.model,
                    "language": settings.tts.language,
                    "voice": settings.tts.voice,
                }
            }
        })
    except Exception as e:
        LOGGER.error(f"Failed to get status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve status: {str(e)}"
        )


@app.get("/config")
async def get_config():
    """
    Get current agent configuration.
    Returns the current configuration settings (without sensitive data).
    """
    try:
        settings = ApplicationSettings.from_cfg('config/config.yml')
        
        return JSONResponse({
            "llm": {
                "type": settings.llm.type,
                "model": settings.llm.model,
                "temperature": settings.llm.temperature,
                "verbose": settings.llm.verbose,
            },
            "stt": {
                "type": settings.stt.type,
                "model": settings.stt.model,
                "language": settings.stt.language,
                "base_url": settings.stt.base_url,
            },
            "tts": {
                "type": settings.tts.type,
                "model": settings.tts.model,
                "language": settings.tts.language,
                "voice": settings.tts.voice,
                "base_url": settings.tts.base_url,
            }
        })
    except Exception as e:
        LOGGER.error(f"Failed to get configuration: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve configuration: {str(e)}"
        )


@app.post("/api/token", response_model=TokenResponse)
async def generate_token(request: TokenRequest):
    """
    Generate LiveKit access token for React Native client.
    This is the critical endpoint for frontend integration.
    """
    try:
        settings = ApplicationSettings.from_cfg('config/config.yml')
        
        if not settings.livekit:
            raise HTTPException(
                status_code=500,
                detail="LiveKit configuration not found. Please set LIVEKIT_URL, LIVEKIT_API_KEY, and LIVEKIT_API_SECRET environment variables."
            )
        
        # Import LiveKit API for token generation
        from livekit import api
        
        # Create access token
        token = api.AccessToken(
            settings.livekit.LIVEKIT_API_KEY,
            settings.livekit.LIVEKIT_API_SECRET
        ) \
            .with_identity(request.participant_identity or request.participant_name) \
            .with_name(request.participant_name) \
            .with_grants(api.VideoGrants(
                room_join=True,
                room=request.room_name,
                can_publish=True,
                can_subscribe=True,
            )) \
            .to_jwt()
        
        return TokenResponse(
            token=token,
            url=settings.livekit.LIVEKIT_URL,
            room_name=request.room_name,
            participant_name=request.participant_name,
            participant_identity=request.participant_identity or request.participant_name
        )
    except HTTPException:
        raise
    except Exception as e:
        LOGGER.error(f"Failed to generate token: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate token: {str(e)}"
        )


@app.post("/api/room/create")
async def create_room(request: CreateRoomRequest):
    """Create a new LiveKit room."""
    try:
        settings = ApplicationSettings.from_cfg('config/config.yml')
        
        if not settings.livekit:
            raise HTTPException(
                status_code=500,
                detail="LiveKit configuration not found"
            )
        
        from livekit import api
        
        lk_api = api.LiveKitAPI(
            settings.livekit.LIVEKIT_URL,
            settings.livekit.LIVEKIT_API_KEY,
            settings.livekit.LIVEKIT_API_SECRET
        )
        
        # Create room request
        create_request = api.CreateRoomRequest(name=request.room_name)
        if request.empty_timeout:
            create_request.empty_timeout = request.empty_timeout
        if request.max_participants:
            create_request.max_participants = request.max_participants
        
        room = await lk_api.room.create_room(create_request)
        
        return {
            "room": {
                "name": room.name,
                "creation_time": str(room.creation_time) if hasattr(room, 'creation_time') else None,
                "empty_timeout": room.empty_timeout if hasattr(room, 'empty_timeout') else None,
                "max_participants": room.max_participants if hasattr(room, 'max_participants') else None,
            },
            "url": settings.livekit.LIVEKIT_URL
        }
    except HTTPException:
        raise
    except Exception as e:
        LOGGER.error(f"Failed to create room: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create room: {str(e)}"
        )


@app.get("/api/room/list", response_model=RoomListResponse)
async def list_rooms():
    """List all active LiveKit rooms."""
    try:
        settings = ApplicationSettings.from_cfg('config/config.yml')
        
        if not settings.livekit:
            raise HTTPException(
                status_code=500,
                detail="LiveKit configuration not found"
            )
        
        from livekit import api
        
        lk_api = api.LiveKitAPI(
            settings.livekit.LIVEKIT_URL,
            settings.livekit.LIVEKIT_API_KEY,
            settings.livekit.LIVEKIT_API_SECRET
        )
        
        rooms = await lk_api.room.list_rooms()
        
        room_list = []
        for room in rooms.rooms:
            room_info = RoomInfo(
                name=room.name,
                num_participants=len(room.participants) if hasattr(room, 'participants') else 0,
                creation_time=str(room.creation_time) if hasattr(room, 'creation_time') else None,
                empty_timeout=room.empty_timeout if hasattr(room, 'empty_timeout') else None,
                max_participants=room.max_participants if hasattr(room, 'max_participants') else None,
            )
            room_list.append(room_info)
        
        return RoomListResponse(rooms=room_list, count=len(room_list))
    except HTTPException:
        raise
    except Exception as e:
        LOGGER.error(f"Failed to list rooms: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list rooms: {str(e)}"
        )


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return JSONResponse({
        "service": "Hospitality Agent API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "status": "/status",
            "config": "/config",
            "token": "/api/token (POST)",
            "room_create": "/api/room/create (POST)",
            "room_list": "/api/room/list (GET)",
            "docs": "/docs",
            "openapi": "/openapi.json"
        }
    })


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("API_PORT", "8000"))
    host = os.getenv("API_HOST", "0.0.0.0")
    
    LOGGER.info(f"Starting FastAPI server on {host}:{port}")
    uvicorn.run(
        "api.app:app",
        host=host,
        port=port,
        log_level="info",
        reload=False
    )

