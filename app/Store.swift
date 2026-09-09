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
}

final class Store {
    static let shared = Store()
    var state = State()
    let url: URL
    init() {
        let dir = FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask)[0].appendingPathComponent("Ledge")
        try? FileManager.default.createDirectory(at: dir, withIntermediateDirectories: true)
        url = dir.appendingPathComponent("state.json")
        if let d = try? Data(contentsOf: url), let s = try? JSONDecoder().decode(State.self, from: d) { state = s }
    }
    func save() { if let d = try? JSONEncoder().encode(state) { try? d.write(to: url) } }
}

/// MAC prefix -> vendor, from the bundled IEEE OUI list.
final class Vendors {
    static let shared = Vendors()
    var table: [String: String] = [:]
    init() {
        if let u = Bundle.main.url(forResource: "oui", withExtension: "json"), let d = try? Data(contentsOf: u),
           let t = try? JSONDecoder().decode([String: String].self, from: d) { table = t }
    }
    func lookup(_ mac: String) -> String {
        let parts = mac.split(separator: ":").map { String(format: "%02X", Int($0, radix: 16) ?? 0) }
        guard parts.count == 6 else { return "Unknown device" }
        if let first = Int(parts[0], radix: 16), first & 0x02 != 0 { return "Phone or laptop (private address)" }   // locally administered = randomised
        return table[parts[0] + parts[1] + parts[2]] ?? "Unknown device"
    }
}
