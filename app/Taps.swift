import Foundation
import CoreGraphics
import AppKit

/// Event taps: the mechanism a program uses to see input events system-wide. A tap on key events means that process
/// can read every keystroke you type, in any app. Text expanders, clipboard managers and shortcut tools use this
/// legitimately; so does every keylogger. `CGGetEventTapList` is public and needs no entitlement, which is why Argus
/// can report it at all.
struct KeyTap: Equatable {
    let pid: Int
    let name: String
    let path: String
    let enabled: Bool
    let signer: String          // "Apple", a Developer ID team, or "unsigned"
    var id: String { "\(name)|\(signer)" }
    var appleSigned: Bool { signer == "Apple" }
}

enum Taps {
    private static let keyMask: UInt64 =
        (1 << CGEventType.keyDown.rawValue) | (1 << CGEventType.keyUp.rawValue) | (1 << CGEventType.flagsChanged.rawValue)

    /// Every process currently tapping key events, deduplicated. Apple's own (Siri, accessibility) are included but
    /// flagged, because reporting them as suspicious would be crying wolf.
    static func keyboardTaps() -> [KeyTap] {
        var count: UInt32 = 0
        CGGetEventTapList(0, nil, &count)
        guard count > 0 else { return [] }
        var list = [CGEventTapInformation](repeating: CGEventTapInformation(), count: Int(count))
        guard CGGetEventTapList(count, &list, &count) == .success else { return [] }
        var seen = Set<String>(), out: [KeyTap] = []
        for t in list where (t.eventsOfInterest & keyMask) != 0 {
            let pid = Int(t.tappingProcess)
            let app = NSRunningApplication(processIdentifier: pid_t(pid))
            let path = app?.bundleURL?.path ?? Collect.processPath(pid)
            let name = app?.localizedName ?? (path as NSString).lastPathComponent
            guard !name.isEmpty else { continue }
            let tap = KeyTap(pid: pid, name: name, path: path, enabled: t.enabled, signer: signer(path))
            if seen.insert(tap.id).inserted { out.append(tap) }
        }
        return out
    }

    /// Who signed it. Apple's own binaries live under /System or are signed by Apple's own authority.
    private static func signer(_ path: String) -> String {
        guard !path.isEmpty else { return "unsigned" }
        if path.hasPrefix("/System/") || path.hasPrefix("/usr/") { return "Apple" }
        let out = sh("/usr/bin/codesign", ["-dv", "--verbose=2", path], timeout: 8)
        if out.contains("Software Signing") || out.contains("Apple Mac OS Application Signing") { return "Apple" }
        if let a = Collect.firstMatch(out, #"Authority=Developer ID Application: (.+?)\n"#) {
            return a.trimmingCharacters(in: .whitespaces)
        }
        if out.contains("code object is not signed") { return "unsigned" }
        return "unknown signer"
    }
}
