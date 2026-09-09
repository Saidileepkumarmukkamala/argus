// Ledge — a plain-English narrator for what changed about your network and your Mac's exposure, living in the notch.
// UI: a cockpit-dark body below the hardware notch, cyan scan sweep on open, glowing glyphs, countdown arc, cascading status board.
import AppKit
import CoreLocation
import ServiceManagement

final class NotchPanel: NSPanel { override var canBecomeKey: Bool { false } }

func notchPath(bodyWidth: CGFloat, depth: CGFloat, top: CGFloat, bottom: CGFloat, in size: CGSize) -> CGPath {
    let yT = size.height, yB = size.height - depth
    let x1 = ((size.width - bodyWidth) / 2).rounded(), x2 = x1 + bodyWidth
    let p = CGMutablePath()
    p.move(to: CGPoint(x: x1 - top, y: yT))
    p.addQuadCurve(to: CGPoint(x: x1, y: yT - top), control: CGPoint(x: x1, y: yT))
    p.addLine(to: CGPoint(x: x1, y: yB + bottom))
    p.addQuadCurve(to: CGPoint(x: x1 + bottom, y: yB), control: CGPoint(x: x1, y: yB))
    p.addLine(to: CGPoint(x: x2 - bottom, y: yB))
    p.addQuadCurve(to: CGPoint(x: x2, y: yB + bottom), control: CGPoint(x: x2, y: yB))
    p.addLine(to: CGPoint(x: x2, y: yT - top))
    p.addQuadCurve(to: CGPoint(x: x2 + top, y: yT), control: CGPoint(x: x2, y: yT))
    p.closeSubpath()
    return p
}

final class ClickView: NSView {
    var onClick: (() -> Void)?
    override func mouseDown(with e: NSEvent) { onClick?() }
    override func acceptsFirstMouse(for event: NSEvent?) -> Bool { true }
}

enum Theme {
    static let cyan = NSColor(red: 0.36, green: 0.86, blue: 1.0, alpha: 1)
    static let green = NSColor(red: 0.38, green: 0.92, blue: 0.62, alpha: 1)
    static let amber = NSColor(red: 1.0, green: 0.62, blue: 0.26, alpha: 1)
    static let body = NSColor(red: 0.024, green: 0.031, blue: 0.055, alpha: 1)
    static let text = NSColor(white: 0.96, alpha: 1)
    static let dim = NSColor(white: 0.66, alpha: 1)
    static let mono = NSFont.monospacedSystemFont(ofSize: 10, weight: .medium)
}

func label(_ text: String, size: CGFloat, weight: NSFont.Weight, color: NSColor, lines: Int = 1, mono: Bool = false) -> NSTextField {
    let l = NSTextField(labelWithString: text)
    l.font = mono ? NSFont.monospacedSystemFont(ofSize: size, weight: weight) : NSFont.systemFont(ofSize: size, weight: weight)
    l.textColor = color; l.maximumNumberOfLines = lines; l.lineBreakMode = lines == 1 ? .byTruncatingTail : .byWordWrapping; l.cell?.truncatesLastVisibleLine = true
    return l
}

final class App: NSObject, NSApplicationDelegate, CLLocationManagerDelegate {
    var panel: NotchPanel!
    let mask = CAShapeLayer()
    var view: ClickView!
    var notch = NSRect.zero
    let bodyW: CGFloat = 420, earOpen: CGFloat = 19, earClosed: CGFloat = 6, bottomOpen: CGFloat = 22, bottomClosed: CGFloat = 14
    var depth: CGFloat = 0
    var status: NSStatusItem!
    let monitor = Monitor()
    let loc = CLLocationManager()
    var hideTimer: Timer?
    var gen = 0
    // layers
    let tint = CAGradientLayer(), scanlines = CAReplicatorLayer(), sweep = CAGradientLayer(), edge = CAShapeLayer()
    let ring = CAShapeLayer(), pulse = CAShapeLayer()
    // widgets
    let glyph = NSImageView(); var title = label("", size: 13.5, weight: .semibold, color: Theme.text)
    var detail = label("", size: 11.5, weight: .regular, color: Theme.dim, lines: 2); var meta = label("", size: 10, weight: .medium, color: Theme.cyan, mono: true)
    var boardViews: [NSView] = []

    func applicationDidFinishLaunching(_ n: Notification) {
        NSApp.setActivationPolicy(.accessory)
        let screen = NSScreen.screens.first { $0.safeAreaInsets.top > 0 } ?? NSScreen.main!
        notch = notchRect(screen)
        panel = NotchPanel(contentRect: closedRect(), styleMask: [.borderless, .nonactivatingPanel], backing: .buffered, defer: false)
        panel.level = NSWindow.Level(rawValue: NSWindow.Level.statusBar.rawValue + 1)
        panel.collectionBehavior = [.canJoinAllSpaces, .stationary, .fullScreenAuxiliary, .ignoresCycle]
        panel.backgroundColor = .clear; panel.isOpaque = false; panel.hasShadow = false; panel.ignoresMouseEvents = false; panel.isMovable = false
        view = ClickView(frame: NSRect(origin: .zero, size: closedRect().size)); view.wantsLayer = true
        view.layer?.backgroundColor = NSColor.black.cgColor
        mask.path = closedPath(in: closedRect().size); view.layer?.mask = mask
        view.onClick = { [weak self] in self?.clicked() }
        buildLayers()
        for v in [glyph, title, detail, meta] { v.isHidden = true; view.addSubview(v) }
        panel.contentView = view; panel.orderFrontRegardless()

        status = NSStatusBar.system.statusItem(withLength: NSStatusItem.squareLength)
        status.button?.image = NSImage(systemSymbolName: "shield.lefthalf.filled", accessibilityDescription: "Ledge")
        rebuildMenu()
        loc.delegate = self
        monitor.locationAllowed = loc.authorizationStatus == .authorizedAlways || loc.authorizationStatus == .authorized
        monitor.onAlert = { [weak self] a in self?.show(a) }
        monitor.start()
        if ProcessInfo.processInfo.environment["LEDGE_DEMO"] != nil { demo() }
    }

    // MARK: layers (all positioned per open size in layout())
    func buildLayers() {
        guard let root = view.layer else { return }
        tint.colors = [Theme.body.cgColor, NSColor(red: 0.03, green: 0.05, blue: 0.09, alpha: 1).cgColor]; tint.startPoint = CGPoint(x: 0.5, y: 1); tint.endPoint = CGPoint(x: 0.5, y: 0)
        root.addSublayer(tint)
        let line = CALayer(); line.backgroundColor = NSColor(white: 1, alpha: 0.035).cgColor; line.frame = CGRect(x: 0, y: 0, width: 1000, height: 1)
        scanlines.addSublayer(line); scanlines.instanceCount = 200; scanlines.instanceTransform = CATransform3DMakeTranslation(0, 3, 0); root.addSublayer(scanlines)
        edge.fillColor = nil; edge.strokeColor = Theme.cyan.withAlphaComponent(0.35).cgColor; edge.lineWidth = 1; root.addSublayer(edge)
        sweep.colors = [Theme.cyan.withAlphaComponent(0).cgColor, Theme.cyan.withAlphaComponent(0.22).cgColor, Theme.cyan.withAlphaComponent(0).cgColor]
        sweep.startPoint = CGPoint(x: 0, y: 0.5); sweep.endPoint = CGPoint(x: 1, y: 0.5); sweep.opacity = 0; root.addSublayer(sweep)
        ring.fillColor = nil; ring.lineWidth = 2; ring.lineCap = .round; ring.strokeColor = Theme.cyan.cgColor; ring.isHidden = true; root.addSublayer(ring)
        pulse.fillColor = nil; pulse.lineWidth = 1.5; pulse.isHidden = true; root.addSublayer(pulse)
        glyph.wantsLayer = true; glyph.contentTintColor = Theme.cyan; glyph.imageScaling = .scaleProportionallyUpOrDown
        glyph.layer?.shadowColor = Theme.cyan.cgColor; glyph.layer?.shadowRadius = 8; glyph.layer?.shadowOpacity = 0.9; glyph.layer?.shadowOffset = .zero
    }
    func layout(size: CGSize, d: CGFloat) {
        CATransaction.begin(); CATransaction.setDisableActions(true)
        let x1 = (size.width - bodyW) / 2, bodyRect = CGRect(x: x1, y: 0, width: bodyW, height: d)     // below the hardware notch
        tint.frame = bodyRect; scanlines.frame = bodyRect; sweep.frame = CGRect(x: x1 - 80, y: 0, width: 80, height: d)
        let p = CGMutablePath(); p.move(to: CGPoint(x: x1 + 26, y: d + 0.5)); p.addLine(to: CGPoint(x: x1 + bodyW - 26, y: d + 0.5)); edge.path = p   // hairline where body meets notch
        CATransaction.commit()
    }
    func runSweep(size: CGSize) {
        let a = CABasicAnimation(keyPath: "position.x"); a.fromValue = (size.width - bodyW) / 2 - 40; a.toValue = (size.width + bodyW) / 2 + 40; a.duration = 0.75
        a.timingFunction = CAMediaTimingFunction(name: .easeInEaseOut)
        let o = CAKeyframeAnimation(keyPath: "opacity"); o.values = [0, 1, 1, 0]; o.keyTimes = [0, 0.15, 0.85, 1]; o.duration = 0.75
        sweep.add(a, forKey: "x"); sweep.add(o, forKey: "o")
    }

    // MARK: geometry
    func notchRect(_ s: NSScreen) -> NSRect {
        let top = s.safeAreaInsets.top
        if top > 0, let l = s.auxiliaryTopLeftArea, let r = s.auxiliaryTopRightArea { return NSRect(x: l.maxX, y: s.frame.maxY - top, width: r.minX - l.maxX, height: top) }
        return NSRect(x: s.frame.midX - 92, y: s.frame.maxY - 32, width: 185, height: 32)
    }
    func closedRect() -> NSRect { NSRect(x: notch.minX - earClosed, y: notch.minY, width: notch.width + 2 * earClosed, height: notch.height) }
    func openSize(_ d: CGFloat) -> NSSize { NSSize(width: bodyW + 2 * earOpen, height: notch.height + d) }
    func openRect(_ d: CGFloat) -> NSRect { let s = openSize(d); return NSRect(x: notch.midX - s.width / 2, y: notch.maxY - s.height, width: s.width, height: s.height) }
    func openPath(_ d: CGFloat, in size: CGSize) -> CGPath { notchPath(bodyWidth: bodyW, depth: notch.height + d, top: earOpen, bottom: bottomOpen, in: size) }
    func closedPath(in size: CGSize) -> CGPath { notchPath(bodyWidth: notch.width, depth: notch.height, top: earClosed, bottom: bottomClosed, in: size) }

    func setDepth(_ d: CGFloat) {
        gen += 1; let g = gen
        let size = openSize(max(d, depth))
        if d > 0 {
            panel.setFrame(openRect(max(d, depth)), display: false); view.frame = NSRect(origin: .zero, size: size)
            if depth == 0 { mask.removeAllAnimations(); mask.path = closedPath(in: size) }
            layout(size: size, d: d)
        }
        let to = d > 0 ? openPath(d, in: size) : closedPath(in: size)
        let anim = CASpringAnimation(keyPath: "path"); anim.fromValue = mask.presentation()?.path ?? mask.path; anim.toValue = to
        anim.damping = 20; anim.stiffness = 300; anim.mass = 1; anim.duration = anim.settlingDuration
        mask.add(anim, forKey: "morph"); mask.path = to
        if d > 0 && depth == 0 { runSweep(size: size) }
        depth = d
        if d == 0 {
            DispatchQueue.main.asyncAfter(deadline: .now() + anim.settlingDuration) { [weak self] in
                guard let s = self, s.gen == g, s.depth == 0 else { return }
                s.panel.setFrame(s.closedRect(), display: false); s.view.frame = NSRect(origin: .zero, size: s.closedRect().size)
                s.mask.removeAllAnimations(); s.mask.path = s.closedPath(in: s.closedRect().size)
            }
        }
    }

    // MARK: alert card
    func tone(_ l: Level) -> NSColor { l == .warning ? Theme.amber : (l == .notice ? Theme.green : Theme.cyan) }
    func symbol(for a: Alert) -> String {
        let k = a.key
        if k.hasPrefix("join") { return a.level == .warning ? "wifi.exclamationmark" : "wifi" }
        if k.hasPrefix("vpn-down") { return "lock.open.trianglebadge.exclamationmark" }
        if k.hasPrefix("vpn") { return "lock.shield" }
        if k.hasPrefix("listen") { return "antenna.radiowaves.left.and.right" }
        if k.hasPrefix("dev") { return "dot.radiowaves.left.and.right" }
        if k.hasPrefix("dns") { return "arrow.triangle.branch" }
        if k.hasPrefix("home") { return "house" }
        return "shield.lefthalf.filled"
    }
    func metaLine() -> String {
        let n = monitor.net
        var parts: [String] = []
        if n.isWiFi { parts.append(n.securityName.uppercased()) } else if n.online { parts.append("WIRED") }
        if !n.iface.isEmpty { parts.append(n.iface) }
        if !n.gatewayIP.isEmpty { parts.append("GW " + n.gatewayIP) }
        if monitor.vpn == true { parts.append("VPN") }
        let f = DateFormatter(); f.dateFormat = "HH:mm:ss"; parts.append(f.string(from: Date()))
        return parts.joined(separator: "  ·  ")
    }
    func show(_ a: Alert) {
        if a.level == .info { return }
        clearBoard()
        let d: CGFloat = 78, c = tone(a.level)
        setDepth(d)
        let size = openSize(d), x0 = (size.width - bodyW) / 2
        glyph.image = NSImage(systemSymbolName: symbol(for: a), accessibilityDescription: nil)?.withSymbolConfiguration(.init(pointSize: 22, weight: .medium))
        glyph.contentTintColor = c; glyph.layer?.shadowColor = c.cgColor
        glyph.frame = NSRect(x: x0 + 20, y: d - 52, width: 30, height: 30)
        title.stringValue = a.title; title.frame = NSRect(x: x0 + 62, y: d - 30, width: bodyW - 120, height: 18)
        detail.stringValue = a.detail; detail.frame = NSRect(x: x0 + 62, y: d - 62, width: bodyW - 120, height: 30)
        meta.stringValue = metaLine(); meta.textColor = c.withAlphaComponent(0.85); meta.frame = NSRect(x: x0 + 62, y: 6, width: bodyW - 80, height: 13)
        for v in [glyph, title, detail, meta] { v.isHidden = false; v.alphaValue = 0 }
        NSAnimationContext.runAnimationGroup { ctx in ctx.duration = 0.35; for v in [glyph, title, detail, meta] { v.animator().alphaValue = 1 } }
        // countdown arc + warning pulse
        let dur: Double = a.sticky ? 45 : 10
        let center = CGPoint(x: x0 + bodyW - 26, y: d - 37)
        ring.path = CGPath(ellipseIn: CGRect(x: center.x - 9, y: center.y - 9, width: 18, height: 18), transform: nil)
        ring.strokeColor = c.withAlphaComponent(0.9).cgColor; ring.isHidden = false; ring.removeAllAnimations(); ring.strokeEnd = 0
        let drain = CABasicAnimation(keyPath: "strokeEnd"); drain.fromValue = 1; drain.toValue = 0; drain.duration = dur; drain.fillMode = .forwards; drain.isRemovedOnCompletion = false
        ring.add(drain, forKey: "drain")
        pulse.removeAllAnimations(); pulse.isHidden = a.level != .warning
        if a.level == .warning {
            pulse.path = CGPath(ellipseIn: CGRect(x: -16, y: -16, width: 32, height: 32), transform: nil); pulse.position = CGPoint(x: x0 + 35, y: d - 37); pulse.strokeColor = c.cgColor
            let s = CABasicAnimation(keyPath: "transform.scale"); s.fromValue = 0.6; s.toValue = 1.9; let o = CABasicAnimation(keyPath: "opacity"); o.fromValue = 0.9; o.toValue = 0
            let grp = CAAnimationGroup(); grp.animations = [s, o]; grp.duration = 1.4; grp.repeatCount = .infinity; pulse.add(grp, forKey: "pulse")
        }
        hideTimer?.invalidate(); hideTimer = Timer.scheduledTimer(withTimeInterval: dur, repeats: false) { [weak self] _ in self?.hide() }
    }
    func hide() {
        hideTimer?.invalidate(); ring.isHidden = true; pulse.isHidden = true
        NSAnimationContext.runAnimationGroup({ ctx in ctx.duration = 0.18; for v in [glyph, title, detail, meta] { v.animator().alphaValue = 0 }; boardViews.forEach { $0.animator().alphaValue = 0 } },
            completionHandler: { for v in [self.glyph, self.title, self.detail, self.meta] { v.isHidden = true }; self.clearBoard() })
        setDepth(0)
    }
    func clearBoard() { boardViews.forEach { $0.removeFromSuperview() }; boardViews = [] }

    // MARK: status board (click)
    func showBoard() {
        for v in [glyph, title, detail, meta] { v.isHidden = true }
        clearBoard(); ring.isHidden = true; pulse.isHidden = true
        let rows = Collect.posture(net: monitor.net, vpn: monitor.vpn ?? false)
        let rowH: CGFloat = 20, d = CGFloat(rows.count) * rowH + 48
        setDepth(d)
        let size = openSize(d), x0 = (size.width - bodyW) / 2
        let bad = rows.filter { !$0.ok }.count
        let head = label("SYSTEM STATUS", size: 10, weight: .semibold, color: Theme.cyan, mono: true); head.frame = NSRect(x: x0 + 20, y: d - 26, width: 200, height: 14)
        let sum = label(bad == 0 ? "ALL CLEAR" : "\(bad) NEEDS ATTENTION", size: 10, weight: .semibold, color: bad == 0 ? Theme.green : Theme.amber, mono: true); sum.frame = NSRect(x: x0 + bodyW - 220, y: d - 26, width: 200, height: 14); sum.alignment = .right
        var y = d - 40
        var all: [NSView] = [head, sum]
        for r in rows {
            let led = NSView(frame: NSRect(x: x0 + 22, y: y - 12, width: 7, height: 7)); led.wantsLayer = true; led.layer?.cornerRadius = 3.5
            let c = r.ok ? Theme.green : Theme.amber; led.layer?.backgroundColor = c.cgColor; led.layer?.shadowColor = c.cgColor; led.layer?.shadowRadius = 5; led.layer?.shadowOpacity = 0.9; led.layer?.shadowOffset = .zero
            let l = label(r.label, size: 12, weight: .medium, color: Theme.text); l.frame = NSRect(x: x0 + 40, y: y - 16, width: 170, height: 16)
            let v = label(r.value, size: 11, weight: .medium, color: r.ok ? Theme.dim : Theme.text, mono: true); v.frame = NSRect(x: x0 + 200, y: y - 16, width: bodyW - 220, height: 16); v.alignment = .right
            all += [led, l, v]; y -= rowH
        }
        let foot = label(metaLine(), size: 10, weight: .medium, color: Theme.cyan.withAlphaComponent(0.7), mono: true); foot.frame = NSRect(x: x0 + 40, y: 6, width: bodyW - 60, height: 13); all.append(foot)
        for (i, v) in all.enumerated() {
            view.addSubview(v); boardViews.append(v); v.alphaValue = 0
            let f = v.frame; v.frame = f.offsetBy(dx: -10, dy: 0)
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.12 + Double(i) * 0.022) { NSAnimationContext.runAnimationGroup { ctx in ctx.duration = 0.25; v.animator().alphaValue = 1; v.animator().frame = f } }
        }
        hideTimer?.invalidate(); hideTimer = Timer.scheduledTimer(withTimeInterval: 40, repeats: false) { [weak self] _ in self?.hide() }
    }
    func clicked() { if depth > 0 { hide() } else { showBoard() } }

    // MARK: menu
    func rebuildMenu() {
        let m = NSMenu()
        m.addItem(withTitle: "Show status", action: #selector(menuBoard), keyEquivalent: "")
        let home = Store.shared.state.networks[monitor.net.key]?.isHome ?? false
        m.addItem(withTitle: home ? "This network is Home ✓  (click to unmark)" : "Mark this network as Home", action: #selector(menuHome), keyEquivalent: "")
        if !monitor.locationAllowed { m.addItem(withTitle: "Show Wi-Fi names (needs Location)…", action: #selector(menuLocation), keyEquivalent: "") }
        let paused = (Store.shared.state.pausedUntil ?? .distantPast) > Date()
        m.addItem(withTitle: paused ? "Resume alerts" : "Pause alerts for 1 hour", action: #selector(menuPause), keyEquivalent: "")
        m.addItem(.separator())
        let login = NSMenuItem(title: "Launch at Login", action: #selector(toggleLogin(_:)), keyEquivalent: ""); login.state = SMAppService.mainApp.status == .enabled ? .on : .off; m.addItem(login)
        m.addItem(withTitle: "Quit Ledge", action: #selector(NSApplication.terminate(_:)), keyEquivalent: "q")
        status.menu = m
    }
    @objc func menuBoard() { if depth > 0 { hide() }; DispatchQueue.main.asyncAfter(deadline: .now() + (depth > 0 ? 0.4 : 0)) { self.showBoard() } }
    @objc func menuHome() { let on = monitor.toggleHome(); rebuildMenu(); show(Alert(level: .notice, title: on ? "Marked as Home" : "No longer Home", detail: on ? "New devices joining this network will be announced." : "Device alerts are off for this network.", key: "home", sticky: false)) }
    @objc func menuLocation() { loc.requestWhenInUseAuthorization() }
    @objc func menuPause() { let st = Store.shared; let paused = (st.state.pausedUntil ?? .distantPast) > Date(); st.state.pausedUntil = paused ? nil : Date().addingTimeInterval(3600); st.save(); rebuildMenu() }
    @objc func toggleLogin(_ item: NSMenuItem) {
        do { if SMAppService.mainApp.status == .enabled { try SMAppService.mainApp.unregister(); item.state = .off } else { try SMAppService.mainApp.register(); item.state = .on } }
        catch { NSLog("launch at login: %@", error.localizedDescription) }
    }
    func locationManagerDidChangeAuthorization(_ m: CLLocationManager) { monitor.locationAllowed = m.authorizationStatus == .authorizedAlways || m.authorizationStatus == .authorized; rebuildMenu() }

    func demo() {
        let samples: [Alert] = [
            Alert(level: .warning, title: "Open Wi-Fi: Airport Free WiFi", detail: "No encryption. Anyone nearby can read unencrypted traffic. Use a VPN here.", key: "join-demo", sticky: false),
            Alert(level: .warning, title: "VPN dropped", detail: "You're on Airport Free WiFi directly now.", key: "vpn-down", sticky: false),
            Alert(level: .notice, title: "node is open to this network", detail: "Listening on port 3000 on all interfaces. Bind it to localhost if that isn't intended.", key: "listen-demo", sticky: false),
            Alert(level: .notice, title: "New device on Home", detail: "Samsung at 10.0.0.55.", key: "dev-demo", sticky: false),
            Alert(level: .notice, title: "DNS changed", detail: "Lookups now go to the router (10.0.0.1).", key: "dns-demo", sticky: false),
        ]
        for (i, a) in samples.enumerated() { DispatchQueue.main.asyncAfter(deadline: .now() + 2 + Double(i) * 7) { self.show(a) } }
        DispatchQueue.main.asyncAfter(deadline: .now() + 2 + Double(samples.count) * 7) { self.showBoard() }
    }
}
