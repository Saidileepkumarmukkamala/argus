import Foundation

struct DeviceRecord: Codable { var mac: String; var ip: String; var vendor: String; var firstSeen: Date; var lastSeen: Date }
struct NetworkRecord: Codable {
    var key: String; var name: String; var security: String; var firstSeen: Date; var lastSeen: Date
    var isHome: Bool = false; var visits: Int = 1; var devices: [String: DeviceRecord] = [:]; var vpnSeen: Bool = false
}
struct State: Codable {
    var networks: [String: NetworkRecord] = [:]
    var seenListeners: [String] = []          // "process:port" already announced
    var lastAlert: [String: Date] = [:]        // rate limiting by alert key
    var pausedUntil: Date? = nil
    var persistenceItems: [String] = []     // launch agents/daemons + login items already known
    var hostsHash: String = ""
    var customRoots: Int = -1
    var sharingSeen: [String] = []
    var assessedApps: [String] = []          // bundle ids already checked for notarization
    var events: [EventRecord] = []           // last 40 alerts shown
    var tlsCheck: Bool = false               // optional: verify HTTPS to apple.com on new networks (the only connection Argus ever makes)
    var fileHashes: [String: String] = [:]   // authorized_keys, crontab, shell rc
    var sysExtensions: [String] = []
    var sessions: [String] = []              // remote logins already announced
    var keyTaps: [String] = []               // processes already known to read keystrokes
    var alwaysOn: Bool = false               // keep the live stats strip under the notch
}
struct EventRecord: Codable { var time: Date; var title: String; var detail: String; var level: String }

final class Store {
    static let shared = Store()
    var state = State()
    let url: URL
    init() {
        let base = FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask).first
            ?? URL(fileURLWithPath: NSHomeDirectory() + "/Library/Application Support")
        let dir = base.appendingPathComponent("Argus")
        try? FileManager.default.createDirectory(at: dir, withIntermediateDirectories: true)
        url = dir.appendingPathComponent("state.json")
        if let d = try? Data(contentsOf: url), let s = try? JSONDecoder().decode(State.self, from: d) { state = s }
    }
    func save() { if let d = try? JSONEncoder().encode(state) { try? d.write(to: url) } }
}

/// MAC prefix -> vendor, from the bundled IEEE OUI list. Forty thousand entries are only needed the first time an
/// unrecognised device turns up on a home network, so the table is loaded on demand rather than at launch.
final class Vendors {
    static let shared = Vendors()
    private var loaded: [String: String]?
    private let lock = NSLock()
    private var table: [String: String] {
        lock.lock(); defer { lock.unlock() }
        if let t = loaded { return t }
        var t: [String: String] = [:]
        if let u = Bundle.main.url(forResource: "oui", withExtension: "json"), let d = try? Data(contentsOf: u),
           let parsed = try? JSONDecoder().decode([String: String].self, from: d) { t = parsed }
        loaded = t
        return t
    }
    func lookup(_ mac: String) -> String {
        let parts = mac.split(separator: ":").map { String(format: "%02X", Int($0, radix: 16) ?? 0) }
        guard parts.count == 6 else { return "Unknown device" }
        if let first = Int(parts[0], radix: 16), first & 0x02 != 0 { return "Phone or laptop (private address)" }   // locally administered = randomised
        return table[parts[0..<3].joined()] ?? "Unknown device"
    }
}
