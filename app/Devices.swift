import Foundation
import CoreMediaIO
import CoreAudio

/// Camera and microphone activation, using the same public properties OverSight relies on. No entitlement, no
/// polling: CoreMediaIO and CoreAudio call us when a device starts or stops being used by anything on the system.
/// What this cannot do is name the app responsible — that needs Apple's Endpoint Security entitlement.
final class DeviceWatch {
    var onChange: ((_ kind: String, _ name: String, _ on: Bool) -> Void)?
    private var camState: [CMIOObjectID: Bool] = [:]
    private var micState: [AudioObjectID: Bool] = [:]
    private var started = false

    func start() {
        guard !started else { return }; started = true
        for id in cameraIDs() {
            camState[id] = cameraRunning(id)
            var a = addrCM(kCMIODevicePropertyDeviceIsRunningSomewhere)
            CMIOObjectAddPropertyListenerBlock(id, &a, DispatchQueue.main) { [weak self] _, _ in
                guard let s = self else { return }
                let on = s.cameraRunning(id)
                if s.camState[id] != on { s.camState[id] = on; s.onChange?("camera", s.cmName(id), on) }
            }
        }
        for id in micIDs() {
            micState[id] = audioRunning(id)
            var a = addrAU(kAudioDevicePropertyDeviceIsRunningSomewhere)
            AudioObjectAddPropertyListenerBlock(id, &a, DispatchQueue.main) { [weak self] _, _ in
                guard let s = self else { return }
                let on = s.audioRunning(id)
                if s.micState[id] != on { s.micState[id] = on; s.onChange?("microphone", s.auName(id), on) }
            }
        }
        NSLog("DeviceWatch: %d cameras, %d microphones", camState.count, micState.count)
    }

    // MARK: CoreMediaIO
    private func addrCM(_ sel: Int) -> CMIOObjectPropertyAddress {
        CMIOObjectPropertyAddress(mSelector: CMIOObjectPropertySelector(sel),
                                  mScope: CMIOObjectPropertyScope(kCMIOObjectPropertyScopeGlobal),
                                  mElement: CMIOObjectPropertyElement(kCMIOObjectPropertyElementMain))
    }
    func cameraIDs() -> [CMIOObjectID] {
        var a = addrCM(kCMIOHardwarePropertyDevices); var size: UInt32 = 0
        CMIOObjectGetPropertyDataSize(CMIOObjectID(kCMIOObjectSystemObject), &a, 0, nil, &size)
        let n = Int(size) / MemoryLayout<CMIOObjectID>.size; guard n > 0 else { return [] }
        var ids = [CMIOObjectID](repeating: 0, count: n)
        CMIOObjectGetPropertyData(CMIOObjectID(kCMIOObjectSystemObject), &a, 0, nil, size, &size, &ids)
        return ids
    }
    func cameraRunning(_ id: CMIOObjectID) -> Bool {
        var a = addrCM(kCMIODevicePropertyDeviceIsRunningSomewhere)
        var run: UInt32 = 0; var s = UInt32(MemoryLayout<UInt32>.size)
        CMIOObjectGetPropertyData(id, &a, 0, nil, s, &s, &run); return run != 0
    }
    private func cmName(_ id: CMIOObjectID) -> String {
        var a = addrCM(kCMIOObjectPropertyName); var name: CFString = "" as CFString
        var s = UInt32(MemoryLayout<CFString>.size)
        CMIOObjectGetPropertyData(id, &a, 0, nil, s, &s, &name)
        return (name as String).isEmpty ? "Camera" : (name as String)
    }

    // MARK: CoreAudio
    private func addrAU(_ sel: AudioObjectPropertySelector, _ scope: AudioObjectPropertyScope = kAudioObjectPropertyScopeGlobal) -> AudioObjectPropertyAddress {
        AudioObjectPropertyAddress(mSelector: sel, mScope: scope, mElement: kAudioObjectPropertyElementMain)
    }
    func micIDs() -> [AudioObjectID] {
        var a = addrAU(kAudioHardwarePropertyDevices); var size: UInt32 = 0
        AudioObjectGetPropertyDataSize(AudioObjectID(kAudioObjectSystemObject), &a, 0, nil, &size)
        let n = Int(size) / MemoryLayout<AudioObjectID>.size; guard n > 0 else { return [] }
        var ids = [AudioObjectID](repeating: 0, count: n)
        AudioObjectGetPropertyData(AudioObjectID(kAudioObjectSystemObject), &a, 0, nil, &size, &ids)
        return ids.filter { hasInput($0) }
    }
    private func hasInput(_ id: AudioObjectID) -> Bool {
        var a = addrAU(kAudioDevicePropertyStreamConfiguration, kAudioDevicePropertyScopeInput)
        var size: UInt32 = 0; AudioObjectGetPropertyDataSize(id, &a, 0, nil, &size)
        guard size > 0 else { return false }
        let buf = UnsafeMutableRawPointer.allocate(byteCount: Int(size), alignment: 8); defer { buf.deallocate() }
        AudioObjectGetPropertyData(id, &a, 0, nil, &size, buf)
        let abl = buf.assumingMemoryBound(to: AudioBufferList.self)
        return UnsafeMutableAudioBufferListPointer(abl).reduce(0) { $0 + Int($1.mNumberChannels) } > 0
    }
    func audioRunning(_ id: AudioObjectID) -> Bool {
        var a = addrAU(kAudioDevicePropertyDeviceIsRunningSomewhere)
        var run: UInt32 = 0; var s = UInt32(MemoryLayout<UInt32>.size)
        AudioObjectGetPropertyData(id, &a, 0, nil, &s, &run); return run != 0
    }
    private func auName(_ id: AudioObjectID) -> String {
        var a = addrAU(kAudioObjectPropertyName); var name: CFString = "" as CFString
        var s = UInt32(MemoryLayout<CFString>.size)
        AudioObjectGetPropertyData(id, &a, 0, nil, &s, &name)
        return (name as String).isEmpty ? "Microphone" : (name as String)
    }
}
