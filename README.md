# Argus

Know what changed, from the notch. A free, open-source macOS app that watches the network you're on and what your
Mac exposes to it, and says in plain English when something changes: open Wi-Fi, VPN off, a server reachable by
everyone on the network, a router impersonation, HTTPS interception, a new device at home, a new background item.
It lives in the MacBook notch and is silent otherwise.

Site and download: https://saidileepkumarmukkamala.github.io/argus/

## What it is not
Not a firewall, not antivirus, not traffic inspection. It reads your Mac's own state and the network's shape using
public macOS tools, and it makes no network connections (one optional HTTPS check to apple.com, off by default).

## Verify
```
shasum -a 256 ~/Downloads/Argus.zip   # 1.4.0 -> 27dd7bed37acb4b04ece9d0591285ae42279ab2916de0dcc3ab922d57fdfe126
```

## Install (from a release)
macOS blocks apps that are not notarized by Apple. Argus is ad-hoc signed, so after dragging it to `/Applications`:
```
xattr -dr com.apple.quarantine /Applications/Argus.app
```
or double-click it once and use System Settings → Privacy & Security → **Open Anyway**. The Control-click → Open
shortcut was removed in macOS 15 and does not work for this.

## Build
```
cd app && ./build.sh            # needs Xcode command-line tools; output Argus.app (ad-hoc signed)
./build.sh --dist               # also zips to ../dist/Argus.zip
./Argus --dump                  # print everything Argus believes about this Mac, for auditing
ARGUS_DEMO=1 open Argus.app     # play sample cards
```

## Layout
- `app/main.swift` — entry, `--dump`
- `app/Argus.swift` — the notch panel, cards, status board, menu
- `app/Signals.swift` — collectors and the alert engine (event-driven via `NWPathMonitor` + `SCDynamicStore`, minute timers for the rest)
- `app/Store.swift` — persisted state in `~/Library/Application Support/Argus/state.json`; IEEE OUI vendor table
- `app/Shell.swift` — running built-in tools, port probes, the ARP nudge
- `docs/` — the site (GitHub Pages)
- `archive/animations/` — the project's first life as an animated-notch toy; unused by the app

## Signals and where they come from
| Signal | Source |
|---|---|
| Network identity, Wi-Fi security | `route -n get default`, `arp -n`, CoreWLAN (`security()`; `ssid()` only with Location) |
| VPN | tunnel interfaces with addresses (`ifconfig`), default route via `utun`/`ipsec`/`ppp` |
| DNS, proxy | `scutil --dns`, `scutil --proxy` |
| Exposed apps | `lsof -nP -iTCP -sTCP:LISTEN` bound to `*`, `0.0.0.0`, `[::]` or the LAN address |
| Sharing services | TCP connect to localhost 22, 5900, 445, 3283, 548 |
| Home devices | UDP nudge to the /24, then `arp -an`; vendor from the bundled OUI list |
| Router impersonation | gateway MAC changes while gateway IP, interface and local address stay the same |
| HTTPS interception (optional) | `curl -v https://www.apple.com` issuer line |
| Persistence | `~/Library/LaunchAgents`, `/Library/LaunchAgents`, `/Library/LaunchDaemons`, `sfltool dumpbtm` |
| Integrity | md5 of `/etc/hosts`, `~/.ssh/authorized_keys`, shell rc files; `crontab -l`; `systemextensionsctl list`; `security dump-trust-settings` |
| Keystroke taps | `CGGetEventTapList` — any process tapping keyDown/keyUp/flagsChanged, with its code signer |
| Live remote sessions | `who` for network logins, plus the Screen Sharing daemon and its peer address |
| Notarization | `spctl --assess --type execute` on app launch (NSWorkspace notification) |
| Board | `fdesetup`, `socketfilterfw`, `spctl --status`, `csrutil`, `sysadminctl -screenLock`, `defaults` (SoftwareUpdate, loginwindow, sharingd), XProtect plist date, `profiles`, `sudo -n true`, `dscl` |

## False-alarm policy
Baseline silently on first launch; announce only changes. Debounce VPN state (10 s). Suppress DNS alerts within 90 s
of a network or VPN transition. Per-key quiet periods (10 min to 30 days). Home networks are quiet unless something
matters. Amber only when a decision is needed; green for information. If Argus says something that turns out to be
wrong, that is a bug: open an issue.
