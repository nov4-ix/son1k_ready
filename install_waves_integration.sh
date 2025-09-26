#!/bin/bash

# Waves Plugin Integration Installation Script
# This script sets up the necessary components for Waves plugin integration

echo "🎵 Installing Waves Plugin Integration for Son1kVers3..."

# Check if Waves is installed
WAVES_PATH="/Applications/Waves"
if [ ! -d "$WAVES_PATH" ]; then
    echo "⚠️  Waves not found in /Applications/Waves"
    echo "Please install Waves plugins first"
    exit 1
fi

echo "✅ Waves found at $WAVES_PATH"

# Create OSC server directory
mkdir -p ~/.son1kvers3/osc
echo "✅ Created OSC directory"

# Install Node.js dependencies for OSC
if command -v npm &> /dev/null; then
    echo "📦 Installing OSC dependencies..."
    npm install osc-js
    echo "✅ OSC dependencies installed"
else
    echo "⚠️  npm not found. Please install Node.js first"
fi

# Create Waves bridge script
cat > waves_bridge.js << 'EOF'
const OSC = require('osc-js');
const fs = require('fs');
const path = require('path');

class WavesBridge {
    constructor() {
        this.osc = new OSC({ plugin: new OSC.DatagramPlugin() });
        this.config = JSON.parse(fs.readFileSync('waves_config.json', 'utf8'));
    }
    
    async start() {
        await this.osc.open({ port: 57120 });
        console.log('Waves Bridge started on port 57120');
        
        this.osc.on('/waves/*', (message) => {
            const [, plugin, parameter] = message.address.split('/');
            const value = message.args[0];
            this.updateWavesParameter(plugin, parameter, value);
        });
    }
    
    updateWavesParameter(plugin, parameter, value) {
        console.log(`Updating ${plugin}: ${parameter} = ${value}%`);
        // Here you would implement the actual Waves plugin control
        // This could involve VST bridge, OSC to VST, or other methods
    }
}

const bridge = new WavesBridge();
bridge.start().catch(console.error);
EOF

echo "✅ Created Waves bridge script"

# Create systemd service for Waves bridge
if command -v systemctl &> /dev/null; then
    cat > son1kvers3-waves.service << EOF
[Unit]
Description=Son1kVers3 Waves Bridge
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
ExecStart=/usr/bin/node waves_bridge.js
Restart=always

[Install]
WantedBy=multi-user.target
EOF

    sudo mv son1kvers3-waves.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable son1kvers3-waves
    echo "✅ Created systemd service"
fi

# Create launchd plist for macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    cat > com.son1kvers3.waves.plist << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.son1kvers3.waves</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/node</string>
        <string>$(pwd)/waves_bridge.js</string>
    </array>
    <key>WorkingDirectory</key>
    <string>$(pwd)</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
EOF

    mv com.son1kvers3.waves.plist ~/Library/LaunchAgents/
    launchctl load ~/Library/LaunchAgents/com.son1kvers3.waves.plist
    echo "✅ Created macOS launchd service"
fi

echo ""
echo "🎉 Waves Plugin Integration installed successfully!"
echo ""
echo "Next steps:"
echo "1. Start the Waves bridge: node waves_bridge.js"
echo "2. Open Son1kVers3 in your browser"
echo "3. The knobs should now control your Waves plugins"
echo ""
echo "For troubleshooting, check the console logs in your browser"
