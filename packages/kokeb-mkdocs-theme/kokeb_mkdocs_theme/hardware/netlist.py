"""Export a reference circuit as a KiCad netlist (the eeschema export format, version "E").

KiCad's PCB editor reads this file directly (File > Import > Netlist), and most other schematic and PCB tools import
it, so a reader can start a board from the documented circuit instead of redrawing it. The file is deterministic:
no dates or time stamps, components in designator order, nets by name, so a committed export is drift-checked by
comparing bytes.

Each part maps to a symbol of KiCad's standard library where one exists (``Device:R``, ``Device:C``, ``Device:LED``
...); the documented chip, the MCU and other ICs get a ``kokeb`` library part whose pins are listed in ``libparts``.
Chip pins that share a name (GND on several package pins) appear once per package pin. A chip pin on no net is
written as KiCad writes an open pin, a single-node ``unconnected-(...)`` net.
"""

from __future__ import annotations

from .model import Circuit, Hardware

KICAD_LIB = {
    "resistor": ("Device", "R"),
    "capacitor": ("Device", "C"),
    "polarized-capacitor": ("Device", "C_Polarized"),
    "inductor": ("Device", "L"),
    "solenoid": ("Device", "L"),
    "diode": ("Device", "D"),
    "zener": ("Device", "D_Zener"),
    "led": ("Device", "LED"),
    "crystal": ("Device", "Crystal"),
    "fuse": ("Device", "Fuse"),
}
PIN_TYPE = {
    "power": "power_in",
    "ground": "power_in",
    "digital-in": "input",
    "digital-out": "output",
    "digital-io": "bidirectional",
    "open-drain": "open_collector",
    "analog": "passive",
    "bus": "bidirectional",
    "power-out": "power_out",
    "nc": "no_connect",
}
TWO_PIN_NAMES = {"diode": ("A", "K"), "zener": ("A", "K"), "led": ("A", "K"), "polarized-capacitor": ("+", "-")}


def q(s) -> str:
    """A KiCad s-expression string."""
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"') + '"'


def _nodes(hw: Hardware, circ: Circuit, pid: str, pin: str) -> list[tuple[str, str, str]]:
    """(pin number, pin function, pin type) of every package pin behind a circuit node."""
    part = circ.parts[pid]
    if part.kind == "chip":
        return [(str(p.number), p.name, PIN_TYPE[p.type]) for p in hw.pins if p.name == pin]
    if part.two_pin:
        names = TWO_PIN_NAMES.get(part.kind, ("", ""))
        return [(pin, names[int(pin) - 1], "passive")]
    net = circ.net_of(pid, pin)
    kind = "power_in" if net is not None and net.kind in ("supply", "ground") else "bidirectional"
    return [(pin, pin, kind)]


def kicad_netlist(hw: Hardware, circ: Circuit, source: str = "docs/hardware.yml") -> str:
    out = ['(export (version "E")', "  (design", f"    (source {q(source)})", '    (tool "kokeb-docs hardware")',
           '    (sheet (number "1") (name "/") (tstamps "/")',
           f"      (title_block (title {q(hw.chip + ': ' + circ.title)}) (source {q(source)})",
           f'        (comment (number "1") (value {q("Datasheet: " + circ.ref.section + ", p. " + str(circ.ref.page))}))'
           "))", "  )", "  (components"]
    for pid in sorted(circ.parts):
        p = circ.parts[pid]
        if p.kind == "chip":
            lib, part, value = "kokeb", hw.chip, hw.chip
        elif p.kind in KICAD_LIB:
            lib, part = KICAD_LIB[p.kind]
            value = p.value or part
        elif p.kind == "connector":
            lib, part, value = "Connector_Generic", f"Conn_01x{len(p.pins):02d}", p.value or p.label or pid
        else:
            lib, part, value = "kokeb", p.label or pid, p.value or p.label or p.kind
        desc = p.label or p.kind
        out.append(f"    (comp (ref {q(pid)})")
        out.append(f"      (value {q(value)})")
        out.append(f"      (libsource (lib {q(lib)}) (part {q(part)}) (description {q(desc)}))")
        out.append(f"      (property (name \"Datasheet ref\") (value {q(p.ref.section + ', p. ' + str(p.ref.page))}))")
        if p.unverified:
            out.append(f"      (property (name \"Unverified\") (value {q(p.unverified)}))")
        out.append("    )")
    out += ["  )", "  (libparts"]
    seen = set()
    for pid in sorted(circ.parts):
        p = circ.parts[pid]
        if p.kind not in ("chip", "mcu", "ic"):
            continue
        name = hw.chip if p.kind == "chip" else (p.label or pid)
        if name in seen:
            continue
        seen.add(name)
        out.append(f"    (libpart (lib \"kokeb\") (part {q(name)})")
        out.append(f"      (description {q(p.label or p.kind)})")
        out.append("      (pins")
        if p.kind == "chip":
            for hp in sorted(hw.pins, key=lambda x: (x.is_pad, int(x.number) if not x.is_pad else 0)):
                out.append(f"        (pin (num {q(hp.number)}) (name {q(hp.name)}) (type {q(PIN_TYPE[hp.type])}))")
        else:
            for n, _lab in p.pins:
                kind = _nodes(hw, circ, pid, n)[0][2]
                out.append(f"        (pin (num {q(n)}) (name {q(n)}) (type {q(kind)}))")
        out.append("      ))")
    out += ["  )", "  (nets"]
    nets = []
    for n in circ.nets:
        nodes = []
        for pid, pin in n.nodes:
            for num, fn, kind in _nodes(hw, circ, pid, pin):
                nodes.append((pid, num, fn, kind))
        nets.append((n.name, sorted(nodes, key=lambda t: (t[0], _natural(t[1])))))
    chip = circ.chip
    for hp in sorted(hw.pins, key=lambda x: (x.is_pad, int(x.number) if not x.is_pad else 0)):
        if circ.net_of(chip.id, hp.name) is None:
            nets.append((f"unconnected-({chip.id}-{hp.name}-Pad{hp.number})",
                         [(chip.id, str(hp.number), hp.name, PIN_TYPE[hp.type])]))
    for code, (name, nodes) in enumerate(sorted(nets, key=lambda t: t[0]), 1):
        out.append(f"    (net (code {q(code)}) (name {q(name)})")
        for pid, num, fn, kind in nodes:
            func = f" (pinfunction {q(fn)})" if fn else ""
            out.append(f"      (node (ref {q(pid)}) (pin {q(num)}){func} (pintype {q(kind)}))")
        out.append("    )")
    out += ["  )", ")"]
    return "\n".join(out) + "\n"


def _natural(s: str):
    return (0, int(s), "") if s.isdigit() else (1, 0, s)


def check(hw: Hardware, circ: Circuit) -> list[str]:
    """The export's own rules: every net joins at least two package pins, every chip pin is used or marked unused."""
    problems = []
    for n in circ.nets:
        count = sum(len(_nodes(hw, circ, pid, pin)) for pid, pin in n.nodes)
        if count < 2:
            problems.append(f"circuit {circ.id}: net {n.name!r} has {count} node(s)")
    unused = set(circ.unused)
    for hp in hw.pins:
        if circ.net_of(circ.chip.id, hp.name) is None and (circ.chip.id, hp.name) not in unused and hp.type != "nc":
            problems.append(f"circuit {circ.id}: {circ.chip.id}.{hp.name} is on no net and not marked unused")
    return problems
