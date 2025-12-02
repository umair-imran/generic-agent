# React Native Integration Guide

Complete guide for integrating the Hospitality Bot with your React Native application.

## 📦 Installation

### 1. Install Dependencies

```bash
npm install livekit-react-native
# or
yarn add livekit-react-native
```

### 2. Install Peer Dependencies

```bash
npm install react-native-permissions
npm install @react-native-async-storage/async-storage
```

### 3. iOS Setup

Add to `ios/Podfile`:
```ruby
pod 'LiveKitReactNative', :path => '../node_modules/livekit-react-native'
```

Then run:
```bash
cd ios && pod install
```

### 4. Android Setup

Add permissions to `android/app/src/main/AndroidManifest.xml`:
```xml
<uses-permission android:name="android.permission.RECORD_AUDIO" />
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.MODIFY_AUDIO_SETTINGS" />
```

For iOS, add to `ios/YourApp/Info.plist`:
```xml
<key>NSMicrophoneUsageDescription</key>
<string>We need microphone access for voice conversations</string>
```

## 🔧 Configuration

### API Base URL

Set your backend API URL. You can use environment variables or a config file:

```typescript
// config.ts
export const API_BASE_URL = __DEV__ 
  ? 'http://localhost:8000'  // Development
  : 'https://your-production-api.com';  // Production
```

For Android, use `10.0.2.2` instead of `localhost`:
```typescript
export const API_BASE_URL = __DEV__ 
  ? Platform.OS === 'android' ? 'http://10.0.2.2:8000' : 'http://localhost:8000'
  : 'https://your-production-api.com';
```

## 💻 Implementation

### Step 1: Create Voice Assistant Hook

Create `hooks/useVoiceAssistant.ts`:

```typescript
import { useState, useEffect, useCallback } from 'react';
import { Room, RoomEvent, RemoteParticipant } from 'livekit-react-native';
import { API_BASE_URL } from '../config';

interface TokenResponse {
  token: string;
  url: string;
  room_name: string;
  participant_name: string;
  participant_identity: string;
}

export const useVoiceAssistant = () => {
  const [room, setRoom] = useState<Room | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [isAgentConnected, setIsAgentConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const getAccessToken = async (
    roomName: string,
    participantName: string
  ): Promise<TokenResponse> => {
    const response = await fetch(`${API_BASE_URL}/api/token`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        room_name: roomName,
        participant_name: participantName,
      }),
    });

    if (!response.ok) {
      throw new Error(`Failed to get token: ${response.statusText}`);
    }

    return response.json();
  };

  const connect = useCallback(async () => {
    try {
      setError(null);
      const roomName = `room-${Date.now()}`;
      const participantName = 'User';

      // Get token from backend
      const { token, url } = await getAccessToken(roomName, participantName);

      // Create room instance
      const newRoom = new Room();

      // Set up event listeners
      newRoom.on(RoomEvent.Connected, () => {
        console.log('Connected to room');
        setIsConnected(true);
      });

      newRoom.on(RoomEvent.ParticipantConnected, (participant: RemoteParticipant) => {
        console.log('Agent connected:', participant.identity);
        setIsAgentConnected(true);
      });

      newRoom.on(RoomEvent.ParticipantDisconnected, () => {
        console.log('Agent disconnected');
        setIsAgentConnected(false);
      });

      newRoom.on(RoomEvent.Disconnected, () => {
        console.log('Disconnected from room');
        setIsConnected(false);
        setIsAgentConnected(false);
      });

      // Connect to room
      await newRoom.connect(url, token);

      // Enable microphone
      await newRoom.localParticipant?.setMicrophoneEnabled(true);

      setRoom(newRoom);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setError(errorMessage);
      console.error('Failed to connect:', err);
    }
  }, []);

  const disconnect = useCallback(async () => {
    if (room) {
      await room.disconnect();
      setRoom(null);
    }
  }, [room]);

  useEffect(() => {
    return () => {
      if (room) {
        room.disconnect();
      }
    };
  }, [room]);

  return {
    room,
    isConnected,
    isAgentConnected,
    error,
    connect,
    disconnect,
  };
};
```

### Step 2: Create Voice Assistant Component

Create `components/VoiceAssistant.tsx`:

```typescript
import React from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
} from 'react-native';
import { useVoiceAssistant } from '../hooks/useVoiceAssistant';

export const VoiceAssistant: React.FC = () => {
  const {
    isConnected,
    isAgentConnected,
    error,
    connect,
    disconnect,
  } = useVoiceAssistant();

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Voice Assistant</Text>
      
      <View style={styles.statusContainer}>
        <Text style={styles.statusLabel}>Connection:</Text>
        <Text style={[styles.status, isConnected && styles.statusConnected]}>
          {isConnected ? 'Connected' : 'Disconnected'}
        </Text>
      </View>

      <View style={styles.statusContainer}>
        <Text style={styles.statusLabel}>Agent:</Text>
        <Text style={[styles.status, isAgentConnected && styles.statusConnected]}>
          {isAgentConnected ? 'Connected' : 'Not Connected'}
        </Text>
      </View>

      {error && (
        <View style={styles.errorContainer}>
          <Text style={styles.errorText}>{error}</Text>
        </View>
      )}

      <TouchableOpacity
        style={[styles.button, isConnected && styles.buttonDisconnect]}
        onPress={isConnected ? disconnect : connect}
        disabled={false}
      >
        {isConnected ? (
          <Text style={styles.buttonText}>Disconnect</Text>
        ) : (
          <Text style={styles.buttonText}>Connect</Text>
        )}
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 30,
  },
  statusContainer: {
    flexDirection: 'row',
    marginBottom: 15,
    alignItems: 'center',
  },
  statusLabel: {
    fontSize: 16,
    marginRight: 10,
  },
  status: {
    fontSize: 16,
    color: '#666',
    fontWeight: '600',
  },
  statusConnected: {
    color: '#4CAF50',
  },
  errorContainer: {
    backgroundColor: '#ffebee',
    padding: 10,
    borderRadius: 5,
    marginBottom: 20,
  },
  errorText: {
    color: '#c62828',
    fontSize: 14,
  },
  button: {
    backgroundColor: '#2196F3',
    padding: 15,
    borderRadius: 8,
    minWidth: 150,
    alignItems: 'center',
    marginTop: 20,
  },
  buttonDisconnect: {
    backgroundColor: '#f44336',
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
});
```

### Step 3: Use in Your App

```typescript
import React from 'react';
import { VoiceAssistant } from './components/VoiceAssistant';

export default function App() {
  return <VoiceAssistant />;
}
```

## 🎯 Usage Flow

1. **User taps "Connect"**
   - App requests token from `/api/token`
   - Receives token and LiveKit server URL
   - Connects to LiveKit room

2. **LiveKit Server**
   - Detects new participant
   - Triggers agent worker
   - Agent connects to same room

3. **Conversation Starts**
   - User speaks → Audio sent to LiveKit
   - Agent processes → Generates response
   - Response audio → Sent back to user

4. **User taps "Disconnect"**
   - Disconnects from room
   - Agent session ends

## 🔍 Troubleshooting

### Connection Fails

- Check API URL is correct
- Verify backend is running
- Check network connectivity
- Review error messages in console

### No Audio

- Check microphone permissions
- Verify `setMicrophoneEnabled(true)` is called
- Check device audio settings
- Test with headphones

### Agent Not Connecting

- Verify agent worker is running
- Check LiveKit server credentials
- Review agent logs
- Ensure room name matches

## 📱 Platform-Specific Notes

### iOS

- Requires microphone permission
- Test on real device (simulator has limited audio support)
- Check Info.plist permissions

### Android

- Use `10.0.2.2` for localhost in emulator
- Use actual device IP for physical device
- Check AndroidManifest.xml permissions

## 🚀 Production Considerations

1. **Error Handling**: Add retry logic and user-friendly error messages
2. **Loading States**: Show loading indicators during connection
3. **Reconnection**: Implement automatic reconnection on disconnect
4. **Analytics**: Track connection success/failure rates
5. **Security**: Add authentication to token endpoint
6. **Rate Limiting**: Implement on backend

## 📚 Additional Resources

- [LiveKit React Native Docs](https://docs.livekit.io/client-sdk-react-native/)
- [Example Code](../react-native-integration/)
- [API Documentation](../API_DOCS.md)

