/**
 * Example React Native component for Voice Assistant integration
 * 
 * Usage:
 * ```tsx
 * import { VoiceAssistant } from './react-native-integration/VoiceAssistant';
 * 
 * export default function App() {
 *   return <VoiceAssistant />;
 * }
 * ```
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  Platform,
  Alert,
} from 'react-native';
import { Room, RoomEvent, RemoteParticipant } from 'livekit-react-native';
import { TokenRequest, TokenResponse, VoiceAssistantState } from './types';

// Configure your API base URL
const API_BASE_URL = __DEV__
  ? Platform.OS === 'android'
    ? 'http://10.0.2.2:8000' // Android emulator
    : 'http://localhost:8000' // iOS simulator / development
  : 'https://your-production-api.com'; // Production

export const VoiceAssistant: React.FC = () => {
  const [room, setRoom] = useState<Room | null>(null);
  const [state, setState] = useState<VoiceAssistantState>({
    isConnected: false,
    isAgentConnected: false,
    isConnecting: false,
    error: null,
    roomName: null,
  });

  const getAccessToken = async (
    request: TokenRequest
  ): Promise<TokenResponse> => {
    const response = await fetch(`${API_BASE_URL}/api/token`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || `Failed to get token: ${response.statusText}`);
    }

    return response.json();
  };

  const connect = useCallback(async () => {
    try {
      setState((prev) => ({
        ...prev,
        isConnecting: true,
        error: null,
      }));

      const roomName = `room-${Date.now()}`;
      const participantName = 'User';

      // Get token from backend
      const { token, url } = await getAccessToken({
        room_name: roomName,
        participant_name: participantName,
      });

      // Create room instance
      const newRoom = new Room();

      // Set up event listeners
      newRoom.on(RoomEvent.Connected, () => {
        console.log('✅ Connected to room');
        setState((prev) => ({
          ...prev,
          isConnected: true,
          isConnecting: false,
          roomName,
        }));
      });

      newRoom.on(RoomEvent.ParticipantConnected, (participant: RemoteParticipant) => {
        console.log('🤖 Agent connected:', participant.identity);
        setState((prev) => ({
          ...prev,
          isAgentConnected: true,
        }));
      });

      newRoom.on(RoomEvent.ParticipantDisconnected, () => {
        console.log('🤖 Agent disconnected');
        setState((prev) => ({
          ...prev,
          isAgentConnected: false,
        }));
      });

      newRoom.on(RoomEvent.Disconnected, () => {
        console.log('❌ Disconnected from room');
        setState((prev) => ({
          ...prev,
          isConnected: false,
          isAgentConnected: false,
          roomName: null,
        }));
      });

      newRoom.on(RoomEvent.RoomMetadataChanged, (metadata) => {
        console.log('📝 Room metadata changed:', metadata);
      });

      // Connect to room
      await newRoom.connect(url, token);

      // Enable microphone
      await newRoom.localParticipant?.setMicrophoneEnabled(true);

      setRoom(newRoom);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      console.error('❌ Failed to connect:', err);
      setState((prev) => ({
        ...prev,
        error: errorMessage,
        isConnecting: false,
      }));
      Alert.alert('Connection Error', errorMessage);
    }
  }, []);

  const disconnect = useCallback(async () => {
    if (room) {
      try {
        await room.disconnect();
        setRoom(null);
        setState((prev) => ({
          ...prev,
          isConnected: false,
          isAgentConnected: false,
          roomName: null,
        }));
      } catch (err) {
        console.error('Failed to disconnect:', err);
      }
    }
  }, [room]);

  useEffect(() => {
    return () => {
      if (room) {
        room.disconnect();
      }
    };
  }, [room]);

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Voice Assistant</Text>
      <Text style={styles.subtitle}>Real-time AI Conversation</Text>

      <View style={styles.statusContainer}>
        <View style={styles.statusRow}>
          <Text style={styles.statusLabel}>Connection:</Text>
          <View style={styles.statusIndicator}>
            <View
              style={[
                styles.statusDot,
                state.isConnected && styles.statusDotActive,
              ]}
            />
            <Text
              style={[
                styles.statusText,
                state.isConnected && styles.statusTextActive,
              ]}
            >
              {state.isConnected ? 'Connected' : 'Disconnected'}
            </Text>
          </View>
        </View>

        <View style={styles.statusRow}>
          <Text style={styles.statusLabel}>Agent:</Text>
          <View style={styles.statusIndicator}>
            <View
              style={[
                styles.statusDot,
                state.isAgentConnected && styles.statusDotActive,
              ]}
            />
            <Text
              style={[
                styles.statusText,
                state.isAgentConnected && styles.statusTextActive,
              ]}
            >
              {state.isAgentConnected ? 'Connected' : 'Not Connected'}
            </Text>
          </View>
        </View>

        {state.roomName && (
          <Text style={styles.roomName}>Room: {state.roomName}</Text>
        )}
      </View>

      {state.error && (
        <View style={styles.errorContainer}>
          <Text style={styles.errorText}>⚠️ {state.error}</Text>
        </View>
      )}

      <TouchableOpacity
        style={[
          styles.button,
          state.isConnected && styles.buttonDisconnect,
          state.isConnecting && styles.buttonDisabled,
        ]}
        onPress={state.isConnected ? disconnect : connect}
        disabled={state.isConnecting}
      >
        {state.isConnecting ? (
          <ActivityIndicator color="#fff" />
        ) : state.isConnected ? (
          <Text style={styles.buttonText}>Disconnect</Text>
        ) : (
          <Text style={styles.buttonText}>Connect</Text>
        )}
      </TouchableOpacity>

      {state.isConnected && (
        <Text style={styles.hint}>
          🎤 Speak into your microphone to start the conversation
        </Text>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    marginBottom: 8,
    color: '#333',
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    marginBottom: 40,
  },
  statusContainer: {
    width: '100%',
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 20,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  statusRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 15,
  },
  statusLabel: {
    fontSize: 16,
    color: '#666',
    fontWeight: '500',
  },
  statusIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statusDot: {
    width: 10,
    height: 10,
    borderRadius: 5,
    backgroundColor: '#ccc',
    marginRight: 8,
  },
  statusDotActive: {
    backgroundColor: '#4CAF50',
  },
  statusText: {
    fontSize: 16,
    color: '#666',
    fontWeight: '600',
  },
  statusTextActive: {
    color: '#4CAF50',
  },
  roomName: {
    fontSize: 12,
    color: '#999',
    marginTop: 10,
    fontFamily: Platform.OS === 'ios' ? 'Courier' : 'monospace',
  },
  errorContainer: {
    backgroundColor: '#ffebee',
    padding: 15,
    borderRadius: 8,
    marginBottom: 20,
    width: '100%',
  },
  errorText: {
    color: '#c62828',
    fontSize: 14,
    textAlign: 'center',
  },
  button: {
    backgroundColor: '#2196F3',
    padding: 18,
    borderRadius: 12,
    minWidth: 200,
    alignItems: 'center',
    marginTop: 20,
    shadowColor: '#2196F3',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 4,
    elevation: 5,
  },
  buttonDisconnect: {
    backgroundColor: '#f44336',
    shadowColor: '#f44336',
  },
  buttonDisabled: {
    opacity: 0.6,
  },
  buttonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: '600',
  },
  hint: {
    marginTop: 30,
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
    fontStyle: 'italic',
  },
});

