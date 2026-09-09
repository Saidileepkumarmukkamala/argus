import Foundation
import CoreWLAN

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
        guard let s = servers.first else { return "no resolver" }
        let known: [String: String] = ["1.1.1.1": "Cloudflare", "1.0.0.1": "Cloudflare", "8.8.8.8": "Google", "8.8.4.4": "Google", "9.9.9.9": "Quad9", "149.112.112.112": "Quad9", "208.67.222.222": "OpenDNS", "94.140.14.14": "AdGuard"]
        if let k = known[s] { return "\(k) public resolver" }
        if s == net.gatewayIP { return "the router (\(s))" }
        if s.hasPrefix("10.") || s.hasPrefix("192.168.") || s.hasPrefix("172.") { return "a private resolver (\(s))" }
        if s.hasPrefix("100.") { return "the VPN's resolver" }
        return "an external resolver (\(s))"
    }

    struct Listener: Hashable { let process: String; let port: Int; let exposed: Bool }
    static let systemListeners: Set<String> = ["ControlCe", "rapportd", "sharingd", "AirPlayXP", "launchd", "identitys", "remoted", "Spotlight", "mDNSRespo", "Bluetooth", "AirPlayUI"]
    static func listeners() -> [Listener] {
        var out: [Listener] = []
        for line in sh("/usr/sbin/lsof", ["-nP", "-iTCP", "-sTCP:LISTEN"]).split(separator: "\n").dropFirst() {
            var cols = line.split(separator: " ", omittingEmptySubsequences: true).map(String.init)
            if cols.last == "(LISTEN)" { cols.removeLast() }                       // lsof appends the state in parentheses
            guard cols.count >= 9, let name = cols.last, let portStr = name.split(separator: ":").last, let port = Int(portStr) else { continue }
            let host = String(name.dropLast(portStr.count + 1))
            let exposed = host == "*" || host == "0.0.0.0" || host == "[::]"
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

    struct PostureRow { let label: String; let ok: Bool; let value: String; let hint: String }
    static func posture(net: NetInfo, vpn: Bool) -> [PostureRow] {
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
        let upd = Int(firstMatch(sh("/usr/bin/defaults", ["read", "/Library/Preferences/com.apple.SoftwareUpdate", "LastUpdatesAvailable"]), #"(\d+)"#) ?? "0") ?? 0
        rows.append(.init(label: "Software updates", ok: upd == 0, value: upd == 0 ? "Up to date" : "\(upd) pending", hint: "System Settings › General › Software Update"))
        let netOk = !net.isWiFi || net.securityLevel == 3 || vpn
        rows.append(.init(label: "This network", ok: netOk, value: net.isWiFi ? "\(net.displayName) · \(net.securityName)" : net.displayName, hint: vpn ? "VPN is on" : (netOk ? "Encrypted" : "Use a VPN here")))
        rows.append(.init(label: "VPN", ok: true, value: vpn ? "Connected" : "Not connected", hint: ""))
        return rows
    }
}

/// Watches the signals on timers and turns changes into a small number of plain-English alerts.
final class Monitor {
    var onAlert: ((Alert) -> Void)?
    var net = NetInfo(); var vpn: Bool? = nil; var dns: [String] = []; var locationAllowed = false
    private var started = false
    let q = DispatchQueue(label: "ledge.monitor", qos: .utility)

    func start() {
        guard !started else { return }; started = true
        schedule(5) { self.fastTick() }; schedule(20) { self.mediumTick() }; schedule(120) { self.slowTick() }
        q.async { self.fastTick(); self.mediumTick(first: true) }
    }
    private func schedule(_ every: Double, _ f: @escaping () -> Void) {
        let t = DispatchSource.makeTimerSource(queue: q); t.schedule(deadline: .now() + every, repeating: every); t.setEventHandler(handler: f); t.resume(); timers.append(t)
    }
    private var timers: [DispatchSourceTimer] = []

    func emit(_ level: Level, _ title: String, _ detail: String, key: String, sticky: Bool = false, minGap: TimeInterval = 600) {
        let st = Store.shared
        if let p = st.state.pausedUntil, p > Date() { return }
        if let last = st.state.lastAlert[key], Date().timeIntervalSince(last) < minGap { return }
        st.state.lastAlert[key] = Date(); st.save()
        let a = Alert(level: level, title: title, detail: detail, key: key, sticky: sticky)
        NSLog("alert [%@] %@ — %@", key, title, detail)
        DispatchQueue.main.async { self.onAlert?(a) }
    }

    func fastTick() {
        let now = Collect.network(locationAllowed: locationAllowed)
        let v = Collect.vpnActive()
        if now.key != net.key { networkChanged(from: net, to: now, vpn: v) }
        else if now.ssid != nil && net.ssid == nil { net.ssid = now.ssid; if var r = Store.shared.state.networks[now.key] { r.name = now.displayName; Store.shared.state.networks[now.key] = r; Store.shared.save() } }
        if let old = vpn, old != v {
            if v { emit(.notice, "VPN connected", "Traffic now goes through the tunnel.", key: "vpn-up", minGap: 60) }
            else { emit(.warning, "VPN dropped", "You're on \(now.displayName) directly now.", key: "vpn-down", sticky: true, minGap: 60) }
            if v, var r = Store.shared.state.networks[now.key] { r.vpnSeen = true; Store.shared.state.networks[now.key] = r; Store.shared.save() }
        }
        vpn = v
        let d = Collect.dnsServers()
        if !dns.isEmpty && d != dns && now.key == net.key && !d.isEmpty {
            emit(.notice, "DNS changed", "Lookups now go to \(Collect.dnsClass(d, net: now)).", key: "dns-\(d.first ?? "")", minGap: 900)
        }
        dns = d
        net = now
    }

    func networkChanged(from old: NetInfo, to new: NetInfo, vpn: Bool) {
        guard new.online else {
            if old.online { emit(.info, "Offline", "No default route.", key: "offline", minGap: 60) }
            return
        }
        let st = Store.shared
        var rec = st.state.networks[new.key]
        let first = rec == nil
        if rec == nil { rec = NetworkRecord(key: new.key, name: new.displayName, security: new.securityName, firstSeen: Date(), lastSeen: Date()) }
        rec!.lastSeen = Date(); rec!.visits += first ? 0 : 1; rec!.security = new.securityName
        if new.ssid != nil || rec!.name.isEmpty { rec!.name = new.displayName }
        st.state.networks[new.key] = rec!; st.save()
        let name = rec!.name
        switch (new.isWiFi ? new.securityLevel : 3) {
        case 1: emit(.warning, "Open Wi-Fi: \(name)", first ? "No encryption. Anyone nearby can read unencrypted traffic. Use a VPN here." : "No encryption on this network. Use a VPN here.", key: "join-\(new.key)", sticky: true, minGap: 120)
        case 2: emit(.warning, "Weak Wi-Fi security: \(name)", "\(new.securityName). Treat it like an open network; use a VPN.", key: "join-\(new.key)", sticky: true, minGap: 120)
        default:
            if first { emit(.notice, "New network: \(name)", "\(new.isWiFi ? new.securityName : "Wired"), first time here. Nothing to do.", key: "join-\(new.key)", minGap: 120) }
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
            if first && net.securityLevel == 3 && (st.state.networks[net.key]?.isHome ?? false) { continue }   // don't nag about known dev servers at home on launch
            let risky = net.isWiFi && net.securityLevel < 3 && !(vpn ?? false)
            emit(risky ? .warning : .notice, "\(l.process) is open to this network", "Listening on port \(l.port) on all interfaces\(risky ? ", on an unencrypted network" : ""). Bind it to localhost if that isn't intended.", key: "listen-\(id)", sticky: risky, minGap: 3600)
        }
        let live = Set(ls.map { "\($0.process):\($0.port)" })
        st.state.seenListeners = st.state.seenListeners.filter { live.contains($0) }   // forget closed ones so a re-open is announced again
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
