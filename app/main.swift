import AppKit
if CommandLine.arguments.contains("--dump") {
    // Print what Ledge believes, for auditing against the raw commands.
    let n = Collect.network(locationAllowed: false), v = Collect.vpnActive()
    print("network:", n); print("vpn:", v); print("dns:", Collect.dnsServers(), Collect.dnsClass(Collect.dnsServers(), net: n)); print("proxy:", Collect.proxy() ?? "none")
    Collect.localIPForExposure = n.localIP
    print("listeners:", Collect.listeners().filter { $0.exposed }.map { "\($0.process):\($0.port)" }); print("sharing:", Collect.sharingOn())
    print("persistence:", Collect.persistenceItems().count, "items"); print("sysext:", Collect.systemExtensions()); print("roots:", Collect.customRoots(), "profiles:", Collect.profilesCount(), "mdm:", Collect.mdm())
    for r in Collect.posture(net: n, vpn: v) { print(r.ok ? "  ok " : "  !! ", r.label.padding(toLength: 28, withPad: " ", startingAt: 0), r.value) }
    exit(0)
}
let app = NSApplication.shared
let delegate = App()
app.delegate = delegate
app.run()
