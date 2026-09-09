import Foundation

/// Run a command and return stdout (stderr merged). Everything the app knows comes from public macOS tools.
@discardableResult
func sh(_ cmd: String, _ args: [String], timeout: TimeInterval = 8) -> String {
    let p = Process(); p.executableURL = URL(fileURLWithPath: cmd); p.arguments = args
    let out = Pipe(); p.standardOutput = out; p.standardError = out
    do { try p.run() } catch { return "" }
    let deadline = DispatchTime.now() + timeout
    let group = DispatchGroup(); group.enter()
    DispatchQueue.global().async { p.waitUntilExit(); group.leave() }
    if group.wait(timeout: deadline) == .timedOut { p.terminate() }
    return String(data: out.fileHandleForReading.readDataToEndOfFile(), encoding: .utf8) ?? ""
}

/// TCP connect probe on localhost: tells whether a service is listening on a port even if it belongs to root.
func portOpen(_ port: Int, host: String = "127.0.0.1", timeoutMs: Int = 300) -> Bool {
    let s = socket(AF_INET, SOCK_STREAM, 0); if s < 0 { return false }
    defer { close(s) }
    var tv = timeval(tv_sec: 0, tv_usec: Int32(timeoutMs * 1000))
    setsockopt(s, SOL_SOCKET, SO_SNDTIMEO, &tv, socklen_t(MemoryLayout<timeval>.size))
    var addr = sockaddr_in(); addr.sin_family = sa_family_t(AF_INET); addr.sin_port = in_port_t(port).bigEndian
    inet_pton(AF_INET, host, &addr.sin_addr)
    let r = withUnsafePointer(to: &addr) { $0.withMemoryRebound(to: sockaddr.self, capacity: 1) { connect(s, $0, socklen_t(MemoryLayout<sockaddr_in>.size)) } }
    return r == 0
}

/// Nudge every host in a /24 with one UDP packet so the ARP table fills in. Cheap, local, no reply needed.
func arpSweep(prefix: String) {
    let s = socket(AF_INET, SOCK_DGRAM, 0); if s < 0 { return }
    defer { close(s) }
    for i in 1...254 {
        var addr = sockaddr_in(); addr.sin_family = sa_family_t(AF_INET); addr.sin_port = in_port_t(9).bigEndian
        inet_pton(AF_INET, "\(prefix).\(i)", &addr.sin_addr)
        var byte: UInt8 = 0
        _ = withUnsafePointer(to: &addr) { $0.withMemoryRebound(to: sockaddr.self, capacity: 1) { sendto(s, &byte, 1, 0, $0, socklen_t(MemoryLayout<sockaddr_in>.size)) } }
    }
}
