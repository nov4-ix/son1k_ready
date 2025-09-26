# Waves Plugin Integration for Son1kVers3

This document explains how to connect your Waves plugins to the Son1kVers3 interface knobs.

## 🎛️ Supported Plugins

### Currently Mapped:
- **SSL E-Channel** - EQ controls (High, Mid, Low frequencies)
- **API 2500** - Compression (Ratio, Attack, Release, Threshold)
- **CLA-2A** - Compression (Gain, Peak Reduction)
- **CLA-76** - Compression (Input, Output, Attack, Release)

### Knob Mappings:
- **EXPRESSION** → API 2500 Ratio
- **RAREZA** → CLA-2A Gain
- **GARAGE** → SSL E-Channel High
- **TUNING** → SSL E-Channel Mid
- **ANALOG** → CLA-76 Input

## 🔧 Installation

### Prerequisites:
1. Waves plugins installed locally
2. Node.js installed
3. macOS or Linux system

### Quick Install:
```bash
./install_waves_integration.sh
```

### Manual Install:
1. Install OSC dependencies:
   ```bash
   npm install osc-js
   ```

2. Start the Waves bridge:
   ```bash
   node waves_bridge.js
   ```

3. Open Son1kVers3 in your browser

## 🎵 How It Works

### Connection Methods:

1. **OSC (Open Sound Control)**
   - Sends parameter changes via OSC messages
   - Port: 57120
   - Real-time communication

2. **Web Audio API**
   - Processes audio in real-time
   - Applies EQ and compression effects
   - Works in browser

3. **VST Bridge** (Future)
   - Direct VST plugin control
   - Requires additional setup

### Real-time Processing:

When you turn a knob in Son1kVers3:
1. The value is sent to the Waves bridge
2. The bridge updates the corresponding plugin parameter
3. Audio processing is applied in real-time
4. Visual feedback shows the parameter change

## 🎛️ Using the Interface

### Expression Controls:
- **EXPRESSION**: Controls compression ratio for dynamic expression
- **RAREZA**: Controls gain for unique character
- **GARAGE**: Controls high frequency for garage sound

### Generation Parameters:
- **TUNING**: Controls mid frequency for pitch correction
- **ANALOG**: Controls analog saturation input

### SSL EQ Module:
- 5-band equalizer (80Hz, 250Hz, 1kHz, 4kHz, 12kHz)
- Click on sliders to adjust
- Real-time frequency response

## 🔧 Configuration

### Custom Mappings:
Edit `waves_config.json` to change knob mappings:

```json
{
  "knob_mappings": {
    "expresividad": {
      "plugin": "api_2500",
      "parameter": "ratio"
    }
  }
}
```

### Adding New Plugins:
1. Add plugin to `waves_config.json`
2. Define parameters and ranges
3. Update `waves_integration.js`
4. Restart the bridge

## 🐛 Troubleshooting

### Common Issues:

1. **"WAVES OFFLINE" Status**
   - Check if Waves plugins are installed
   - Verify the bridge is running
   - Check console for errors

2. **Knobs Not Responding**
   - Ensure OSC is running on port 57120
   - Check browser console for errors
   - Verify plugin mappings

3. **Audio Not Processing**
   - Check Web Audio API support
   - Verify audio context is initialized
   - Check browser permissions

### Debug Mode:
Enable debug logging in browser console:
```javascript
localStorage.setItem('debug', 'waves');
```

## 🚀 Advanced Features

### Preset Management:
- Save current knob positions
- Load saved presets
- Export/import configurations

### MIDI Control:
- Map knobs to MIDI controllers
- Use external hardware
- Real-time parameter control

### Automation:
- Record knob movements
- Playback automation
- Export automation data

## 📚 API Reference

### JavaScript API:
```javascript
// Update plugin parameter
wavesBridge.updatePluginParameter('SSL E-Channel', 'High', 75);

// Get current settings
const settings = wavesBridge.exportSettings();

// Load settings
wavesBridge.importSettings(settings);
```

### OSC Messages:
```
/waves/ssl_e_channel/high 75
/waves/api_2500/ratio 50
/waves/cla_2a/gain 25
```

## 🤝 Contributing

To add support for more Waves plugins:

1. Fork the repository
2. Add plugin configuration to `waves_config.json`
3. Implement parameter mapping in `waves_integration.js`
4. Test with your plugins
5. Submit a pull request

## 📄 License

This integration is part of Son1kVers3 and follows the same license terms.

## 🆘 Support

For issues with Waves integration:
1. Check the troubleshooting section
2. Review console logs
3. Open an issue on GitHub
4. Contact support

---

**Note**: This integration requires Waves plugins to be installed locally. The interface will show "WAVES OFFLINE" if no connection is established.
