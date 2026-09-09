#!/bin/sh
# Build Ledge.app (no Xcode needed). Usage: ./build.sh [--dist] && open Ledge.app
set -e
cd "$(dirname "$0")"
swiftc -O -framework AppKit -framework CoreWLAN -framework CoreLocation -framework ServiceManagement -o Ledge main.swift Ledge.swift Signals.swift Store.swift Shell.swift
APP=Ledge.app/Contents
rm -rf Ledge.app; mkdir -p "$APP/MacOS" "$APP/Resources"
cp Ledge "$APP/MacOS/Ledge"
cp Resources/oui.json "$APP/Resources/oui.json"
[ -f AppIcon.icns ] && cp AppIcon.icns "$APP/Resources/AppIcon.icns"
cat > "$APP/Info.plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
 <key>CFBundleName</key><string>Ledge</string>
 <key>CFBundleDisplayName</key><string>Ledge</string>
 <key>CFBundleIdentifier</key><string>app.ledge.mac</string>
 <key>CFBundleExecutable</key><string>Ledge</string>
 <key>CFBundlePackageType</key><string>APPL</string>
 <key>CFBundleShortVersionString</key><string>1.0</string>
 <key>CFBundleVersion</key><string>10</string>
 <key>LSMinimumSystemVersion</key><string>14.0</string>
 <key>LSUIElement</key><true/>
 <key>NSHighResolutionCapable</key><true/>
 <key>CFBundleIconFile</key><string>AppIcon</string>
 <key>NSLocationUsageDescription</key><string>macOS only reveals a Wi-Fi network's name to apps with Location access. Ledge uses it to label networks; it never records where you are.</string>
 <key>NSLocationWhenInUseUsageDescription</key><string>macOS only reveals a Wi-Fi network's name to apps with Location access. Ledge uses it to label networks; it never records where you are.</string>
</dict></plist>
PLIST
codesign --force --deep --sign - Ledge.app >/dev/null 2>&1 || true
echo "built $APP"
if [ "$1" = "--dist" ]; then
  mkdir -p ../dist; rm -f ../dist/Ledge.zip
  ditto -c -k --keepParent Ledge.app ../dist/Ledge.zip && ls -la ../dist/Ledge.zip
fi
