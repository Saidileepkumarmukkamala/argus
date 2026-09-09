#!/bin/sh
# Build NotchParade.app (no Xcode needed). Usage: ./build.sh && open NotchParade.app
set -e
cd "$(dirname "$0")"
swiftc -O -framework AppKit -o NotchParade NotchParade.swift
APP=NotchParade.app/Contents
mkdir -p "$APP/MacOS" "$APP/Resources"
cp NotchParade "$APP/MacOS/NotchParade"
rm -rf "$APP/Resources/clips"; cp -R ../clips "$APP/Resources/clips"          # bundle the library
[ -f AppIcon.icns ] && cp AppIcon.icns "$APP/Resources/AppIcon.icns"
cat > "$APP/Info.plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
 <key>CFBundleName</key><string>Notch Parade</string>
 <key>CFBundleDisplayName</key><string>Notch Parade</string>
 <key>CFBundleIdentifier</key><string>dev.notchparade.app</string>
 <key>CFBundleExecutable</key><string>NotchParade</string>
 <key>CFBundlePackageType</key><string>APPL</string>
 <key>CFBundleShortVersionString</key><string>0.1</string>
 <key>CFBundleVersion</key><string>1</string>
 <key>LSMinimumSystemVersion</key><string>14.0</string>
 <key>LSUIElement</key><true/>
 <key>CFBundleIconFile</key><string>AppIcon</string>
 <key>NSHighResolutionCapable</key><true/>
</dict></plist>
PLIST
codesign --force --deep --sign - NotchParade.app >/dev/null 2>&1 && echo "ad-hoc signed"
echo "built $APP"
if [ "$1" = "--dist" ]; then
  mkdir -p ../dist; rm -f ../dist/NotchParade.zip
  ditto -c -k --keepParent NotchParade.app ../dist/NotchParade.zip && ls -la ../dist/NotchParade.zip
fi
