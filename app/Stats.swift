import Foundation
import Darwin
import CoreWLAN

/// Live machine stats for the always-on strip. Every number here comes from a Mach or BSD call, not from spawning a
/// tool, which is what makes a one-second refresh affordable.
struct Stats {
    var cpu: Double = 0            // 0...1 across all cores
    var memUsed: Double = 0        // 0...1 of physical memory
    var memGB: Double = 0
    var down: Double = 0           // bytes per second
    var up: Double = 0
    var rssi: Int = 0              // dBm, 0 when not on Wi-Fi
    var txRate: Double = 0         // Mbps
    var wifi = false
}

final class StatsReader {
    private var lastCPU: (user: UInt64, sys: UInt64, idle: UInt64, nice: UInt64)?
    private var lastNet: (rx: UInt64, tx: UInt64, at: Date)?

    func read(interface: String) -> Stats {
        var s = Stats()
        s.cpu = cpuBusy()
        let m = memory(); s.memUsed = m.0; s.memGB = m.1
        let n = throughput(interface: interface); s.down = n.0; s.up = n.1
        if let w = CWWiFiClient.shared().interface(withName: interface), w.powerOn(), w.ssid() != nil || w.rssiValue() != 0 {
            s.wifi = true; s.rssi = w.rssiValue(); s.txRate = w.transmitRate()
        }
        return s
    }

    /// Fraction of CPU time that was not idle since the previous sample.
    private func cpuBusy() -> Double {
        var count = mach_msg_type_number_t(MemoryLayout<host_cpu_load_info_data_t>.size / MemoryLayout<integer_t>.size)
        var info = host_cpu_load_info()
        let r = withUnsafeMutablePointer(to: &info) {
            $0.withMemoryRebound(to: integer_t.self, capacity: Int(count)) {
                host_statistics(mach_host_self(), HOST_CPU_LOAD_INFO, $0, &count)
            }
        }
        guard r == KERN_SUCCESS else { return 0 }
        let u = UInt64(info.cpu_ticks.0), sy = UInt64(info.cpu_ticks.1), i = UInt64(info.cpu_ticks.2), ni = UInt64(info.cpu_ticks.3)
        defer { lastCPU = (u, sy, i, ni) }
        guard let p = lastCPU else { return 0 }
        let busy = Double((u &- p.user) &+ (sy &- p.sys) &+ (ni &- p.nice))
        let total = busy + Double(i &- p.idle)
        return total > 0 ? min(1, busy / total) : 0
    }

    /// App-visible memory pressure: what is resident and not reclaimable, over physical RAM.
    private func memory() -> (Double, Double) {
        var count = mach_msg_type_number_t(MemoryLayout<vm_statistics64_data_t>.size / MemoryLayout<integer_t>.size)
        var vm = vm_statistics64_data_t()
        let r = withUnsafeMutablePointer(to: &vm) {
            $0.withMemoryRebound(to: integer_t.self, capacity: Int(count)) {
                host_statistics64(mach_host_self(), HOST_VM_INFO64, $0, &count)
            }
        }
        let total = Double(ProcessInfo.processInfo.physicalMemory)
        guard r == KERN_SUCCESS, total > 0 else { return (0, 0) }
        let page = Double(vm_kernel_page_size)
        let used = (Double(vm.active_count) + Double(vm.wire_count) + Double(vm.compressor_page_count)) * page
        return (min(1, used / total), used / 1_073_741_824)
    }

    /// Bytes per second on the active interface, from the kernel's own counters.
    private func throughput(interface: String) -> (Double, Double) {
        var head: UnsafeMutablePointer<ifaddrs>?
        guard getifaddrs(&head) == 0, let start = head else { return (0, 0) }
        defer { freeifaddrs(head) }
        var rx: UInt64 = 0, tx: UInt64 = 0
        var p: UnsafeMutablePointer<ifaddrs>? = start
        while let cur = p {
            let name = String(cString: cur.pointee.ifa_name)
            if name == interface, cur.pointee.ifa_addr?.pointee.sa_family == UInt8(AF_LINK),
               let d = cur.pointee.ifa_data?.assumingMemoryBound(to: if_data.self) {
                rx = UInt64(d.pointee.ifi_ibytes); tx = UInt64(d.pointee.ifi_obytes)
            }
            p = cur.pointee.ifa_next
        }
        let now = Date()
        defer { lastNet = (rx, tx, now) }
        guard let last = lastNet else { return (0, 0) }
        let dt = now.timeIntervalSince(last.at)
        guard dt > 0.05, rx >= last.rx, tx >= last.tx else { return (0, 0) }   // counters reset on interface change
        return (Double(rx - last.rx) / dt, Double(tx - last.tx) / dt)
    }

    /// Deliberately terse: this sits in a 26pt strip, so "1.2M" beats "1.2 MB/s".
    static func rate(_ bps: Double) -> String {
        if bps >= 10_485_760 { return String(format: "%.0fM", bps / 1_048_576) }
        if bps >= 1_048_576 { return String(format: "%.1fM", bps / 1_048_576) }
        if bps >= 1024 { return String(format: "%.0fK", bps / 1024) }
        return "—"
    }
    /// RSSI to four bars. -50 and up is excellent, -80 and below is unusable.
    static func bars(_ rssi: Int) -> Int {
        if rssi == 0 { return 0 }
        if rssi >= -55 { return 4 }; if rssi >= -65 { return 3 }; if rssi >= -75 { return 2 }; return 1
    }
}
