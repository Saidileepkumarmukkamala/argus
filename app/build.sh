#!/bin/sh
# Build Ledge.app (no Xcode needed). Usage: ./build.sh [--dist] && open Ledge.app
set -e
cd "$(dirname "$0")"
swiftc -O -framework AppKit -o Ledge Ledge.swift
APP=Ledge.app/Contents
mkdir -p "$APP/MacOS" "$APP/Resources"
cp Ledge "$APP/MacOS/Ledge"
rm -rf "$APP/Resources/clips"; cp -R ../clips "$APP/Resources/clips"          # bundle the library
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
 <key>CFBundleShortVersionString</key><string>0.2.1</string>
 <key>CFBundleVersion</key><string>3</string>
 <key>LSMinimumSystemVersion</key><string>14.0</string>
 <key>LSUIElement</key><true/>
 <key>CFBundleIconFile</key><string>AppIcon</string>
 <key>NSHighResolutionCapable</key><true/>
</dict></plist>
PLIST
codesign --force --deep --sign - Ledge.app >/dev/null 2>&1 && echo "ad-hoc signed"
echo "built $APP"
if [ "$1" = "--dist" ]; then
  mkdir -p ../dist; rm -f ../dist/Ledge.zip
  ditto -c -k --keepParent Ledge.app ../dist/Ledge.zip && ls -la ../dist/Ledge.zip
fi
