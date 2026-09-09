// Ledge — minimal AppKit shell. Build: ./build.sh && open Ledge.app
// A transparent panel sits over the notch; a black layer masked to Apple's notch silhouette (flared ears at the
// top, rounded bottom) plays pixel frames with nearest-neighbour scaling. The art canvas is the whole shape and the
// hardware notch occludes its top centre, so clips can hang from it, climb it, and hide behind it.
// Idle = silhouette shrinks to the hardware notch (invisible, still clickable). Click = random clip.
import AppKit
import ServiceManagement

struct ClipMeta: Decodable { let name: String; let bucket: String; let frames: Int; let fps: Double; let w: Int; let h: Int }

final class NotchPanel: NSPanel { override var canBecomeKey: Bool { false } }

/// Apple's notch silhouette in layer coords (origin bottom-left, screen top at size.height).
/// Radii: closed 6/14, opened 19/24 — the values boring.notch and DynamicNotchKit converged on to match the hardware fillets.
func notchPath(bodyWidth: CGFloat, depth: CGFloat, top: CGFloat, bottom: CGFloat, in size: CGSize) -> CGPath {
    let yT = size.height, yB = size.height - depth
    let x1 = ((size.width - bodyWidth) / 2).rounded(), x2 = x1 + bodyWidth
    let p = CGMutablePath()
    p.move(to: CGPoint(x: x1 - top, y: yT))
    p.addQuadCurve(to: CGPoint(x: x1, y: yT - top), control: CGPoint(x: x1, y: yT))          // left ear
    p.addLine(to: CGPoint(x: x1, y: yB + bottom))
    p.addQuadCurve(to: CGPoint(x: x1 + bottom, y: yB), control: CGPoint(x: x1, y: yB))       // bottom-left
    p.addLine(to: CGPoint(x: x2 - bottom, y: yB))
    p.addQuadCurve(to: CGPoint(x: x2, y: yB + bottom), control: CGPoint(x: x2, y: yB))       // bottom-right
    p.addLine(to: CGPoint(x: x2, y: yT - top))
    p.addQuadCurve(to: CGPoint(x: x2 + top, y: yT), control: CGPoint(x: x2, y: yT))          // right ear
    p.closeSubpath()
    return p
}

final class App: NSObject, NSApplicationDelegate {
    var panel: NotchPanel!
    let mask = CAShapeLayer()
    let strip = CALayer()
    var clips: [ClipMeta] = []
    var clipsDir: URL!
    var frames: [CGImage] = []
    var frameTimer: Timer?
    var visitTimer: Timer?
    var notch = NSRect.zero
    var stripSize = NSSize.zero       // visible strip in points = art size * pxPerArtPx / 2 (Retina)
    var pxPerArtPx: CGFloat = 3       // NP_SCALE: 2 crisp-small · 3 default · 4 chunky-big
    var panelSize = NSSize.zero
    var expandGeneration = 0
    var status: NSStatusItem!
    let earOpen: CGFloat = 19, earClosed: CGFloat = 6, bottomOpen: CGFloat = 24, bottomClosed: CGFloat = 14

    func applicationDidFinishLaunching(_ n: Notification) {
        NSApp.setActivationPolicy(.accessory)
        // Clips: explicit path arg > bundled Resources/clips > the dev folder.
        let bundled = Bundle.main.resourceURL?.appendingPathComponent("clips")
        if CommandLine.arguments.count > 1 { clipsDir = URL(fileURLWithPath: CommandLine.arguments[1]) }
        else if let b = bundled, FileManager.default.fileExists(atPath: b.appendingPathComponent("manifest.json").path) { clipsDir = b }
        else { clipsDir = URL(fileURLWithPath: NSHomeDirectory() + "/Documents/notch-parade/clips") }
        if let d = try? Data(contentsOf: clipsDir.appendingPathComponent("manifest.json")),
           let m = try? JSONDecoder().decode([ClipMeta].self, from: d) { clips = m }
        NSLog("Ledge: %d clips from %@", clips.count, clipsDir.path)

        let screen = NSScreen.screens.first { $0.safeAreaInsets.top > 0 } ?? NSScreen.main!
        notch = notchRect(screen)
        if let v = ProcessInfo.processInfo.environment["NP_SCALE"], let d = Double(v) { pxPerArtPx = CGFloat(d) }
        let artW: CGFloat = 184, artH: CGFloat = 52          // design canvas; clips of any pixel size are fitted to it
        stripSize = NSSize(width: artW * pxPerArtPx / 2, height: artH * pxPerArtPx / 2)   // art covers the WHOLE open shape
        let bodyW = max(stripSize.width, notch.width)
        panelSize = NSSize(width: bodyW + 2 * earOpen, height: max(stripSize.height, notch.height + 8))
        NSLog("notch %@  strip %@ (x%.0f)  panel %@", NSStringFromRect(notch), NSStringFromSize(stripSize), pxPerArtPx, NSStringFromSize(panelSize))

        // Idle: the window is only the notch (plus the small ears), so nothing on screen below it loses clicks.
        // Playing: the window grows to the open shape for the duration of the clip.
        panel = NotchPanel(contentRect: closedRect(), styleMask: [.borderless, .nonactivatingPanel], backing: .buffered, defer: false)
        panel.level = NSWindow.Level(rawValue: NSWindow.Level.statusBar.rawValue + 1)
        panel.collectionBehavior = [.canJoinAllSpaces, .stationary, .fullScreenAuxiliary, .ignoresCycle]
        panel.backgroundColor = .clear; panel.isOpaque = false; panel.hasShadow = false
        panel.ignoresMouseEvents = false; panel.isMovable = false

        let v = ClickView(frame: NSRect(origin: .zero, size: closedRect().size)); v.onClick = { [weak self] in self?.playRandom() }
        v.wantsLayer = true
        v.layer?.backgroundColor = NSColor.black.cgColor
        mask.path = closedPathSmall(); v.layer?.mask = mask
        strip.magnificationFilter = .nearest; strip.minificationFilter = .nearest
        strip.contentsGravity = .resize; strip.backgroundColor = NSColor.black.cgColor
        strip.frame = .zero
        v.layer?.addSublayer(strip)
        panel.contentView = v
        panel.orderFrontRegardless()

        status = NSStatusBar.system.statusItem(withLength: NSStatusItem.squareLength)
        status.button?.title = "🐌"
        let menu = NSMenu()
        menu.addItem(withTitle: "Play a clip", action: #selector(playRandom), keyEquivalent: "p")
        let login = NSMenuItem(title: "Launch at Login", action: #selector(toggleLogin(_:)), keyEquivalent: "")
        login.state = SMAppService.mainApp.status == .enabled ? .on : .off
        menu.addItem(login)
        menu.addItem(.separator())
        menu.addItem(withTitle: "Quit Ledge", action: #selector(NSApplication.terminate(_:)), keyEquivalent: "q")
        status.menu = menu

        scheduleVisitor()
        DispatchQueue.main.asyncAfter(deadline: .now() + 1) { self.playRandom() }
    }

    @objc func toggleLogin(_ item: NSMenuItem) {
        do {
            if SMAppService.mainApp.status == .enabled { try SMAppService.mainApp.unregister(); item.state = .off }
            else { try SMAppService.mainApp.register(); item.state = .on }
        } catch { NSLog("launch at login: %@", error.localizedDescription) }
    }

    func closedPath() -> CGPath { notchPath(bodyWidth: notch.width, depth: notch.height, top: earClosed, bottom: bottomClosed, in: panelSize) }
    func closedRect() -> NSRect { NSRect(x: notch.minX - earClosed, y: notch.minY, width: notch.width + 2 * earClosed, height: notch.height) }
    func openRect() -> NSRect { NSRect(x: notch.midX - panelSize.width / 2, y: notch.maxY - panelSize.height, width: panelSize.width, height: panelSize.height) }
    func closedPathSmall() -> CGPath { notchPath(bodyWidth: notch.width, depth: notch.height, top: earClosed, bottom: bottomClosed, in: closedRect().size) }
    func openPath() -> CGPath { notchPath(bodyWidth: max(stripSize.width, notch.width), depth: panelSize.height, top: earOpen, bottom: bottomOpen, in: panelSize) }

    func notchRect(_ s: NSScreen) -> NSRect {
        let top = s.safeAreaInsets.top
        if top > 0, let l = s.auxiliaryTopLeftArea, let r = s.auxiliaryTopRightArea {
            return NSRect(x: l.maxX, y: s.frame.maxY - top, width: r.minX - l.maxX, height: top)
        }
        return NSRect(x: s.frame.midX - 92, y: s.frame.maxY - 32, width: 185, height: 32)   // no notch: fake the 14" one
    }

    func scheduleVisitor() {
        visitTimer?.invalidate()
        let wait = Double.random(in: 150...300)     // "a visitor every few minutes"
        visitTimer = Timer.scheduledTimer(withTimeInterval: wait, repeats: false) { [weak self] _ in self?.playRandom() }
    }

    @objc func playRandom() {
        guard frameTimer == nil, let meta = clips.randomElement() else { return }
        guard let img = NSImage(contentsOf: clipsDir.appendingPathComponent(meta.name + ".png")),
              let cg = img.cgImage(forProposedRect: nil, context: nil, hints: nil) else { return }
        frames = (0..<meta.frames).compactMap { cg.cropping(to: CGRect(x: 0, y: $0 * meta.h, width: meta.w, height: meta.h)) }
        NSLog("play %@ (%d frames)", meta.name, frames.count)
        expand(true)
        var i = 0
        frameTimer = Timer(timeInterval: 1.0 / meta.fps, repeats: true) { [weak self] t in
            guard let s = self else { return }
            if i >= s.frames.count {
                t.invalidate(); s.frameTimer = nil; s.strip.contents = nil; s.expand(false)
                if ProcessInfo.processInfo.environment["NP_TEST"] != nil { DispatchQueue.main.asyncAfter(deadline: .now() + 0.6) { s.playRandom() } } else { s.scheduleVisitor() }
                return
            }
            s.strip.contents = s.frames[i]; i += 1
        }
        RunLoop.main.add(frameTimer!, forMode: .common)
    }

    /// Morph the silhouette between the hardware notch and the open strip. The window itself is resized around it:
    /// grown before opening, shrunk back to the notch after the close animation settles.
    func expand(_ open: Bool) {
        let bodyW = max(stripSize.width, notch.width)
        if open {
            panel.setFrame(openRect(), display: false)
            panel.contentView?.frame = NSRect(origin: .zero, size: panelSize)
            strip.frame = CGRect(x: ((panelSize.width - bodyW) / 2).rounded(), y: panelSize.height - stripSize.height, width: bodyW, height: stripSize.height)
            mask.removeAllAnimations(); mask.path = closedPath()
        }
        let to = open ? openPath() : closedPath()
        let anim = CASpringAnimation(keyPath: "path")
        anim.fromValue = mask.presentation()?.path ?? mask.path; anim.toValue = to
        anim.damping = 18; anim.stiffness = 260; anim.mass = 1; anim.initialVelocity = 0
        anim.duration = anim.settlingDuration
        mask.add(anim, forKey: "morph"); mask.path = to
        if !open {
            let gen = expandGeneration + 1; expandGeneration = gen
            DispatchQueue.main.asyncAfter(deadline: .now() + anim.settlingDuration) { [weak self] in
                guard let s = self, s.expandGeneration == gen, s.frameTimer == nil else { return }
                s.panel.setFrame(s.closedRect(), display: false)
                s.panel.contentView?.frame = NSRect(origin: .zero, size: s.closedRect().size)
                s.strip.frame = .zero
                s.mask.removeAllAnimations(); s.mask.path = s.closedPathSmall()
            }
        }
    }
}

final class ClickView: NSView {
    var onClick: (() -> Void)?
    override func mouseDown(with e: NSEvent) { onClick?() }
    override func acceptsFirstMouse(for event: NSEvent?) -> Bool { true }
}

let app = NSApplication.shared
let delegate = App()
app.delegate = delegate
app.run()
