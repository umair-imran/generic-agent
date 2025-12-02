/**
 * TypeScript types for LiveKit integration
 */

export interface TokenRequest {
  room_name: string;
  participant_name: string;
  participant_identity?: string;
}

export interface TokenResponse {
  token: string;
  url: string;
  room_name: string;
  participant_name: string;
  participant_identity: string;
}

export interface RoomInfo {
  name: string;
  num_participants: number;
  creation_time?: string;
  empty_timeout?: number;
  max_participants?: number;
}

export interface RoomListResponse {
  rooms: RoomInfo[];
  count: number;
}

export interface VoiceAssistantState {
  isConnected: boolean;
  isAgentConnected: boolean;
  isConnecting: boolean;
  error: string | null;
  roomName: string | null;
}

