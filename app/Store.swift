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
    let url: URL
    /// The whole state is reachable from two threads: the monitor's background queue writes it constantly and the menu,
    /// the board and the menu bar icon read it on the main thread. Swift arrays and dictionaries mutated concurrently
    /// corrupt or crash, so every access goes through this lock. Reads hand back a copy, so a caller can never be
    /// holding a half-written structure.
    private var _state = State()
    private let lock = NSRecursiveLock()
    var state: State {
        get { lock.lock(); defer { lock.unlock() }; return _state }
        set { lock.lock(); _state = newValue; lock.unlock() }
    }
    /// Read-modify-write in one critical section, for the places that would otherwise lose a concurrent update.
    func mutate(_ body: (inout State) -> Void) {
        lock.lock(); body(&_state); lock.unlock()
    }

    init() {
        let base = FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask).first
            ?? URL(fileURLWithPath: NSHomeDirectory() + "/Library/Application Support")
        let dir = base.appendingPathComponent("Argus")
        try? FileManager.default.createDirectory(at: dir, withIntermediateDirectories: true)
        url = dir.appendingPathComponent("state.json")
        guard let d = try? Data(contentsOf: url) else { return }
        if let s = try? JSONDecoder().decode(State.self, from: d) { _state = s }
        else {
            // Keep the damaged file rather than silently starting from nothing: losing the baseline means every known
            // background item and listener would be announced as new.
            let bad = url.appendingPathExtension("corrupt")
            try? FileManager.default.removeItem(at: bad)
            try? FileManager.default.moveItem(at: url, to: bad)
            NSLog("Argus: state.json was unreadable, kept it as state.json.corrupt and started fresh")
        }
    }

    /// Atomic, and pruned so the file cannot grow without bound over months of use.
    func save() {
        lock.lock()
        prune(&_state)
        let data = try? JSONEncoder().encode(_state)
        lock.unlock()
        guard let data else { return }
        try? data.write(to: url, options: .atomic)
    }

    private func prune(_ s: inout State) {
        let now = Date()
        // Rate-limit stamps are only useful while their quiet period could still be running.
        s.lastAlert = s.lastAlert.filter { now.timeIntervalSince($0.value) < 60 * 86400 }
        // Networks you have not seen in half a year are not networks you are on.
        if s.networks.count > 200 {
            s.networks = Dictionary(uniqueKeysWithValues:
                s.networks.sorted { $0.value.lastSeen > $1.value.lastSeen }.prefix(200).map { ($0.key, $0.value) })
        }
        for (k, var n) in s.networks where n.devices.count > 300 {
            n.devices = Dictionary(uniqueKeysWithValues:
                n.devices.sorted { $0.value.lastSeen > $1.value.lastSeen }.prefix(300).map { ($0.key, $0.value) })
            s.networks[k] = n
        }
        if s.assessedApps.count > 500 { s.assessedApps.removeFirst(s.assessedApps.count - 500) }
        if s.events.count > 40 { s.events.removeFirst(s.events.count - 40) }
    }
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
