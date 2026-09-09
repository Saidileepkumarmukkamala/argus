import AppKit
if CommandLine.arguments.contains("--dump") {
    // Print what Argus believes, for auditing against the raw commands.
    let n = Collect.network(locationAllowed: false), v = Collect.vpnActive()
    print("network:", n); print("vpn:", v); print("dns:", Collect.dnsServers(), Collect.dnsClass(Collect.dnsServers(), net: n)); print("proxy:", Collect.proxy() ?? "none")
    Collect.localIPForExposure = n.localIP
    print("listeners:", Collect.listeners().filter { $0.exposed }.map { "\($0.process):\($0.port)" }); print("sharing:", Collect.sharingOn())
    print("persistence:", Collect.persistenceItems().count, "items"); print("sysext:", Collect.systemExtensions()); print("roots:", Collect.customRoots(), "profiles:", Collect.profilesCount(), "mdm:", Collect.mdm())
    var t0 = Date(); let rows = Collect.posture(net: n, vpn: v); let cold = Date().timeIntervalSince(t0)
    t0 = Date(); _ = Collect.posture(net: n, vpn: v); let warm = Date().timeIntervalSince(t0)
    for r in rows { print(r.ok ? "  ok " : "  !! ", r.label.padding(toLength: 28, withPad: " ", startingAt: 0), r.value) }
    print(String(format: "\nposture scan: cold %.2f s, warm %.2f s (%d rows)", cold, warm, rows.count))
    exit(0)
}
if CommandLine.arguments.contains("--selftest") {
    // Drive the alert engine with synthetic transitions so the risky paths can be checked without needing a hostile
    // network: VPN drop, gateway impersonation, evil twin, weak security, proxy, DNS change, offline.
    let mon = Monitor()
    var fired: [(String, String, String)] = []
    mon.onAlert = { a in fired.append((a.level == .warning ? "WARN" : (a.level == .notice ? "note" : "info"), a.title, a.detail)) }
    func net(_ gwMAC: String, _ gwIP: String = "10.0.0.1", ssid: String? = nil, sec: Int = 3, secName: String = "WPA3", iface: String = "en0", local: String = "10.0.0.82", wifi: Bool = true) -> NetInfo {
        var n = NetInfo(); n.iface = iface; n.gatewayIP = gwIP; n.gatewayMAC = gwMAC; n.localIP = local
        n.ssid = ssid; n.isWiFi = wifi; n.securityName = secName; n.securityLevel = sec; return n
    }
    func run(_ label: String, _ body: () -> Void) {
        fired.removeAll(); Store.shared.state.lastAlert.removeAll()
        body()
        RunLoop.main.run(until: Date().addingTimeInterval(0.15))
        print("\n▸ \(label)")
        if fired.isEmpty { print("   (silent)") }
        for f in fired { print("   [\(f.0)] \(f.1)\n         \(f.2)") }
    }
    let home = net("aa:bb:cc:00:00:01", ssid: "Home")
    run("join a known-good home network for the first time") { mon.networkChanged(from: NetInfo(), to: home, vpn: false) }
    run("join an OPEN network") { mon.net = NetInfo(); mon.networkChanged(from: NetInfo(), to: net("de:ad:be:ef:00:01", "172.16.0.1", ssid: "Airport Free WiFi", sec: 1, secName: "Open"), vpn: false) }
    run("join a WEP/WPA1 network") { mon.net = NetInfo(); mon.networkChanged(from: NetInfo(), to: net("de:ad:be:ef:00:02", "192.168.1.1", ssid: "Hotel", sec: 2, secName: "WPA / WEP (weak)"), vpn: false) }
    run("gateway hardware changes underneath us (ARP spoofing shape)") {
        mon.net = home
        mon.networkChanged(from: home, to: net("99:99:99:99:99:99", ssid: "Home"), vpn: false)
    }
    run("a second network calling itself Home, different router (evil twin shape)") {
        Store.shared.state.networks[home.key] = NetworkRecord(key: home.key, name: "Home", security: "WPA3", firstSeen: Date(), lastSeen: Date(), isHome: true, visits: 40)
        mon.net = NetInfo()
        mon.networkChanged(from: NetInfo(), to: net("13:37:13:37:13:37", "10.5.0.1", ssid: "Home", local: "10.5.0.9"), vpn: false)
    }
    run("go offline") { mon.net = home; mon.networkChanged(from: home, to: NetInfo(), vpn: false) }
    print("\nNote: VPN up/down and DNS changes are driven by fastTick() against the live system, not synthesised here.")
    exit(0)
}
let app = NSApplication.shared
let delegate = App()
app.delegate = delegate
app.run()
