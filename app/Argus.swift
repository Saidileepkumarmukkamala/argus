// Argus — a plain-English narrator for what changed about your network and your Mac's exposure, living in the notch.
// UI: a cockpit-dark body below the hardware notch, cyan scan sweep on open, glowing glyphs, countdown arc, cascading status board.
import AppKit
import CoreLocation
import ServiceManagement

final class NotchPanel: NSPanel { override var canBecomeKey: Bool { false } }

/// The notch silhouette. Two different curve families, because the corners are doing opposite jobs:
/// the top "ears" are concave fillets that should sweep gently into the menu bar (superellipse exponent < 2),
/// the bottom corners are convex and get Apple's squircle continuity (exponent > 2). Every corner is sampled with the
/// same number of segments, so the open and closed paths tween cleanly under a spring animation.
func notchPath(bodyWidth: CGFloat, depth: CGFloat, top: CGFloat, bottom: CGFloat, in size: CGSize) -> CGPath {
    let yT = size.height, yB = size.height - depth
    let x1 = ((size.width - bodyWidth) / 2).rounded(), x2 = x1 + bodyWidth
    let p = CGMutablePath()
    let steps = 28, nEar: CGFloat = 1.5, nBottom: CGFloat = 5.0
    func corner(_ cx: CGFloat, _ cy: CGFloat, _ r: CGFloat, _ a0: CGFloat, _ a1: CGFloat, _ n: CGFloat) {
        for k in 0...steps {
            let t = (a0 + (a1 - a0) * CGFloat(k) / CGFloat(steps)) * .pi / 180
            let c = cos(t), s = sin(t)
            let x = cx + r * (c < 0 ? -1 : 1) * pow(abs(c), 2 / n)
            let y = cy + r * (s < 0 ? -1 : 1) * pow(abs(s), 2 / n)
            if p.isEmpty { p.move(to: CGPoint(x: x, y: y)) } else { p.addLine(to: CGPoint(x: x, y: y)) }
        }
    }
    corner(x1 - top, yT - top, top, 90, 0, nEar)                     // left ear, concave into the menu bar
    corner(x1 + bottom, yB + bottom, bottom, 180, 270, nBottom)      // bottom-left
    corner(x2 - bottom, yB + bottom, bottom, 270, 360, nBottom)      // bottom-right
    corner(x2 + top, yT - top, top, 180, 90, nEar)                   // right ear
    p.closeSubpath()
    return p
}

final class ClickView: NSView {
    var onClick: (() -> Void)?
    var onHover: ((Bool) -> Void)?
    /// x-range (in this view's coordinates) of the real notch, and the height of the menu bar row.
    var notchSpan: (CGFloat, CGFloat) = (0, 0)
    var menuBarHeight: CGFloat = 0
    override func hitTest(_ point: NSPoint) -> NSView? {
        // Points in the menu bar row but outside the notch belong to the menu bar, not to us.
        let topBand = bounds.maxY - menuBarHeight
        if point.y >= topBand, point.x < notchSpan.0 || point.x > notchSpan.1 { return nil }
        return super.hitTest(point)
    }
    private var tracking: NSTrackingArea?
    override func mouseDown(with e: NSEvent) { onClick?() }
    override func acceptsFirstMouse(for event: NSEvent?) -> Bool { true }
    override func updateTrackingAreas() {
        super.updateTrackingAreas()
        if let t = tracking { removeTrackingArea(t) }
        let t = NSTrackingArea(rect: bounds, options: [.mouseEnteredAndExited, .activeAlways], owner: self)
        addTrackingArea(t); tracking = t
    }
    override func mouseEntered(with e: NSEvent) { onHover?(true) }
    override func mouseExited(with e: NSEvent) { onHover?(false) }
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

final class App: NSObject, NSApplicationDelegate, CLLocationManagerDelegate, NSMenuDelegate {
    /// The menu bar's own appearance is unreliable here: on this machine the status button reports VibrantLight while
    /// the system is in Dark mode and the bar is drawn dark, so a template image paints black and disappears. Draw the
    /// symbol in an explicit colour instead, chosen from the system's interface style, and re-render when it changes.
    static func systemIsDark() -> Bool {
        (UserDefaults.standard.string(forKey: "AppleInterfaceStyle") ?? "").lowercased().contains("dark")
    }
    static func shieldIcon(_ color: NSColor, badge: Bool = false) -> NSImage? {
        let cfg = NSImage.SymbolConfiguration(pointSize: 15, weight: .semibold)
        guard let base = NSImage(systemSymbolName: "shield.lefthalf.filled", accessibilityDescription: "Argus")?.withSymbolConfiguration(cfg) else { return nil }
        // NSImage(size:flipped:drawingHandler:) re-draws on demand and works in every context; lockFocus is deprecated
        // and can silently yield an empty image for a status item.
        let size = NSSize(width: base.size.width + (badge ? 5 : 0), height: base.size.height)
        let out = NSImage(size: size, flipped: false) { rect in
            let iconRect = NSRect(x: 0, y: 0, width: base.size.width, height: base.size.height)
            base.draw(in: iconRect)
            color.set()
            iconRect.fill(using: .sourceAtop)
            if badge {                                   // small amber dot; the shield itself stays legible
                Theme.amber.setFill()
                NSBezierPath(ovalIn: NSRect(x: rect.maxX - 4.5, y: rect.maxY - 4.5, width: 4.5, height: 4.5)).fill()
            }
            return true
        }
        out.isTemplate = false
        return out
    }
    func menuNeedsUpdate(_ menu: NSMenu) { rebuildMenu(); status.menu?.delegate = self }
    var panel: NotchPanel!
    let mask = CAShapeLayer()
    var view: ClickView!
    var notch = NSRect.zero
    var bodyW: CGFloat = 440
    let cardW: CGFloat = 440, boardW: CGFloat = 640, earOpen: CGFloat = 32, earClosed: CGFloat = 8, bottomOpen: CGFloat = 44, bottomClosed: CGFloat = 16
    var tintTimer: Timer?
    var depth: CGFloat = 0
    var status: NSStatusItem!
    let monitor = Monitor()
    let devices = DeviceWatch()
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
    var queue: [Alert] = []            // alerts that arrived while one was on screen
    var showing: Alert?
    // always-on strip
    let stats = StatsReader()
    var statsTimer: Timer?
    var statsViews: [NSTextField] = []
    var statsOn: Bool { Store.shared.state.alwaysOn }
    let statsDepth: CGFloat = 26, statsWidth: CGFloat = 430

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
        // Reading the board shouldn't be a race against a timer: hovering holds it open, leaving restarts the countdown.
        view.onHover = { [weak self] inside in
            guard let s = self, s.depth > 0 else { return }
            if inside { s.hideTimer?.invalidate(); s.ring.removeAnimation(forKey: "drain") }
            else { s.armHide(s.boardViews.isEmpty ? 6 : 12) }
        }
        buildLayers()
        for v in [glyph, title, detail, meta] { v.isHidden = true; view.addSubview(v) }
        panel.contentView = view; panel.orderFrontRegardless()

        status = NSStatusBar.system.statusItem(withLength: NSStatusItem.squareLength)
        // isTemplate lets macOS paint the icon for the current menu bar (white on dark, black on light).
        // Without it the symbol keeps its own colour and disappears against a dark menu bar.
        applyTint([])
        if status.button?.image == nil { status.button?.title = "◆" }          // never let the item be invisible
        DistributedNotificationCenter.default.addObserver(forName: Notification.Name("AppleInterfaceThemeChangedNotification"), object: nil, queue: .main) { [weak self] _ in
            guard let s = self else { return }; s.applyTint(s.monitor.cachedPosture)
        }
        // Plugging in a monitor, closing the lid or changing resolution moves the notch. Without this the panel keeps
        // drawing at the old coordinates, i.e. in the middle of nowhere.
        NotificationCenter.default.addObserver(forName: NSApplication.didChangeScreenParametersNotification, object: nil, queue: .main) { [weak self] _ in
            self?.screenChanged()
        }
        rebuildMenu(); status.menu?.delegate = self
        loc.delegate = self
        monitor.locationAllowed = loc.authorizationStatus == .authorizedAlways || loc.authorizationStatus == .authorized
        monitor.onAlert = { [weak self] a in self?.show(a) }
        monitor.onPosture = { [weak self] rows in self?.applyTint(rows) }
        monitor.start()
        devices.onChange = { [weak self] kind, name, on in self?.monitor.deviceChanged(kind: kind, name: name, on: on) }
        devices.start()
        NSWorkspace.shared.notificationCenter.addObserver(forName: NSWorkspace.didLaunchApplicationNotification, object: nil, queue: .main) { [weak self] n in
            guard let app = n.userInfo?[NSWorkspace.applicationUserInfoKey] as? NSRunningApplication, let url = app.bundleURL, let bid = app.bundleIdentifier else { return }
            let name = app.localizedName ?? bid
            self?.monitor.q.asyncAfter(deadline: .now() + 3) { self?.monitor.appLaunched(name: name, bundleID: bid, path: url.path) }
        }
        tintTimer = Timer.scheduledTimer(withTimeInterval: 1800, repeats: true) { [weak self] _ in self?.refreshTint() }
        // Click anywhere else on the screen: close. (Mouse monitors need no permissions; key monitors would.)
        NSEvent.addGlobalMonitorForEvents(matching: [.leftMouseDown, .rightMouseDown]) { [weak self] _ in
            guard let s = self, s.depth > 0, !s.boardViews.isEmpty || s.showing != nil else { return }
            s.hide()
        }
        DispatchQueue.main.asyncAfter(deadline: .now() + 20) { self.refreshTint() }
        if statsOn { DispatchQueue.main.asyncAfter(deadline: .now() + 0.8) { self.startStats() } }
        if ProcessInfo.processInfo.environment["ARGUS_DEMO"] != nil { demo() }
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

    /// Recompute the notch for whatever screen is now the built-in one and re-seat the panel.
    func screenChanged() {
        guard let screen = NSScreen.screens.first(where: { $0.safeAreaInsets.top > 0 }) ?? NSScreen.main else { return }
        let newNotch = notchRect(screen)
        guard newNotch != notch else { return }
        notch = newNotch
        hideTimer?.invalidate(); hideTimer = nil
        for v in [glyph, title, detail, meta] { v.isHidden = true }
        clearBoard(); ring.isHidden = true; pulse.isHidden = true
        depth = 0; gen += 1
        panel.setFrame(closedRect(), display: false)
        view.frame = NSRect(origin: .zero, size: closedRect().size)
        mask.removeAllAnimations(); mask.path = closedPath(in: closedRect().size)
        panel.orderFrontRegardless()
        NSLog("screen changed: notch now %@", NSStringFromRect(notch))
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

    func setDepth(_ d: CGFloat, width: CGFloat? = nil) {
        gen += 1; let g = gen
        if let w = width { bodyW = w }
        defer { syncHitRegion() }
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

    /// One scan feeds both the board and the menu bar tint; never a second pass.
    func refreshTint() { monitor.refreshPosture { [weak self] rows in self?.applyTint(rows) } }
    func applyTint(_ rows: [Collect.PostureRow]) {
        if let p = Store.shared.state.pausedUntil, p > Date() {
            status.button?.image = Self.shieldIcon(Self.systemIsDark() ? NSColor(white: 1, alpha: 0.38) : NSColor(white: 0, alpha: 0.38))
            let f = DateFormatter(); f.dateFormat = "HH:mm"
            status.button?.toolTip = "Argus — alerts paused until \(f.string(from: p))"
            return
        }
        let bad = rows.filter { !$0.ok }.count
        // The shield is always the menu bar's own colour so it is never invisible; attention is an amber dot on it.
        status.button?.image = Self.shieldIcon(Self.systemIsDark() ? .white : .black, badge: bad > 0)
        status.button?.contentTintColor = nil
        status.button?.toolTip = bad > 0 ? "Argus — \(bad) item\(bad == 1 ? "" : "s") need attention" : "Argus — all clear"
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
    /// Alerts arrive in bursts (join a network and three things change at once). Queue them instead of letting each
    /// one overwrite the last unread card.
    func show(_ a: Alert) {
        if a.level == .info { return }
        if showing != nil || !boardViews.isEmpty {
            if !queue.contains(where: { $0.key == a.key }) && queue.count < 6 { queue.append(a) }
            return
        }
        present(a)
    }
    func present(_ a: Alert) {
        showing = a
        statsViews.forEach { $0.isHidden = true }
        clearBoard()
        let d: CGFloat = 78, c = tone(a.level)
        setDepth(d, width: cardW)
        let size = openSize(d), x0 = (size.width - bodyW) / 2
        glyph.image = NSImage(systemSymbolName: symbol(for: a), accessibilityDescription: nil)?.withSymbolConfiguration(.init(pointSize: 22, weight: .medium))
        glyph.contentTintColor = c; glyph.layer?.shadowColor = c.cgColor
        glyph.frame = NSRect(x: x0 + 20, y: d - 52, width: 30, height: 30)
        title.stringValue = a.title; title.frame = NSRect(x: x0 + 62, y: d - 30, width: bodyW - 120, height: 18)
        detail.stringValue = a.detail; detail.frame = NSRect(x: x0 + 62, y: d - 62, width: bodyW - 120, height: 30)
        meta.stringValue = metaLine() + (queue.isEmpty ? "" : "  ·  +\(queue.count) more"); meta.textColor = c.withAlphaComponent(0.85); meta.frame = NSRect(x: x0 + 62, y: 6, width: bodyW - 80, height: 13)
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
        armHide(dur)
    }
    /// Single place that schedules the auto-close, so hover and re-show can't leave two timers racing.
    func armHide(_ seconds: TimeInterval) {
        hideTimer?.invalidate()
        hideTimer = Timer.scheduledTimer(withTimeInterval: seconds, repeats: false) { [weak self] _ in self?.hide() }
    }
    func hide() {
        showing = nil
        hideTimer?.invalidate(); ring.isHidden = true; pulse.isHidden = true
        if let next = queue.first {                       // show the next one after the close settles
            queue.removeFirst()
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.45) { [weak self] in
                guard let s = self, s.showing == nil, s.boardViews.isEmpty else { return }
                s.present(next)
            }
        }
        NSAnimationContext.runAnimationGroup({ ctx in ctx.duration = 0.18; for v in [glyph, title, detail, meta] { v.animator().alphaValue = 0 }; boardViews.forEach { $0.animator().alphaValue = 0 } },
            completionHandler: { for v in [self.glyph, self.title, self.detail, self.meta] { v.isHidden = true }; self.clearBoard()
                                 self.restoreStatsOrClose() })
        if !statsOn { setDepth(0) }
    }
    func clearBoard() { boardViews.forEach { $0.removeFromSuperview() }; boardViews = [] }

    // MARK: status board (click)
    func showBoard() {
        showing = nil; queue.removeAll()               // the board supersedes pending cards
        for v in [glyph, title, detail, meta] { v.isHidden = true }
        ring.isHidden = true; pulse.isHidden = true
        // Render whatever the background scan last produced, immediately. A scan takes ~20 shell calls and must never
        // run on the main thread: that is what made the click feel dead.
        let rows = monitor.cachedPosture
        if rows.isEmpty {
            renderBoard(rows: [Collect.PostureRow(label: "Scanning…", ok: true, value: "", hint: "")], scanning: true)
            monitor.refreshPosture { [weak self] fresh in self?.renderBoard(rows: fresh, scanning: false) }
            return
        }
        renderBoard(rows: rows, scanning: false)
        monitor.refreshPosture { [weak self] fresh in
            guard let s = self, s.depth > 0, !s.boardViews.isEmpty else { return }
            if fresh.map({ "\($0.label)\($0.ok)\($0.value)" }) != rows.map({ "\($0.label)\($0.ok)\($0.value)" }) { s.renderBoard(rows: fresh, scanning: false) }
        }
    }

    func renderBoard(rows: [Collect.PostureRow], scanning: Bool) {
        statsViews.forEach { $0.isHidden = true }
        clearBoard()
        let rowH: CGFloat = 20, perCol = max(1, (rows.count + 1) / 2), d = CGFloat(perCol) * rowH + 52
        setDepth(d, width: boardW)
        let size = openSize(d), x0 = (size.width - bodyW) / 2
        let bad = rows.filter { !$0.ok }.count
        let head = label("SYSTEM STATUS", size: 10, weight: .semibold, color: Theme.cyan, mono: true); head.frame = NSRect(x: x0 + 20, y: d - 26, width: 200, height: 14)
        let sum = label(scanning ? "READING SETTINGS" : (bad == 0 ? "ALL CLEAR" : "\(bad) NEED\(bad == 1 ? "S" : "") ATTENTION"), size: 10, weight: .semibold, color: scanning ? Theme.cyan : (bad == 0 ? Theme.green : Theme.amber), mono: true); sum.frame = NSRect(x: x0 + bodyW - 220, y: d - 26, width: 200, height: 14); sum.alignment = .right
        var all: [NSView] = [head, sum]
        let colW = (bodyW - 40) / 2
        for (i, r) in rows.enumerated() {
            let col = CGFloat(i / perCol), cx = x0 + 20 + col * colW, y = d - 40 - CGFloat(i % perCol) * rowH
            let led = NSView(frame: NSRect(x: cx + 2, y: y - 12, width: 7, height: 7)); led.wantsLayer = true; led.layer?.cornerRadius = 3.5
            let c = r.ok ? Theme.green : Theme.amber; led.layer?.backgroundColor = c.cgColor; led.layer?.shadowColor = c.cgColor; led.layer?.shadowRadius = 5; led.layer?.shadowOpacity = 0.9; led.layer?.shadowOffset = .zero
            let l = label(r.label, size: 11.5, weight: .medium, color: Theme.text); l.frame = NSRect(x: cx + 18, y: y - 16, width: 128, height: 16)
            let v = label(r.value, size: 10, weight: .medium, color: r.ok ? Theme.dim : Theme.text, mono: true); v.frame = NSRect(x: cx + 146, y: y - 15, width: colW - 156, height: 14); v.alignment = .right; v.toolTip = r.hint
            all += [led, l, v]
        }
        let foot = label(metaLine(), size: 10, weight: .medium, color: Theme.cyan.withAlphaComponent(0.7), mono: true); foot.frame = NSRect(x: x0 + 40, y: 6, width: bodyW - 60, height: 13); all.append(foot)
        let step = min(0.008, 0.32 / Double(max(1, all.count)))      // whole cascade lands inside ~0.35 s
        for (i, v) in all.enumerated() {
            view.addSubview(v); boardViews.append(v); v.alphaValue = 0
            let f = v.frame; v.frame = f.offsetBy(dx: -8, dy: 0)
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.04 + Double(i) * step) { NSAnimationContext.runAnimationGroup { ctx in ctx.duration = 0.18; v.animator().alphaValue = 1; v.animator().frame = f } }
        }
        armHide(40)
    }
    func clicked() {
        if !boardViews.isEmpty || showing != nil { hide() }        // something is being shown: dismiss it
        else { showBoard() }                                        // idle, or the always-on strip: open the board
    }

    /// The notch's x-range inside the panel, so clicks on the menu bar either side pass straight through.
    func syncHitRegion() {
        guard let v = view else { return }
        let mid = v.bounds.width / 2
        v.notchSpan = (mid - notch.width / 2, mid + notch.width / 2)
        v.menuBarHeight = notch.height
    }

    // MARK: always-on strip
    /// A permanently open, shallow band under the notch showing live CPU, memory, throughput and Wi-Fi. It yields to
    /// alerts and the board, and restores itself when they close.
    func startStats() {
        stopStats(clearing: false)
        guard statsOn else { return }
        buildStatsViews()
        renderStats()
        statsTimer = Timer.scheduledTimer(withTimeInterval: 1.0, repeats: true) { [weak self] _ in self?.renderStats() }
        RunLoop.main.add(statsTimer!, forMode: .common)
    }
    func stopStats(clearing: Bool = true) {
        statsTimer?.invalidate(); statsTimer = nil
        if clearing { statsViews.forEach { $0.removeFromSuperview() }; statsViews = [] }
    }
    private func buildStatsViews() {
        statsViews.forEach { $0.removeFromSuperview() }; statsViews = []
        for _ in 0..<4 {
            let l = label("", size: 10.5, weight: .medium, color: Theme.dim, mono: true)
            view.addSubview(l); statsViews.append(l)
        }
    }
    private func renderStats() {
        guard statsOn, showing == nil, boardViews.isEmpty else { return }
        if depth != statsDepth || bodyW != statsWidth { setDepth(statsDepth, width: statsWidth) }
        syncHitRegion()
        if statsViews.count < 4 { buildStatsViews() }
        let s = stats.read(interface: monitor.net.iface.isEmpty ? "en0" : monitor.net.iface)
        let size = openSize(statsDepth), x0 = (size.width - statsWidth) / 2
        let bars = StatsReader.bars(s.rssi)
        let wifiCell: String
        if s.wifi {
            let meter = String(repeating: "▮", count: bars) + String(repeating: "▯", count: 4 - bars)
            wifiCell = s.txRate > 0 ? String(format: "%@ %.0fM", meter, s.txRate) : meter
        } else { wifiCell = monitor.net.online ? "WIRED" : "OFFLINE" }
        let cells: [(String, NSColor)] = [
            (String(format: "CPU %.0f%%", s.cpu * 100), s.cpu > 0.8 ? Theme.amber : Theme.cyan),
            (String(format: "MEM %.1fG", s.memGB), s.memUsed > 0.9 ? Theme.amber : Theme.dim),
            ("↓" + StatsReader.rate(s.down) + "  ↑" + StatsReader.rate(s.up), Theme.dim),
            (wifiCell, s.wifi && bars <= 1 ? Theme.amber : Theme.dim)
        ]
        let w = (statsWidth - 28) / 4
        for (i, (text, colour)) in cells.enumerated() {
            let l = statsViews[i]
            l.stringValue = text; l.textColor = colour; l.font = NSFont.monospacedSystemFont(ofSize: 9.5, weight: .medium)
            l.frame = NSRect(x: x0 + 14 + CGFloat(i) * w, y: statsDepth / 2 - 8, width: w - 2, height: 15)
            l.alignment = i == 0 ? .left : (i == 3 ? .right : .center)
            l.isHidden = false
        }
    }
    /// Called whenever an alert or the board finishes, so the strip comes back.
    func restoreStatsOrClose() {
        guard statsOn else { setDepth(0); return }
        statsViews.forEach { $0.isHidden = false }
        setDepth(statsDepth, width: statsWidth)     // unconditional: the board leaves the panel at its own size
        renderStats()
        if statsTimer == nil { startStats() }        // the ticker must never be left stopped
    }

    // MARK: menu
    func rebuildMenu() {
        let m = NSMenu()
        m.addItem(withTitle: "Show status", action: #selector(menuBoard), keyEquivalent: "")
        let rec = Store.shared.state.networks[monitor.net.key]
        let netName = rec?.name ?? monitor.net.displayName
        let home = rec?.isHome ?? false
        let item = NSMenuItem(title: home ? "\(netName) is Home ✓" : "Mark \(netName) as Home", action: #selector(menuHome), keyEquivalent: "")
        item.toolTip = home ? "Click to stop treating this network as Home" : "Argus will announce new devices that join this network"
        item.isEnabled = monitor.net.online
        m.addItem(item)
        if !monitor.locationAllowed { m.addItem(withTitle: "Show Wi-Fi names (needs Location)…", action: #selector(menuLocation), keyEquivalent: "") }
        let paused = (Store.shared.state.pausedUntil ?? .distantPast) > Date()
        m.addItem(withTitle: paused ? "Resume alerts" : "Pause alerts for 1 hour", action: #selector(menuPause), keyEquivalent: "")
        let ao = NSMenuItem(title: "Always-on stats", action: #selector(menuAlwaysOn(_:)), keyEquivalent: "")
        ao.state = statsOn ? .on : .off
        ao.toolTip = "Keep a live strip under the notch showing CPU, memory, network throughput and Wi-Fi signal"
        m.addItem(ao)
        let tls = NSMenuItem(title: "Check for HTTPS interception on new networks", action: #selector(menuTLS(_:)), keyEquivalent: ""); tls.state = Store.shared.state.tlsCheck ? .on : .off; tls.toolTip = "The only connection Argus makes: one HTTPS request to apple.com when you join a new or open network, to see who issued the certificate."; m.addItem(tls)
        let ev = NSMenuItem(title: "Recent events", action: nil, keyEquivalent: ""); let sub = NSMenu()
        let f = DateFormatter(); f.dateFormat = "MMM d HH:mm"
        for (i, e) in Store.shared.state.events.suffix(12).reversed().enumerated() {
            let it = NSMenuItem(title: "\(f.string(from: e.time))  \(e.title)", action: #selector(menuReplay(_:)), keyEquivalent: "")
            it.toolTip = e.detail; it.tag = Store.shared.state.events.count - 1 - i; it.target = self
            sub.addItem(it)
        }
        if sub.items.isEmpty { sub.addItem(withTitle: "Nothing yet", action: nil, keyEquivalent: "") }
        ev.submenu = sub; m.addItem(ev)
        m.addItem(withTitle: "Open data folder", action: #selector(menuData), keyEquivalent: "")
        m.addItem(.separator())
        let login = NSMenuItem(title: "Launch at Login", action: #selector(toggleLogin(_:)), keyEquivalent: ""); login.state = SMAppService.mainApp.status == .enabled ? .on : .off; m.addItem(login)
        m.addItem(withTitle: "Quit Argus", action: #selector(NSApplication.terminate(_:)), keyEquivalent: "q")
        status.menu = m
    }
    @objc func menuBoard() { showBoard() }
    /// Keep the menu bar icon honest after any action that changes what it should say.
    func syncIcon() { applyTint(monitor.cachedPosture) }
    @objc func menuHome() {
        guard monitor.net.online else {
            show(Alert(level: .notice, title: "No network", detail: "Join a network first, then mark it as Home.", key: "home", sticky: false)); return
        }
        let on = monitor.toggleHome(); rebuildMenu()
        let name = Store.shared.state.networks[monitor.net.key]?.name ?? monitor.net.displayName
        show(Alert(level: .notice, title: on ? "\(name) is now Home" : "\(name) is no longer Home",
                   detail: on ? "Argus will announce devices that join this network, and stay quieter about it otherwise."
                              : "Device announcements are off for this network.", key: "home", sticky: false))
    }
    @objc func menuLocation() { loc.requestWhenInUseAuthorization() }
    @objc func menuAlwaysOn(_ item: NSMenuItem) {
        Store.shared.state.alwaysOn.toggle(); Store.shared.save(); rebuildMenu()
        if statsOn { startStats() }
        else { stopStats(); if showing == nil && boardViews.isEmpty { setDepth(0) } }
    }
    @objc func menuTLS(_ item: NSMenuItem) {
        Store.shared.state.tlsCheck.toggle(); Store.shared.save(); rebuildMenu(); syncIcon()
        let on = Store.shared.state.tlsCheck
        present(Alert(level: .notice, title: on ? "HTTPS check on" : "HTTPS check off",
                      detail: on ? "When you join a new or open network, Argus will make one HTTPS request to apple.com and check who issued the certificate. It is the only connection Argus ever makes."
                                 : "Argus now makes no network connections at all.", key: "tls", sticky: false))
    }
    @objc func menuData() { NSWorkspace.shared.open(Store.shared.url.deletingLastPathComponent()) }
    /// Re-show a past event, so the Recent list is readable rather than a dead label.
    @objc func menuReplay(_ item: NSMenuItem) {
        let evs = Store.shared.state.events
        guard item.tag >= 0, item.tag < evs.count else { return }
        let e = evs[item.tag]
        let lvl: Level = e.level == "warning" ? .warning : .notice
        showing = nil; queue.removeAll()
        present(Alert(level: lvl, title: e.title, detail: e.detail, key: "replay", sticky: false))
    }
    @objc func menuPause() {
        let st = Store.shared
        let paused = (st.state.pausedUntil ?? .distantPast) > Date()
        st.state.pausedUntil = paused ? nil : Date().addingTimeInterval(3600); st.save(); rebuildMenu(); syncIcon()
        let f = DateFormatter(); f.dateFormat = "HH:mm"
        let until = st.state.pausedUntil.map { f.string(from: $0) } ?? "later"
        // Shown directly, not through emit(), which is exactly what a pause suppresses.
        present(Alert(level: .notice, title: paused ? "Alerts resumed" : "Alerts paused",
                      detail: paused ? "Argus will speak up again when something changes."
                                     : "Nothing will be shown until \(until). The status board still works.",
                      key: "pause", sticky: false))
    }
    @objc func toggleLogin(_ item: NSMenuItem) {
        let wasOn = SMAppService.mainApp.status == .enabled
        do {
            if wasOn { try SMAppService.mainApp.unregister() } else { try SMAppService.mainApp.register() }
            item.state = wasOn ? .off : .on
            show(Alert(level: .notice, title: wasOn ? "Launch at login off" : "Launch at login on",
                       detail: wasOn ? "Argus will not start itself again." : "Argus will start quietly when you log in.",
                       key: "login", sticky: false))
        } catch {
            // The usual cause is running from somewhere macOS will not register, such as Downloads or a disk image.
            let inApps = Bundle.main.bundlePath.hasPrefix("/Applications")
            show(Alert(level: .warning, title: "Could not set launch at login",
                       detail: inApps ? error.localizedDescription : "Move Argus into your Applications folder and try again.",
                       key: "login-fail", sticky: false))
        }
    }
    func locationManagerDidChangeAuthorization(_ m: CLLocationManager) {
        let ok = m.authorizationStatus == .authorizedAlways || m.authorizationStatus == .authorized
        monitor.locationAllowed = ok           // this pokes the monitor, so the name appears at once
        rebuildMenu()
        if ok { DispatchQueue.main.asyncAfter(deadline: .now() + 1.2) { [weak self] in
            guard let s = self, let name = s.monitor.net.ssid else { return }
            s.show(Alert(level: .notice, title: "Network names are on", detail: "This network is \(name). Argus can label networks by name from now on.", key: "loc-ok", sticky: false)) } }
    }

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
