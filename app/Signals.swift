import Foundation
import CoreWLAN
import Network
import SystemConfiguration

enum Level { case info, notice, warning }
struct Alert { let level: Level; let title: String; let detail: String; let key: String; let sticky: Bool }

struct NetInfo: Equatable {
    var iface = ""; var gatewayIP = ""; var gatewayMAC = ""; var localIP = ""; var ssid: String? = nil
    var isWiFi = false; var securityName = ""; var securityLevel = 0     // 0 unknown/wired · 1 open · 2 weak · 3 good
    var key: String { gatewayMAC.isEmpty ? "\(iface)@\(gatewayIP)" : gatewayMAC }
    var displayName: String { ssid ?? (isWiFi ? "Wi-Fi via \(gatewayIP)" : (iface.isEmpty ? "No network" : "Wired via \(gatewayIP)")) }
    var online: Bool { !gatewayIP.isEmpty }
}

enum Collect {
    /// Time-to-live cache for the few probes that are comparatively slow. Everything Argus runs works as a normal user:
    /// nothing here needs root, so macOS never shows an authorisation dialog.
    private static var cache: [String: (value: Any, at: Date)] = [:]
    private static let cacheLock = NSLock()
    static func cached<T>(_ key: String, ttl: TimeInterval, _ make: () -> T) -> T {
        cacheLock.lock()
        if let e = cache[key], Date().timeIntervalSince(e.at) < ttl, let v = e.value as? T { cacheLock.unlock(); return v }
        cacheLock.unlock()
        let v = make()
        cacheLock.lock(); cache[key] = (v, Date()); cacheLock.unlock()
        return v
    }
    static func normalizeMAC(_ s: String) -> String {
        s.split(separator: ":").map { String(format: "%02x", Int($0, radix: 16) ?? 0) }.joined(separator: ":")
    }
    static func firstMatch(_ text: String, _ pattern: String) -> String? {
        guard let re = try? NSRegularExpression(pattern: pattern), let m = re.firstMatch(in: text, range: NSRange(text.startIndex..., in: text)), m.numberOfRanges > 1,
              let r = Range(m.range(at: 1), in: text) else { return nil }
        return String(text[r])
    }

    static func network(locationAllowed: Bool) -> NetInfo {
        var n = NetInfo()
        let route = sh("/sbin/route", ["-n", "get", "default"])
        n.gatewayIP = firstMatch(route, #"gateway:\s*(\S+)"#) ?? ""
        n.iface = firstMatch(route, #"interface:\s*(\S+)"#) ?? ""
        guard !n.iface.isEmpty else { return n }
        n.localIP = firstMatch(sh("/sbin/ifconfig", [n.iface]), #"inet (\d+\.\d+\.\d+\.\d+)"#) ?? ""
        if let mac = firstMatch(sh("/usr/sbin/arp", ["-n", n.gatewayIP]), #" at ([0-9a-f:]+) "#), mac != "(incomplete)" { n.gatewayMAC = normalizeMAC(mac) }
        if let w = CWWiFiClient.shared().interface(withName: n.iface) {
            n.isWiFi = true
            if locationAllowed { n.ssid = w.ssid() }
            switch w.security() {
            case .none, .OWE, .oweTransition: n.securityName = w.security() == .none ? "Open" : "Open (OWE)"; n.securityLevel = w.security() == .none ? 1 : 3
            case .WEP, .dynamicWEP, .wpaPersonal, .wpaPersonalMixed, .wpaEnterprise, .wpaEnterpriseMixed: n.securityName = "WPA / WEP (weak)"; n.securityLevel = 2
            case .wpa2Personal, .personal, .wpa2Enterprise, .enterprise: n.securityName = "WPA2"; n.securityLevel = 3
            case .wpa3Personal, .wpa3Enterprise, .wpa3Transition: n.securityName = "WPA3"; n.securityLevel = 3
            default: n.securityName = "Unknown"; n.securityLevel = 0
            }
        }
        return n
    }

    /// VPN = a tunnel interface carrying a real address, or the default route going through one.
    static func vpnActive() -> Bool {
        let route = sh("/sbin/route", ["-n", "get", "default"])
        if let i = firstMatch(route, #"interface:\s*(\S+)"#), i.hasPrefix("utun") || i.hasPrefix("ipsec") || i.hasPrefix("ppp") { return true }
        let all = sh("/sbin/ifconfig", ["-a"])
        var cur = ""
        for line in all.split(separator: "\n") {
            let s = String(line)
            if !s.hasPrefix("\t") && !s.hasPrefix(" ") { cur = String(s.prefix(while: { $0 != ":" })); continue }
            guard cur.hasPrefix("utun") || cur.hasPrefix("ipsec") || cur.hasPrefix("ppp") || cur.hasPrefix("tun") || cur.hasPrefix("wg") else { continue }
            if s.contains("inet ") && !s.contains("127.0.0.1") { return true }
            if s.contains("inet6 ") && !s.contains("fe80") && !s.contains("::1") { return true }
        }
        return false
    }

    static func dnsServers() -> [String] {
        let out = sh("/usr/sbin/scutil", ["--dns"])
        guard let block = out.components(separatedBy: "resolver #1").dropFirst().first?.components(separatedBy: "resolver #2").first else { return [] }
        return block.split(separator: "\n").compactMap { firstMatch(String($0), #"nameserver\[\d+\]\s*:\s*(\S+)"#) }
    }
    static func dnsClass(_ servers: [String], net: NetInfo) -> String {
        guard let s = servers.first(where: { $0.contains(".") }) ?? servers.first else { return "no resolver" }
        let known: [String: String] = ["1.1.1.1": "Cloudflare", "1.0.0.1": "Cloudflare", "8.8.8.8": "Google", "8.8.4.4": "Google", "9.9.9.9": "Quad9", "149.112.112.112": "Quad9", "208.67.222.222": "OpenDNS", "94.140.14.14": "AdGuard"]
        if let k = known[s] { return "\(k) public resolver" }
        if s == net.gatewayIP { return "the router (\(s))" }
        if s.hasPrefix("10.") || s.hasPrefix("192.168.") || s.hasPrefix("172.") { return "a private resolver (\(s))" }
        if s.hasPrefix("100.") { return "the VPN's resolver (\(s))" }
        return "\(s) (outside this network, usually your provider)"
    }

    struct Listener: Hashable { let process: String; let port: Int; let exposed: Bool }
    static let systemListeners: Set<String> = ["ControlCe", "rapportd", "sharingd", "AirPlayXP", "launchd", "identitys", "remoted", "Spotlight", "mDNSRespo", "Bluetooth", "AirPlayUI"]
    static var localIPForExposure = ""
    static func listeners() -> [Listener] {
        var out: [Listener] = []
        for line in sh("/usr/sbin/lsof", ["-nP", "-iTCP", "-sTCP:LISTEN"]).split(separator: "\n").dropFirst() {
            var cols = line.split(separator: " ", omittingEmptySubsequences: true).map(String.init)
            if cols.last == "(LISTEN)" { cols.removeLast() }                       // lsof appends the state in parentheses
            guard cols.count >= 9, let name = cols.last, let portStr = name.split(separator: ":").last, let port = Int(portStr) else { continue }
            let host = String(name.dropLast(portStr.count + 1))
            let exposed = host == "*" || host == "0.0.0.0" || host == "[::]" || (!localIPForExposure.isEmpty && host == localIPForExposure)
            out.append(Listener(process: cols[0], port: port, exposed: exposed))
        }
        return Array(Set(out))
    }

    static let sharingPorts: [(Int, String)] = [(22, "Remote Login (SSH)"), (5900, "Screen Sharing"), (445, "File Sharing"), (3283, "Remote Management"), (548, "File Sharing (AFP)")]
    static func sharingOn() -> [String] { sharingPorts.filter { portOpen($0.0) }.map { $0.1 } }

    static func lanDevices(net: NetInfo) -> [(ip: String, mac: String)] {
        guard net.localIP.contains(".") else { return [] }
        let prefix = net.localIP.split(separator: ".").prefix(3).joined(separator: ".")
        arpSweep(prefix: prefix); usleep(600_000)
        var out: [(String, String)] = []
        for line in sh("/usr/sbin/arp", ["-an"]).split(separator: "\n") {
            let s = String(line)
            guard s.contains(" on \(net.iface) "), !s.contains("incomplete"), !s.contains("permanent"),
                  let ip = firstMatch(s, #"\((\d+\.\d+\.\d+\.\d+)\)"#), let mac = firstMatch(s, #" at ([0-9a-f:]+) "#) else { continue }
            if ip.hasSuffix(".255") || mac == "ff:ff:ff:ff:ff:ff" || ip == net.localIP { continue }
            out.append((ip, normalizeMAC(mac)))
        }
        return out
    }

    static func proxy() -> String? {
        let out = sh("/usr/sbin/scutil", ["--proxy"])
        func on(_ k: String) -> Bool { firstMatch(out, k + #"\s*:\s*(\d)"#) == "1" }
        if on("HTTPEnable") || on("HTTPSEnable") { return "HTTP proxy " + (firstMatch(out, #"HTTPProxy\s*:\s*(\S+)"#) ?? firstMatch(out, #"HTTPSProxy\s*:\s*(\S+)"#) ?? "") }
        if on("SOCKSEnable") { return "SOCKS proxy " + (firstMatch(out, #"SOCKSProxy\s*:\s*(\S+)"#) ?? "") }
        if on("ProxyAutoConfigEnable") { return "auto proxy (PAC) " + (firstMatch(out, #"ProxyAutoConfigURLString\s*:\s*(\S+)"#) ?? "") }
        return nil
    }
    static func computerName() -> String { sh("/usr/sbin/scutil", ["--get", "ComputerName"]).trimmingCharacters(in: .whitespacesAndNewlines) }
    static func persistenceItems() -> [String] {
        var items: [String] = []
        let home = NSHomeDirectory()
        for dir in ["\(home)/Library/LaunchAgents", "/Library/LaunchAgents", "/Library/LaunchDaemons"] {
            for f in (try? FileManager.default.contentsOfDirectory(atPath: dir)) ?? [] where f.hasSuffix(".plist") { items.append((dir.hasPrefix(home) ? "~" : "") + dir.split(separator: "/").last! + "/" + f) }
        }
        // Deliberately NOT sfltool dumpbtm: it requires root and pops an authorisation dialog. launchctl lists what is
        // actually loaded in this user's session and needs no privileges at all.
        for line in sh("/bin/launchctl", ["list"], timeout: 8).split(separator: "\n").dropFirst() {
            let cols = line.split(separator: "\t", omittingEmptySubsequences: false).map(String.init)
            guard cols.count >= 3 else { continue }
            let label = cols[2].trimmingCharacters(in: .whitespaces)
            guard !label.isEmpty, !label.hasPrefix("com.apple."), !label.hasPrefix("application.") else { continue }
            items.append("job " + label)
        }
        return Array(Set(items)).sorted()
    }
    static func hostsHash() -> String { sh("/sbin/md5", ["-q", "/etc/hosts"]).trimmingCharacters(in: .whitespacesAndNewlines) }
    static func customRoots() -> Int {
        let a = sh("/usr/bin/security", ["dump-trust-settings", "-d"]), u = sh("/usr/bin/security", ["dump-trust-settings"])
        return (a + u).components(separatedBy: "Cert ").count - 1
    }
    static func profilesCount() -> Int { cached("profiles", ttl: 1800) { Int(firstMatch(sh("/usr/bin/profiles", ["list"]), #"There are (\d+)"#) ?? "0") ?? 0 } }
    static func airdrop() -> String { let v = sh("/usr/bin/defaults", ["read", "com.apple.sharingd", "DiscoverableMode"]).trimmingCharacters(in: .whitespacesAndNewlines); return v.isEmpty || v.contains("does not exist") ? "Contacts Only (default)" : v }
    static func xprotect() -> (version: String, days: Int) { cached("xprotect", ttl: 3600) { xprotectRaw() } }
    private static func xprotectRaw() -> (version: String, days: Int) {
        let p = "/Library/Apple/System/Library/CoreServices/XProtect.bundle/Contents/Info.plist"
        let v = sh("/usr/bin/defaults", ["read", p, "CFBundleShortVersionString"]).trimmingCharacters(in: .whitespacesAndNewlines)
        let m = (try? FileManager.default.attributesOfItem(atPath: p)[.modificationDate] as? Date) ?? Date()
        return (v, Int(Date().timeIntervalSince(m) / 86400))
    }
    static func notarized(_ path: String) -> Bool { sh("/usr/sbin/spctl", ["--assess", "--type", "execute", path], timeout: 15).contains("accepted") }
    /// `defaults read` prints an error line (starting with a timestamp) when a key is absent; only a bare number is a value.
    static func defaultsInt(_ domain: String, _ key: String) -> Int? {
        let out = sh("/usr/bin/defaults", ["read", domain, key]).trimmingCharacters(in: .whitespacesAndNewlines)
        return out.contains("does not exist") ? nil : Int(out)
    }

    /// TLS interception probe: the ONLY network connection Argus ever makes, and only when the user turned it on.
    static func tlsProbe() -> (ok: Bool, issuer: String, captive: Bool) {
        let out = sh("/usr/bin/curl", ["-sv", "--max-time", "6", "-o", "/dev/null", "https://www.apple.com/"], timeout: 10)
        let issuer = firstMatch(out, #"issuer:\s*(.+)"#)?.trimmingCharacters(in: .whitespaces) ?? ""
        if out.contains("SSL certificate problem") || out.contains("certificate verify") { return (false, issuer, true) }
        if issuer.isEmpty { return (true, "", false) }                  // couldn't tell (offline); don't alarm
        return (issuer.contains("Apple Inc"), issuer, false)
    }
    static func mdm() -> String {
        cached("mdm", ttl: 3600) { firstMatch(sh("/usr/bin/profiles", ["status", "-type", "enrollment"]), #"MDM enrollment:\s*(.+)"#)?.trimmingCharacters(in: .whitespaces) ?? "Unknown" }
    }
    static func systemExtensions() -> [String] {
        sh("/usr/bin/systemextensionsctl", ["list"]).split(separator: "\n").compactMap { line -> String? in
            let s = String(line); guard s.hasPrefix("\t") || s.hasPrefix(" "), s.contains("["), let id = firstMatch(s, #"\s([a-zA-Z0-9.\-]+\.[a-zA-Z0-9\-]+) \("#) else { return nil }; return id }
    }
    static func fileHash(_ path: String) -> String { let p = (path as NSString).expandingTildeInPath; return FileManager.default.fileExists(atPath: p) ? sh("/sbin/md5", ["-q", p]).trimmingCharacters(in: .whitespacesAndNewlines) : "absent" }
    static func cronHash() -> String { let o = sh("/usr/bin/crontab", ["-l"]); return o.contains("no crontab") ? "absent" : String(o.hashValue) }

    struct PostureRow { let label: String; let ok: Bool; let value: String; let hint: String }
    static func posture(net: NetInfo, vpn: Bool, quick: Bool = false) -> [PostureRow] {
        var rows: [PostureRow] = []
        let fv = sh("/usr/bin/fdesetup", ["status"]).contains("FileVault is On")
        rows.append(.init(label: "Disk encryption", ok: fv, value: fv ? "FileVault on" : "FileVault off", hint: "System Settings › Privacy & Security › FileVault"))
        let fw = sh("/usr/libexec/ApplicationFirewall/socketfilterfw", ["--getglobalstate"]).contains("enabled")
        rows.append(.init(label: "Firewall", ok: fw, value: fw ? "On" : "Off", hint: "System Settings › Network › Firewall"))
        let gk = sh("/usr/sbin/spctl", ["--status"]).contains("enabled")
        rows.append(.init(label: "Gatekeeper", ok: gk, value: gk ? "On" : "Off", hint: "Only opens apps that pass Apple's checks"))
        let sip = sh("/usr/bin/csrutil", ["status"]).contains("enabled")
        rows.append(.init(label: "System integrity", ok: sip, value: sip ? "On" : "Off", hint: "SIP protects system files"))
        let lock = sh("/usr/sbin/sysadminctl", ["-screenLock", "status"])
        let lockOk = lock.contains("immediate") || (firstMatch(lock, #"delay is (\d+)"#).flatMap { Int($0) }.map { $0 <= 300 } ?? false)
        rows.append(.init(label: "Screen lock", ok: lockOk, value: lock.contains("immediate") ? "Immediately" : (lock.contains("off") ? "Off" : "Delayed"), hint: "Lock Screen › Require password after screen saver"))
        let sharing = sharingOn()
        rows.append(.init(label: "Sharing services", ok: sharing.isEmpty, value: sharing.isEmpty ? "None on" : sharing.joined(separator: ", "), hint: "System Settings › General › Sharing"))
        let exposed = listeners().filter { $0.exposed && !systemListeners.contains($0.process) }
        rows.append(.init(label: "Apps open to the network", ok: exposed.isEmpty, value: exposed.isEmpty ? "None" : exposed.map { "\($0.process):\($0.port)" }.sorted().joined(separator: " "), hint: "Bind dev servers to localhost when you're not at home"))
        let upd = defaultsInt("/Library/Preferences/com.apple.SoftwareUpdate", "LastUpdatesAvailable") ?? 0
        let lcOut = sh("/usr/bin/defaults", ["read", "/Library/Preferences/com.apple.SoftwareUpdate", "LastSuccessfulDate"])
        let lastCheck = lcOut.contains("does not exist") ? nil : firstMatch(lcOut, #"(\d{4}-\d{2}-\d{2})"#)
        var checkDays = -1
        if let lc = lastCheck { let f = DateFormatter(); f.dateFormat = "yyyy-MM-dd"; if let d = f.date(from: lc) { checkDays = Int(Date().timeIntervalSince(d) / 86400) } }
        let updOk = upd == 0 && checkDays >= 0 && checkDays <= 7
        rows.append(.init(label: "Software updates", ok: updOk, value: upd > 0 ? "\(upd) pending" : (checkDays < 0 ? "Never checked" : "None pending · checked \(checkDays)d ago"), hint: "System Settings › General › Software Update"))
        let stealthOut = sh("/usr/libexec/ApplicationFirewall/socketfilterfw", ["--getstealthmode"]).lowercased()
        let stealth = stealthOut.contains("enabled") || stealthOut.contains(" on")
        rows.append(.init(label: "Stealth mode", ok: stealth, value: stealth ? "On" : "Off", hint: "Firewall › Options › Enable stealth mode: your Mac ignores probes"))
        let ad = airdrop()
        rows.append(.init(label: "AirDrop visibility", ok: ad != "Everyone", value: ad, hint: "Everyone = strangers can send you files"))
        let guest = defaultsInt("/Library/Preferences/com.apple.loginwindow", "GuestEnabled") ?? 0
        rows.append(.init(label: "Guest account", ok: guest == 0, value: guest == 0 ? "Off" : "On", hint: "Users & Groups › Guest User"))
        let alOut = sh("/usr/bin/defaults", ["read", "/Library/Preferences/com.apple.loginwindow", "autoLoginUser"]).trimmingCharacters(in: .whitespacesAndNewlines)
        let autoLogin = !alOut.isEmpty && !alOut.contains("does not exist")
        rows.append(.init(label: "Automatic login", ok: !autoLogin, value: autoLogin ? "On" : "Off", hint: "Anyone who opens the lid is you"))
        let autoInstall = defaultsInt("/Library/Preferences/com.apple.SoftwareUpdate", "AutomaticallyInstallMacOSUpdates") ?? 0
        let autoCheck = defaultsInt("/Library/Preferences/com.apple.SoftwareUpdate", "AutomaticCheckEnabled") ?? 1
        rows.append(.init(label: "Automatic updates", ok: autoCheck == 1, value: autoInstall == 1 ? "Install automatically" : (autoCheck == 1 ? "Check only" : "Off"), hint: "General › Software Update › Automatic updates"))
        let xp = xprotect()
        rows.append(.init(label: "Malware definitions", ok: xp.days <= 45, value: "v\(xp.version) · \(xp.days)d ago", hint: "Apple's XProtect, updated silently"))
        let roots = customRoots()
        rows.append(.init(label: "Custom root certificates", ok: roots == 0, value: roots == 0 ? "None" : "\(roots) trusted", hint: "A custom root lets its owner read your encrypted traffic"))
        let prof = profilesCount()
        rows.append(.init(label: "Configuration profiles", ok: true, value: prof == 0 ? "None" : "\(prof) installed", hint: "Management profiles can change network and security settings"))
        let px = proxy()
        rows.append(.init(label: "Proxy", ok: px == nil, value: px ?? "None", hint: "A proxy sees every request that goes through it"))
        let admin = sh("/usr/bin/dscl", [".", "-read", "/Groups/admin", "GroupMembership"]).contains(" " + NSUserName())
        rows.append(.init(label: "Your account", ok: true, value: admin ? "Administrator" : "Standard", hint: "A standard account for daily use limits what malware can do"))
        let analytics = defaultsInt("/Library/Application Support/CrashReporter/DiagnosticMessagesHistory.plist", "AutoSubmit") ?? 0
        rows.append(.init(label: "Share analytics with Apple", ok: true, value: analytics == 1 ? "On" : "Off", hint: ""))
        rows.append(.init(label: "Visible as", ok: true, value: computerName(), hint: "Your Mac's name on every network"))
        let m = mdm()
        rows.append(.init(label: "Device management", ok: true, value: m.hasPrefix("No") ? "Not enrolled" : m, hint: "An MDM can read settings and install profiles"))
        let ext = systemExtensions()
        rows.append(.init(label: "System extensions", ok: true, value: ext.isEmpty ? "None" : "\(ext.count) active", hint: "VPNs, security tools and virtual cameras install these"))
        let netOk = !net.isWiFi || net.securityLevel == 3 || vpn
        rows.append(.init(label: "This network", ok: netOk, value: net.isWiFi ? "\(net.displayName) · \(net.securityName)" : net.displayName, hint: vpn ? "VPN is on" : (netOk ? "Encrypted" : "Use a VPN here")))
        rows.append(.init(label: "VPN", ok: true, value: vpn ? "Connected" : "Not connected", hint: ""))
        return rows
    }
}

/// Watches the signals on timers and turns changes into a small number of plain-English alerts.
final class Monitor {
    var onAlert: ((Alert) -> Void)?
    var onPosture: (([Collect.PostureRow]) -> Void)?
    var net = NetInfo(); var vpn: Bool? = nil; var dns: [String] = []; var locationAllowed = false
    private var vpnCandidate: Bool? = nil; private var lastTransition = Date.distantPast
    /// The status board is expensive (~20 short shell calls). It is computed off the main thread and cached, so a
    /// click renders instantly and the fresh result swaps in when it arrives.
    private(set) var cachedPosture: [Collect.PostureRow] = []
    private var postureBusy = false
    func refreshPosture(_ done: (([Collect.PostureRow]) -> Void)? = nil) {
        if postureBusy { return }
        postureBusy = true
        q.async { [weak self] in
            guard let s = self else { return }
            let rows = Collect.posture(net: s.net, vpn: s.vpn ?? false)
            DispatchQueue.main.async { s.cachedPosture = rows; s.postureBusy = false; s.onPosture?(rows); done?(rows) }
        }
    }
    private var started = false
    let q = DispatchQueue(label: "argus.monitor", qos: .utility)

    private var pathMonitor: NWPathMonitor?
    private var dynStore: SCDynamicStore?
    /// Network, DNS and proxy changes arrive as system events; the heartbeat is a safety net, not the mechanism.
    func start() {
        guard !started else { return }; started = true
        let pm = NWPathMonitor(); pm.pathUpdateHandler = { [weak self] _ in self?.poke() }; pm.start(queue: q); pathMonitor = pm
        var ctx = SCDynamicStoreContext(version: 0, info: Unmanaged.passUnretained(self).toOpaque(), retain: nil, release: nil, copyDescription: nil)
        if let store = SCDynamicStoreCreate(nil, "Argus" as CFString, { _, _, info in Unmanaged<Monitor>.fromOpaque(info!).takeUnretainedValue().poke() }, &ctx) {
            SCDynamicStoreSetNotificationKeys(store, nil, ["State:/Network/Global/.*", "State:/Network/Service/.*/DNS", "State:/Network/Interface/.*/Link"] as CFArray)
            if let src = SCDynamicStoreCreateRunLoopSource(nil, store, 0) { CFRunLoopAddSource(CFRunLoopGetMain(), src, .commonModes) }
            dynStore = store
        }
        let fast = ProcessInfo.processInfo.environment["ARGUS_FAST"] != nil          // test knob: minute timers become seconds
        schedule(fast ? 15 : 60) { self.fastTick() }; schedule(fast ? 15 : 60) { self.mediumTick() }; schedule(fast ? 60 : 300) { self.slowTick() }; schedule(fast ? 30 : 600) { self.integrityTick(first: false) }
        let fresh = Store.shared.state.networks.isEmpty
        refreshPosture()
        q.async { self.fastTick(); self.mediumTick(first: true); self.integrityTick(first: true)
            if fresh { self.emit(.notice, "Argus is watching", "Network changes, VPN, and what your Mac exposes. Click the notch any time for the status board.", key: "welcome", minGap: 1) } }
    }
    private func schedule(_ every: Double, _ f: @escaping () -> Void) {
        let t = DispatchSource.makeTimerSource(queue: q); t.schedule(deadline: .now() + every, repeating: every); t.setEventHandler(handler: f); t.resume(); timers.append(t)
    }
    private var timers: [DispatchSourceTimer] = []
    private var pokePending = false
    /// A system event: look now, and again in 10 s so the VPN debounce can settle.
    func poke() {
        q.async { [weak self] in
            guard let s = self, !s.pokePending else { return }; s.pokePending = true
            s.q.asyncAfter(deadline: .now() + 1.5) { s.fastTick(); s.pokePending = false; s.q.asyncAfter(deadline: .now() + 10) { s.fastTick() } }
        }
    }

    func emit(_ level: Level, _ title: String, _ detail: String, key: String, sticky: Bool = false, minGap: TimeInterval = 600) {
        let st = Store.shared
        if let p = st.state.pausedUntil, p > Date() { return }
        if let last = st.state.lastAlert[key], Date().timeIntervalSince(last) < minGap { return }
        st.state.lastAlert[key] = Date(); st.save()
        let a = Alert(level: level, title: title, detail: detail, key: key, sticky: sticky)
        st.state.events.append(EventRecord(time: Date(), title: title, detail: detail, level: level == .warning ? "warning" : (level == .notice ? "notice" : "info")))
        if st.state.events.count > 40 { st.state.events.removeFirst(st.state.events.count - 40) }
        st.save()
        NSLog("alert [%@] %@ — %@", key, title, detail)
        DispatchQueue.main.async { self.onAlert?(a); self.refreshPosture() }
    }

    func fastTick() {
        let now = Collect.network(locationAllowed: locationAllowed)
        Collect.localIPForExposure = now.localIP
        let raw = Collect.vpnActive()
        // Debounce: a state has to hold for two consecutive ticks (10 s) before it counts. Wake-from-sleep flaps otherwise.
        var v = vpn ?? raw
        if raw == vpnCandidate { v = raw } else { vpnCandidate = raw }
        if now.key != net.key { lastTransition = Date(); networkChanged(from: net, to: now, vpn: v) }
        else if now.ssid != nil && net.ssid == nil { net.ssid = now.ssid; if var r = Store.shared.state.networks[now.key] { r.name = now.displayName; Store.shared.state.networks[now.key] = r; Store.shared.save() } }
        if let old = vpn, old != v {
            lastTransition = Date()
            let untrusted = now.isWiFi && (now.securityLevel < 3 || !(Store.shared.state.networks[now.key]?.isHome ?? false))
            if v { emit(.notice, "VPN connected", "Your traffic now goes through the tunnel.", key: "vpn-up", minGap: 60) }
            else { emit(untrusted ? .warning : .notice, "VPN disconnected", "You're on \(now.displayName) directly now." + (untrusted ? " Reconnect if you meant to stay tunnelled." : ""), key: "vpn-down", sticky: untrusted, minGap: 60) }
            if v, var r = Store.shared.state.networks[now.key] { r.vpnSeen = true; Store.shared.state.networks[now.key] = r; Store.shared.save() }
        }
        vpn = v
        let d = Collect.dnsServers()
        if !dns.isEmpty && d != dns && now.key == net.key && !d.isEmpty && Date().timeIntervalSince(lastTransition) > 90 {
            emit(.notice, "DNS resolver changed", "Lookups now go to \(Collect.dnsClass(d, net: now)). Normal after a VPN or network change; unexpected otherwise.", key: "dns-\(d.first ?? "")", minGap: 900)
        }
        dns = d
        net = now
    }

    // internal so --selftest can drive it with synthetic transitions
    func networkChanged(from old: NetInfo, to new: NetInfo, vpn: Bool) {
        guard new.online else {
            if old.online { emit(.info, "Offline", "No default route.", key: "offline", minGap: 60) }
            return
        }
        let st = Store.shared
        // Gateway impersonation: same router address, same interface, same local address, but the router's hardware
        // identity changed under us. Classic ARP spoofing, or a router that was swapped/rebooted with new hardware.
        if old.online, old.gatewayIP == new.gatewayIP, old.iface == new.iface, old.localIP == new.localIP,
           !old.gatewayMAC.isEmpty, !new.gatewayMAC.isEmpty, old.gatewayMAC != new.gatewayMAC {
            let vendor = Vendors.shared.lookup(new.gatewayMAC)
            let who = vendor.hasPrefix("Unknown") ? "" : " (\(vendor))"
            emit(.warning, "Router identity changed", "The gateway at \(new.gatewayIP) is now answering from different hardware\(who). That is what ARP spoofing looks like; it is also what a replaced or rebooted router looks like. Prefer a VPN until you know which.", key: "gw-\(new.key)", sticky: true, minGap: 600)
            // Deliberately do NOT record this gateway as a known network. Persisting it would both bless the impostor
            // and let it masquerade later as the "network you knew" in the same-name check below.
            net = new
            return
        }
        var rec = st.state.networks[new.key]
        let first = rec == nil
        if rec == nil { rec = NetworkRecord(key: new.key, name: new.displayName, security: new.securityName, firstSeen: Date(), lastSeen: Date()) }
        rec!.lastSeen = Date(); rec!.visits += first ? 0 : 1; rec!.security = new.securityName
        if new.ssid != nil || rec!.name.isEmpty { rec!.name = new.displayName }
        st.state.networks[new.key] = rec!; st.save()
        let name = rec!.name
        // Evil-twin heuristic: a network we know by name, now served by a different gateway.
        // Same name, different router. Compare against the most-visited network of that name, and only bother if we
        // actually knew it well: one previous sighting is not enough to call anything an impostor.
        var twinFired = false
        if let ssid = new.ssid, first,
           let twin = st.state.networks.values.filter({ $0.name == ssid && $0.key != new.key }).max(by: { $0.visits < $1.visits }),
           twin.visits >= 3 {
            twinFired = true
            emit(.warning, "Same name, different network: \(ssid)", "You have joined a \(ssid) \(twin.visits) times, but this one is served by different hardware. Could be a replaced router; could be an impostor using the name. Prefer a VPN until you are sure.", key: "twin-\(new.key)", sticky: true, minGap: 600)
        }
        if let px = Collect.proxy() {
            let open = new.isWiFi && new.securityLevel < 3
            emit(open ? .warning : .notice, "A proxy is configured here", "\(px). Your web traffic passes through it. Normal on corporate networks; on public Wi-Fi, prefer a VPN.", key: "proxy-\(new.key)", sticky: open, minGap: 600)
        }
        if rec!.vpnSeen && !vpn {
            DispatchQueue.main.asyncAfter(deadline: .now() + 60) { [weak self] in
                guard let s = self, s.net.key == new.key, !(s.vpn ?? false) else { return }
                s.emit(.notice, "You usually use a VPN here", "\(name) is a network where your VPN was on before. It isn't now.", key: "vpn-expected-\(new.key)", minGap: 3600)
            }
        }
        let visible = new.isWiFi && new.securityLevel < 3 ? " Your Mac is visible here as \u{201C}\(Collect.computerName())\u{201D}." : ""
        if st.state.tlsCheck && (first || new.securityLevel < 3) {
            q.asyncAfter(deadline: .now() + 8) { [weak self] in
                guard let s = self, s.net.key == new.key else { return }
                let t = Collect.tlsProbe()
                if t.captive { s.emit(.notice, "Sign-in page or interception", "HTTPS to apple.com didn't verify on \(name). If this network shows a sign-in page you haven't completed, that's why. If not, something is intercepting connections.", key: "tls-\(new.key)", minGap: 600) }
                else if !t.ok { s.emit(.warning, "HTTPS is being intercepted", "Certificates on \(name) are issued by \u{201C}\(t.issuer)\u{201D}, not the real site. Whoever runs that can read your encrypted traffic. Expected only on a managed corporate network.", key: "tls-\(new.key)", sticky: true, minGap: 600) }
            }
        }
        // The generic "new network" card would only restate, and soften, a warning we just gave.
        if twinFired && new.securityLevel == 3 { net = new; return }
        switch (new.isWiFi ? new.securityLevel : 3) {
        case 1: emit(.warning, "Open Wi-Fi: \(name)", (first ? "No encryption. Anyone nearby can read unencrypted traffic. Use a VPN here." : "No encryption on this network. Use a VPN here.") + visible, key: "join-\(new.key)", sticky: true, minGap: 120)
        case 2: emit(.warning, "Weak Wi-Fi security: \(name)", "\(new.securityName). Treat it like an open network; use a VPN." + visible, key: "join-\(new.key)", sticky: true, minGap: 120)
        default:
            if first { emit(.notice, "New network: \(name)", "\(new.isWiFi ? new.securityName : "Wired"), first time here." + visible, key: "join-\(new.key)", minGap: 120) }
            else if rec!.isHome { NSLog("home network %@", name) }
            else { emit(.info, name, "\(new.isWiFi ? new.securityName : "Wired"), seen \(rec!.visits) times.", key: "join-\(new.key)", minGap: 120) }
        }
        if old.online, let old = st.state.networks[old.key], old.vpnSeen, !vpn {
            NSLog("left a network where VPN was used")
        }
    }

    func mediumTick(first: Bool = false) {
        let ls = Collect.listeners().filter { $0.exposed && !Collect.systemListeners.contains($0.process) }
        let st = Store.shared
        for l in ls {
            let id = "\(l.process):\(l.port)"
            if st.state.seenListeners.contains(id) { continue }
            st.state.seenListeners.append(id); st.save()
            if first { continue }                                     // launch = learn what's already there, silently; the board shows it
            let risky = net.isWiFi && net.securityLevel < 3 && !(vpn ?? false)
            emit(risky ? .warning : .notice, "\(l.process) is reachable from this network", "It started listening on port \(l.port) on all interfaces\(risky ? ", and this network is unencrypted" : ""). Fine for a server you meant to share; bind it to localhost otherwise.", key: "listen-\(l.process)", sticky: risky, minGap: 3600)
        }
        let live = Set(ls.map { "\($0.process):\($0.port)" })
        st.state.seenListeners = st.state.seenListeners.filter { live.contains($0) }   // forget closed ones so a re-open is announced again
        // sharing services switching on
        let sharing = Collect.sharingOn()
        if !first { for sname in sharing where !st.state.sharingSeen.contains(sname) {
            let risky = net.isWiFi && (net.securityLevel < 3 || !(st.state.networks[net.key]?.isHome ?? false))
            emit(risky ? .warning : .notice, "\(sname) is on", "Other devices on \(net.displayName) can now try to connect to your Mac. Turn it off in System Settings › General › Sharing when you're done.", key: "sharing-\(sname)", sticky: risky, minGap: 3600)
        } }
        st.state.sharingSeen = sharing; st.save()
    }

    /// Persistence, hosts file, custom roots: things that change rarely and matter a lot.
    func integrityTick(first: Bool) {
        let st = Store.shared
        let items = Collect.persistenceItems()
        if !first && !st.state.persistenceItems.isEmpty {
            for it in items where !st.state.persistenceItems.contains(it) {
                emit(.notice, "New background item", "\(it) will run automatically from now on. Expected if you just installed or updated something.", key: "persist-\(it)", minGap: 86400)
            }
        }
        st.state.persistenceItems = items
        let h = Collect.hostsHash()
        if !st.state.hostsHash.isEmpty && h != st.state.hostsHash { emit(.notice, "/etc/hosts was changed", "The file that overrides domain lookups changed. Usually a dev tool or VPN client; worth a look if you didn't expect it.", key: "hosts", minGap: 3600) }
        st.state.hostsHash = h
        let watched: [(String, String)] = [("~/.ssh/authorized_keys", "SSH authorized keys"), ("~/.zshrc", "Shell startup (.zshrc)"), ("~/.zprofile", "Shell startup (.zprofile)"), ("~/.bashrc", "Shell startup (.bashrc)"), ("~/.bash_profile", "Shell startup (.bash_profile)"), ("~/.ssh/config", "SSH config")]
        for (path, label) in watched {
            let h = Collect.fileHash(path)
            if let old = st.state.fileHashes[path], old != h, !first {
                let msg = path.contains("authorized_keys") ? "Someone can now log into this Mac over SSH with a new key, if Remote Login is on." : "Startup files can run commands every time you open a terminal. Expected if you edited it or installed a tool."
                emit(path.contains("authorized_keys") ? .warning : .notice, "\(label) changed", msg, key: "file-\(path)", sticky: path.contains("authorized_keys"), minGap: 86400)
            }
            st.state.fileHashes[path] = h
        }
        let cron = Collect.cronHash()
        if let old = st.state.fileHashes["cron"], old != cron, !first { emit(.notice, "Your scheduled jobs changed", "The user crontab was modified. Expected if you set up a task; otherwise check it with crontab -l.", key: "cron", minGap: 86400) }
        st.state.fileHashes["cron"] = cron
        let exts = Collect.systemExtensions()
        if !first { for e in exts where !st.state.sysExtensions.contains(e) { emit(.notice, "New system extension", "\(e) is now active. VPNs, security tools and virtual cameras install these; malware would love to.", key: "sysext-\(e)", minGap: 86400) } }
        st.state.sysExtensions = exts
        let roots = Collect.customRoots()
        if st.state.customRoots >= 0 && roots > st.state.customRoots { emit(.warning, "New trusted root certificate", "\(roots) custom root\(roots == 1 ? "" : "s") now trusted. Its owner can inspect your encrypted traffic. Expected for a corporate profile or a debugging proxy you installed; otherwise remove it in Keychain Access.", key: "roots-\(roots)", sticky: true, minGap: 3600) }
        st.state.customRoots = roots
        st.save()
    }

    func appLaunched(name: String, bundleID: String, path: String) {
        let st = Store.shared
        guard !st.state.assessedApps.contains(bundleID), !path.hasPrefix("/System/"), !path.hasPrefix("/usr/"), bundleID != "app.argus.mac" else { return }
        st.state.assessedApps.append(bundleID); st.save()
        if !Collect.notarized(path) {
            emit(.notice, "\(name) isn't notarized", "Apple hasn't checked this app for known malware. Fine for tools you built or trust; think twice for downloads.", key: "notary-\(bundleID)", minGap: 86400 * 30)
        }
    }

    func slowTick() {
        let st = Store.shared
        guard net.online, var rec = st.state.networks[net.key], rec.isHome else { return }
        let devices = Collect.lanDevices(net: net)
        for (ip, mac) in devices {
            if var d = rec.devices[mac] { d.lastSeen = Date(); d.ip = ip; rec.devices[mac] = d; continue }
            let vendor = Vendors.shared.lookup(mac)
            rec.devices[mac] = DeviceRecord(mac: mac, ip: ip, vendor: vendor, firstSeen: Date(), lastSeen: Date())
            if rec.devices.count > 1 || rec.visits > 1 {   // first sweep on a fresh home just learns
                emit(.notice, "New device on \(rec.name)", "\(vendor) at \(ip).", key: "dev-\(mac)", minGap: 86400)
            }
        }
        st.state.networks[net.key] = rec; st.save()
    }

    func toggleHome() -> Bool {
        let st = Store.shared
        guard var rec = st.state.networks[net.key] else { return false }
        rec.isHome.toggle()
        if rec.isHome { for (ip, mac) in Collect.lanDevices(net: net) where rec.devices[mac] == nil { rec.devices[mac] = DeviceRecord(mac: mac, ip: ip, vendor: Vendors.shared.lookup(mac), firstSeen: Date(), lastSeen: Date()) } }
        st.state.networks[net.key] = rec; st.save(); return rec.isHome
    }
}
