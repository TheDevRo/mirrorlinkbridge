#!/usr/bin/env python3
"""Probe 1: passively log SSDP traffic to see if the head unit looks for a MirrorLink server.

Listen only. Never sends anything. Standard library only, so it runs in stock Termux.
"""

import argparse
import datetime
import fcntl
import socket
import struct
import sys

SSDP_GROUP = "239.255.255.250"
SSDP_PORT = 1900
SIOCGIFADDR = 0x8915
MIRRORLINK_MARKERS = ("tmserverdevice", "tmclientdevice", "mirrorlink")


def ipv4_addresses():
    """Return {ifname: ipv4} for every interface that has an IPv4 address."""
    found = {}
    probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        names = [name for _, name in socket.if_nameindex()]
    except OSError as exc:
        print(f"[warn] could not list interfaces: {exc}", file=sys.stderr)
        names = []
    for name in names:
        try:
            req = struct.pack("256s", name.encode()[:15])
            addr = socket.inet_ntoa(fcntl.ioctl(probe.fileno(), SIOCGIFADDR, req)[20:24])
        except OSError:
            continue
        if not addr.startswith("127."):
            found[name] = addr
    probe.close()
    return found


def open_listener(iface_ips):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", SSDP_PORT))
    joined = []
    for ip in iface_ips:
        mreq = socket.inet_aton(SSDP_GROUP) + socket.inet_aton(ip)
        try:
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
            joined.append(ip)
        except OSError as exc:
            print(f"[warn] join on {ip} failed: {exc}", file=sys.stderr)
    if not joined:
        mreq = socket.inet_aton(SSDP_GROUP) + socket.inet_aton("0.0.0.0")
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        joined.append("0.0.0.0 (default route only)")
    return sock, joined


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--iface-ip", action="append", default=[],
                        help="IPv4 of the interface to listen on (repeatable). Default: all interfaces.")
    parser.add_argument("--log", default="ssdp_probe.log", help="log file path")
    args = parser.parse_args()

    ifaces = ipv4_addresses()
    print("Interfaces with IPv4:")
    for name, ip in ifaces.items():
        print(f"  {name:12} {ip}")
    targets = args.iface_ip or list(ifaces.values())
    sock, joined = open_listener(targets)
    print(f"Listening on UDP {SSDP_PORT}, joined {SSDP_GROUP} on: {', '.join(joined)}")
    print(f"Logging to {args.log}. Ctrl+C to stop.\n")

    with open(args.log, "a", encoding="utf-8") as log:
        log.write(f"\n=== start {datetime.datetime.now().isoformat()} ifaces={ifaces} ===\n")
        try:
            while True:
                data, (src, port) = sock.recvfrom(65535)
                text = data.decode("utf-8", errors="replace")
                first_line = text.split("\r\n", 1)[0]
                hit = any(m in text.lower() for m in MIRRORLINK_MARKERS)
                stamp = datetime.datetime.now().strftime("%H:%M:%S")
                tag = "MIRRORLINK " if hit else ""
                print(f"{stamp} {tag}{src}:{port}  {first_line}")
                log.write(f"--- {stamp} {tag}from {src}:{port}\n{text}\n")
                log.flush()
        except KeyboardInterrupt:
            print("\nStopped.")


if __name__ == "__main__":
    main()
