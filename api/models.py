"""Pydantic models for API request/response validation."""
from pydantic import BaseModel, Field
from typing import Optional, List


class TokenRequest(BaseModel):
    """Request model for generating LiveKit access token."""
    room_name: str = Field(..., description="Name of the LiveKit room to join")
    participant_name: str = Field(..., description="Display name of the participant")
    participant_identity: Optional[str] = Field(
        None,
        description="Unique identity for the participant (defaults to participant_name)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "room_name": "room-123",
                "participant_name": "John Doe",
                "participant_identity": "user-123"
            }
        }


class TokenResponse(BaseModel):
    """Response model for LiveKit access token."""
    token: str = Field(..., description="JWT access token for LiveKit")
    url: str = Field(..., description="LiveKit server WebSocket URL")
    room_name: str = Field(..., description="Room name")
    participant_name: str = Field(..., description="Participant name")
    participant_identity: str = Field(..., description="Participant identity")


class CreateRoomRequest(BaseModel):
    """Request model for creating a LiveKit room."""
    room_name: str = Field(..., description="Name of the room to create")
    empty_timeout: Optional[int] = Field(
        300,
        description="Timeout in seconds before deleting empty room (default: 300)"
    )
    max_participants: Optional[int] = Field(
        None,
        description="Maximum number of participants allowed"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "room_name": "room-123",
                "empty_timeout": 300,
                "max_participants": 10
            }
        }


class RoomInfo(BaseModel):
    """Information about a LiveKit room."""
    name: str = Field(..., description="Room name")
    num_participants: int = Field(..., description="Number of current participants")
    creation_time: Optional[str] = Field(None, description="Room creation timestamp")
    empty_timeout: Optional[int] = Field(None, description="Empty room timeout")
    max_participants: Optional[int] = Field(None, description="Max participants")


class RoomListResponse(BaseModel):
    """Response model for listing rooms."""
    rooms: List[RoomInfo] = Field(..., description="List of active rooms")
    count: int = Field(..., description="Total number of rooms")


class ErrorResponse(BaseModel):
    """Error response model."""
    detail: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")

