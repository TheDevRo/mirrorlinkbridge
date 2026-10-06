# MirrorLink Bridge PRD

Status: feasibility phase. No bridge code until probe 1 results are in and the build phase is signed off.

## Problem

The 2016 Subaru Crosstrek's factory Starlink head unit (Gen 2.0/2.1, Fujitsu-TEN/Denso-TEN, TSB 15-205-16R era) has MirrorLink but no CarPlay, and its native UI is poor. iOS cannot act as a MirrorLink server, so an Android device has to sit in the middle:

```
iPhone --(wireless CarPlay)--> Pixel 8 Pro running DiPlay
Pixel 8 Pro --(USB, MirrorLink server)--> Starlink head unit
```

## Success criteria

1. Feasibility answered with evidence: does this head unit talk to a non-Samsung, non-certified MirrorLink server?
2. If yes: DiPlay's CarPlay view renders on the Starlink screen and head-unit touches reach DiPlay, with latency usable while parked. Exact thresholds get set after probe 1.
3. Per-trip startup is: plug in the Pixel, at most one tap (the Android screen capture consent), CarPlay appears on the head unit.
4. No root, bootloader unlock, or wipe of the Pixel at any point.

## Scope

In:
- Probe 1: does the head unit discover a phone in USB tethering (NCM) mode without its own MirrorLink switch command?
- If probe 1 passes: a no-root Android bridge app (UPnP/SSDP responder, MirrorLink-flavored RFB/VNC server fed by MediaProjection, touch injection into DiPlay via an AccessibilityService).
- Audio and calls path testing (Pixel to car over Bluetooth).
- Static, read-only inspection of the TSB 15-205-16R update file if head unit behavior is ambiguous.

Out:
- Rooting, unlocking, or wiping the Pixel.
- Flashing or modifying head unit firmware.
- Opening the head unit for the reported internal USB/ADB pins.
- The Galaxy S9 (see decisions). An optional S9 kernel-switch test is documented in the decision log but not planned.

## Constraints

- **Pixel is a daily, carried in and out.** Plugged into the console USB port per trip. No boot-on-power or battery-heat concerns, but nothing destructive is allowed on it.
- **One USB port, two roles.** The Pixel is the USB device to the head unit, so the iPhone link must be wireless (DiPlay over Wi-Fi Direct, Android 10+).
- **No root means no custom kernel.** The Pixel cannot answer the head unit's MirrorLink USB switch command. The bridge only works if the head unit accepts an NCM link that is already up. Probe 1 tests exactly this.
- **Screen capture consent.** Android 14+ asks for MediaProjection consent per session. One tap per trip is accepted.
- **Pixel is tied up while driving.** DiPlay must stay foreground for capture.
- **Double lossy video.** CarPlay H.264 is decoded on the Pixel, then re-encoded as RFB to a weak display. Expect softness and lag.
- **DiPlay is a public preview, not Apple certified.** Pin a known-good APK.
- **Certification risk.** The head unit may refuse uncertified apps or servers. Unknown until tested.
- **Update file is untrusted.** Forum-mirrored dealer files are inspected in a sandbox only, never flashed.

## Plan

1. **Probe 1 (load-bearing).** Pixel in USB tethering mode, Termux running `probe/ssdp_listen.py`, select MirrorLink on the head unit in Park. Pass = SSDP M-SEARCH (ideally for `TmServerDevice`) from the head unit. Fail = no traffic or a "device not supported" style message. Rollback: turn off tethering, unplug.
2. **DiPlay on the Pixel.** Confirm it installs and launches on GrapheneOS, then pair the iPhone over Wi-Fi Direct. Record connect time and stability.
3. **Audio and calls.** With CarPlay on the Pixel, pair the Pixel to the car over Bluetooth. Check music, calls end to end, and what happens to the iPhone's own link to the car.
4. **If probe 1 passes:** probe 2 responds to discovery with a minimal TmServerDevice description and logs what the head unit fetches next (app list, certificates, VNC connect). This answers the certification question empirically.
5. **If probe 1 fails:** the no-root path on this Pixel is dead. Fallback is a dedicated used Pixel (6 or 7) that lives in the car, with an unlocked bootloader and custom kernel. That needs its own PRD.
6. **Go/no-go write-up**, then a build-phase PRD with fresh sign-off.

## Decision log

| Date | Decision | Alternatives | Why |
|---|---|---|---|
| 2026-10-06 | Head unit integration is the requirement | Dash tablet, off-the-shelf CarPlay screen | Owner's call |
| 2026-10-06 | Galaxy S9 (SM-G960U, Android 10, bootloader rev 9) dropped | S9 as permanent in-car bridge | MirrorLink packages confirmed absent via adb. Bootloader locked, no known root, so no custom server, boot-on-power, or charge cap. Untested: Samsung's kernel may still answer the MirrorLink USB switch on its own. Test procedure exists if revisited. |
| 2026-10-06 | Pixel 8 Pro (GrapheneOS) as bridge, carried per trip | Pixel left in car | It is a daily device |
| 2026-10-06 | No root, unlock, or wipe on the Pixel | Custom GrapheneOS build with own signing keys | Daily device, keep verified boot intact |
| 2026-10-06 | One tap per trip is acceptable | Zero taps | Owner's call. Covers the MediaProjection consent. |

## Open questions

1. Which console USB port is wired to the head unit for data? It must not be a charge-only port.
2. Does the head unit accept an NCM link without its switch command? (Probe 1.)
3. Does it display an uncertified server's screen, and does it change behavior in Drive? (Probe 2.)
4. Does DiPlay need Google Play services on GrapheneOS?
5. Can an app enable USB tethering without root, or is it a manual toggle each trip? If manual, it pushes per-trip taps to two.
6. Does the Starlink unit carry MirrorLink audio, or is Bluetooth A2DP the only audio route? How do calls behave with CarPlay running on the Pixel?
7. Is the reported internal USB/ADB pin access real on this specific unit? (Not planned, recorded only.)
