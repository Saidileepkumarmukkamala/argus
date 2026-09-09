#!/bin/sh
# Build Argus.app (no Xcode needed). Usage: ./build.sh [--dist] && open Argus.app
set -e
cd "$(dirname "$0")"
swiftc -O -framework AppKit -framework CoreWLAN -framework CoreLocation -framework ServiceManagement -framework Network -framework SystemConfiguration -framework CoreMediaIO -framework CoreAudio -o Argus main.swift Argus.swift Signals.swift Store.swift Shell.swift Devices.swift Stats.swift Taps.swift
APP=Argus.app/Contents
rm -rf Argus.app; mkdir -p "$APP/MacOS" "$APP/Resources"
cp Argus "$APP/MacOS/Argus"
cp Resources/oui.json "$APP/Resources/oui.json"
[ -f AppIcon.icns ] && cp AppIcon.icns "$APP/Resources/AppIcon.icns"
cat > "$APP/Info.plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
 <key>CFBundleName</key><string>Argus</string>
 <key>CFBundleDisplayName</key><string>Argus</string>
 <key>CFBundleIdentifier</key><string>app.argus.mac</string>
 <key>CFBundleExecutable</key><string>Argus</string>
 <key>CFBundlePackageType</key><string>APPL</string>
 <key>CFBundleShortVersionString</key><string>1.4.3</string>
 <key>CFBundleVersion</key><string>19</string>
 <key>LSMinimumSystemVersion</key><string>14.0</string>
 <key>LSUIElement</key><true/>
 <key>NSHighResolutionCapable</key><true/>
 <key>CFBundleIconFile</key><string>AppIcon</string>
 <key>NSLocationUsageDescription</key><string>macOS only reveals a Wi-Fi network's name to apps with Location access. Argus uses it to label networks; it never records where you are.</string>
 <key>NSLocationWhenInUseUsageDescription</key><string>macOS only reveals a Wi-Fi network's name to apps with Location access. Argus uses it to label networks; it never records where you are.</string>
</dict></plist>
PLIST
codesign --force --deep --sign - Argus.app >/dev/null 2>&1 || true
echo "built $APP"
if [ "$1" = "--dist" ]; then
  mkdir -p ../dist; rm -f ../dist/Argus.zip
  ditto -c -k --keepParent Argus.app ../dist/Argus.zip && ls -la ../dist/Argus.zip
fi
