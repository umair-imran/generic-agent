# React Native Integration Examples

This directory contains example code for integrating the Hospitality Bot with React Native applications.

## Files

- **`VoiceAssistant.tsx`** - Complete React Native component example
- **`types.ts`** - TypeScript type definitions
- **`README.md`** - This file

## Quick Start

### 1. Install Dependencies

```bash
npm install livekit-react-native
npm install react-native-permissions
npm install @react-native-async-storage/async-storage
```

### 2. Configure API URL

Edit `VoiceAssistant.tsx` and update the `API_BASE_URL` constant:

```typescript
const API_BASE_URL = __DEV__
  ? Platform.OS === 'android'
    ? 'http://10.0.2.2:8000' // Android emulator
    : 'http://localhost:8000' // iOS simulator
  : 'https://your-production-api.com';
```

### 3. Add Permissions

**iOS** (`ios/YourApp/Info.plist`):
```xml
<key>NSMicrophoneUsageDescription</key>
<string>We need microphone access for voice conversations</string>
```

**Android** (`android/app/src/main/AndroidManifest.xml`):
```xml
<uses-permission android:name="android.permission.RECORD_AUDIO" />
<uses-permission android:name="android.permission.INTERNET" />
```

### 4. Use the Component

```typescript
import { VoiceAssistant } from './react-native-integration/VoiceAssistant';

export default function App() {
  return <VoiceAssistant />;
}
```

## Features

- ✅ Automatic token generation
- ✅ Room connection management
- ✅ Agent connection status
- ✅ Error handling
- ✅ Loading states
- ✅ Clean disconnect

## Customization

### Change API Base URL

Update the `API_BASE_URL` constant in `VoiceAssistant.tsx`.

### Customize Styling

Modify the `styles` object in `VoiceAssistant.tsx` to match your app's design.

### Add Additional Features

- Connection retry logic
- Audio level indicators
- Conversation history
- Custom error messages

## Troubleshooting

### Connection Issues

1. Verify backend is running: `curl http://localhost:8000/health`
2. Check API URL is correct
3. Verify network connectivity
4. Check console logs for errors

### Audio Issues

1. Check microphone permissions
2. Verify `setMicrophoneEnabled(true)` is called
3. Test on real device (simulator has limited support)
4. Check device audio settings

## Next Steps

1. Review [REACT_NATIVE_SETUP.md](../REACT_NATIVE_SETUP.md) for detailed guide
2. Check [API_DOCS.md](../API_DOCS.md) for API reference
3. Customize the component for your needs
4. Add error handling and retry logic
5. Implement reconnection on disconnect

## Support

For issues:
- Check the main [README.md](../README.md)
- Review [API_DOCS.md](../API_DOCS.md)
- See [REACT_NATIVE_SETUP.md](../REACT_NATIVE_SETUP.md)

