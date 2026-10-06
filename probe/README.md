# Probe 1: does the head unit look for a MirrorLink server over USB tethering?

`ssdp_listen.py` only listens. It never sends anything to the head unit.

## What it answers

MirrorLink head units find the phone with UPnP/SSDP discovery over a USB network link. A stock Pixel cannot answer the head unit's MirrorLink USB switch command, but its USB tethering already brings up a USB network link (NCM). If the head unit sends SSDP M-SEARCH requests over that link, the no-root bridge is viable.

## Setup (once, on the Pixel)

1. Install Termux from F-Droid (not the Play Store build).
2. In Termux:
   ```
   pkg update && pkg install python
   ```
3. Copy `ssdp_listen.py` into Termux, for example:
   ```
   curl -LO https://raw.githubusercontent.com/TheDevRo/mirrorlinkbridge/claude/nifty-lovelace-8xkj26/probe/ssdp_listen.py
   ```

## In the car (Park, about 10 minutes)

1. Plug the Pixel into the console USB port that is wired to the head unit.
2. On the Pixel: Settings, Network and internet, Hotspot and tethering, turn on USB tethering.
3. In Termux: `python ssdp_listen.py`. Note the interface list it prints. The USB tether interface is usually `ncm0`, `rndis0` or `usb0`.
4. On the head unit, select MirrorLink. Leave it for 60 seconds.
5. Note exactly what the head unit says (photo is ideal).
6. Ctrl+C. Turn off USB tethering. Unplug.

Rollback: turning off tethering and unplugging returns everything to normal. Nothing on the phone or the car is changed.

## What to send back

- The printed interface list.
- `ssdp_probe.log` (in the Termux home directory).
- What the head unit displayed.

## Reading the result

- `MIRRORLINK` lines from an address on the USB tether subnet: pass. The head unit is looking for a MirrorLink server over the link. Next is probe 2.
- Other SSDP traffic only, or nothing from the tether subnet: fail on this path. Either the head unit needs its USB switch command (custom kernel, not possible on this Pixel) or the link never came up. Check whether the tether interface got an address before concluding.
- No tether interface listed at all: the head unit did not accept the Pixel as a network device. Also a fail.
