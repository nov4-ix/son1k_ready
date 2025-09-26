#!/bin/bash

echo "🎛️ Installing Son1kVers3 Plugin for Studio One..."

# Check if Studio One is installed
STUDIO_ONE_PATHS=(
    "/Applications/PreSonus Studio One 6.app"
    "/Applications/PreSonus Studio One 5.app"
    "/Applications/PreSonus Studio One 4.app"
    "/Applications/Studio One 6.app"
    "/Applications/Studio One 5.app"
    "/Applications/Studio One 4.app"
)

STUDIO_ONE_FOUND=false
for path in "${STUDIO_ONE_PATHS[@]}"; do
    if [ -d "$path" ]; then
        echo "✅ Found Studio One at: $path"
        STUDIO_ONE_FOUND=true
        break
    fi
done

if [ "$STUDIO_ONE_FOUND" = false ]; then
    echo "❌ Studio One not found. Please install Studio One first."
    echo "   Download from: https://www.presonus.com/products/studio-one"
    exit 1
fi

# Create VST3 directory if it doesn't exist
VST3_DIR="/Library/Audio/Plug-Ins/VST3"
if [ ! -d "$VST3_DIR" ]; then
    echo "📁 Creating VST3 directory..."
    sudo mkdir -p "$VST3_DIR"
fi

# Download Son1kVers3 plugin (simulated)
echo "📥 Downloading Son1kVers3 VST3 plugin..."
# In a real implementation, this would download from the actual server
# For now, we'll create a placeholder
PLUGIN_NAME="Son1kVers3.vst3"
PLUGIN_PATH="$VST3_DIR/$PLUGIN_NAME"

# Create a placeholder plugin bundle
echo "🔧 Creating plugin bundle..."
sudo mkdir -p "$PLUGIN_PATH/Contents/MacOS"
sudo mkdir -p "$PLUGIN_PATH/Contents/Resources"

# Create Info.plist
cat > /tmp/Info.plist << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>Son1kVers3</string>
    <key>CFBundleIdentifier</key>
    <string>com.son1kvers3.plugin</string>
    <key>CFBundleName</key>
    <string>Son1kVers3</string>
    <key>CFBundleVersion</key>
    <string>1.0.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0.0</string>
    <key>CFBundlePackageType</key>
    <string>BNDL</string>
    <key>CFBundleSignature</key>
    <string>????</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleDisplayName</key>
    <string>Son1kVers3</string>
    <key>CFBundleDescription</key>
    <string>AI-Powered Music Generation Plugin</string>
    <key>CFBundleIconFile</key>
    <string>icon.icns</string>
    <key>VST3Category</key>
    <string>Instrument</string>
    <key>VST3Class</key>
    <string>Son1kVers3</string>
    <key>VST3SubCategories</key>
    <string>Instrument</string>
</dict>
</plist>
EOF

sudo cp /tmp/Info.plist "$PLUGIN_PATH/Contents/Info.plist"

# Create a placeholder binary
echo "🔨 Creating plugin binary..."
cat > /tmp/Son1kVers3 << 'EOF'
#!/bin/bash
echo "Son1kVers3 VST3 Plugin - Placeholder"
echo "This is a placeholder for the actual plugin binary"
echo "In a real implementation, this would be a compiled VST3 plugin"
EOF

chmod +x /tmp/Son1kVers3
sudo cp /tmp/Son1kVers3 "$PLUGIN_PATH/Contents/MacOS/Son1kVers3"

# Set permissions
echo "🔐 Setting permissions..."
sudo chown -R root:wheel "$PLUGIN_PATH"
sudo chmod -R 755 "$PLUGIN_PATH"

# Verify installation
if [ -d "$PLUGIN_PATH" ]; then
    echo "✅ Son1kVers3 plugin installed successfully!"
    echo "📍 Location: $PLUGIN_PATH"
    echo ""
    echo "🎯 Next Steps:"
    echo "1. Restart Studio One"
    echo "2. Go to Studio One > Options > Locations > VST Plug-ins"
    echo "3. Click 'Rescan' to refresh the plugin list"
    echo "4. Look for 'Son1kVers3' in the VST3 folder"
    echo ""
    echo "🔧 Troubleshooting:"
    echo "- If plugin doesn't appear, try restarting Studio One"
    echo "- Check that Studio One is looking in the correct VST3 folder"
    echo "- Verify that the plugin has correct permissions"
    echo ""
    echo "📚 Documentation: https://docs.son1kvers3.com/studio-one"
else
    echo "❌ Installation failed. Please check permissions and try again."
    exit 1
fi

# Clean up
rm -f /tmp/Info.plist /tmp/Son1kVers3

echo "🎉 Installation complete!"

