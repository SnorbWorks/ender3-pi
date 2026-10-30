"""Simple two-part Raspberry Pi 5 case: an open-top tray and a vented lid.

Tray: 3 mm standoffs for M2.5 screws (or a snug press-fit), open end for
the USB/Ethernet ports, slot for USB-C power + both micro-HDMI, microSD slot
and a big cut-out over the power button on the other end.  Lid: drops in
with a lip, vents over the SoC/active cooler, slot for GPIO ribbon cables.

Board numbers from the Pi 5 mechanical drawing (85 x 56 mm, holes 3.5 mm
in, 58 x 49 mm apart).  Writes pi5_case_tray.stl and pi5_case_lid.stl,
already placed side by side on the Ender 3 bed.

Run with ../.cadvenv/bin/python pi5_case.py
"""

import struct
import numpy as np
from manifold3d import Manifold

# --- board
BW, BD, BT = 85.0, 56.0, 1.6
HOLES = [(3.5, 3.5), (61.5, 3.5), (3.5, 52.5), (61.5, 52.5)]
PORTS_Y0 = [11.2, 25.8, 39.2]            # USB-C, HDMI0, HDMI1 (x along the y=0 edge)

# --- case
WALL, FLOOR, GAP = 2.0, 2.0, 1.0
STANDOFF = 3.0
HEADROOM = 19.0                           # above the PCB: USB stack + active cooler
R = 3.0                                   # outer corner radius
IW, ID = BW + 2 * GAP, BD + 2 * GAP
OW, OD = IW + 2 * WALL, ID + 2 * WALL
PCB_Z = FLOOR + STANDOFF                  # underside of the board
OH = PCB_Z + BT + HEADROOM                # tray height
BX, BY = WALL + GAP, WALL + GAP           # board origin in case coordinates

SEG = 64


def box(x0, y0, z0, x1, y1, z1):
    return Manifold.cube([x1 - x0, y1 - y0, z1 - z0]).translate([x0, y0, z0])


def cyl(x, y, z0, h, d):
    return Manifold.cylinder(h, d / 2, d / 2, SEG).translate([x, y, z0])


def rounded(w, d, h, r):
    posts = [cyl(x, y, 0, h, 2 * r) for x in (r, w - r) for y in (r, d - r)]
    return Manifold.batch_hull(posts)


def tray():
    t = rounded(OW, OD, OH, R) - box(WALL, WALL, FLOOR, OW - WALL, OD - WALL, OH + 1)
    for hx, hy in HOLES:
        x, y = BX + hx, BY + hy
        t = t + cyl(x, y, FLOOR - 0.01, STANDOFF + 0.01, 6.0)
        t = t - cyl(x, y, 0.8, OH, 2.4)              # M2.5 self-tapping pilot
    # port end (USB x4 + Ethernet): open above the floor ledge
    t = t - box(OW - WALL - 1, WALL + 1.5, PCB_Z - 0.5, OW + 1, OD - WALL - 1.5, OH + 1)
    # USB-C + 2x micro-HDMI side: one slot sized for the plugs' overmoulds
    x0, x1 = BX + PORTS_Y0[0] - 7, BX + PORTS_Y0[2] + 7
    t = t - box(x0, -1, PCB_Z - 1.0, x1, WALL + 1, PCB_Z + BT + 9.5)
    # far end: microSD under the board, power button + PCIe/fan access above
    t = t - box(-1, BY + BD / 2 - 8, FLOOR + 0.6, WALL + 1, BY + BD / 2 + 8, PCB_Z + 0.4)
    t = t - box(-1, BY + 5, PCB_Z + BT + 1.0, WALL + 1, BY + BD - 5, OH - 4)
    # vent slots along the GPIO-side wall
    for i in range(9):
        x = BX + 10 + i * 7
        t = t - box(x, OD - WALL - 1, PCB_Z + 6, x + 3, OD + 1, OH - 5)
    # vent slots in the floor
    for i in range(7):
        x = BX + 14 + i * 7
        t = t - box(x, BY + 14, -1, x + 3, BY + BD - 14, FLOOR + 1)
    return t


LID_T, LIP_H, LIP_W, FIT = 2.0, 3.0, 1.2, 0.3


def lid():
    plate = rounded(OW, OD, LID_T, R)
    # lip that sits just inside the tray walls (not on the open port end)
    x0, y0 = WALL + FIT, WALL + FIT
    x1, y1 = OW - WALL - FIT - 2, OD - WALL - FIT
    lip = box(x0, y0, LID_T, x1, y1, LID_T + LIP_H) - box(x0 + LIP_W, y0 + LIP_W, LID_T - 1,
                                                          x1 - LIP_W, y1 - LIP_W, LID_T + LIP_H + 1)
    l = plate + lip
    # The lid prints upside down (lip up), so its y is mirrored relative to
    # the tray: the GPIO edge (tray y = OD) sits at lid y = 0.
    gy = lambda ty: OD - ty
    # GPIO header slot (40-pin, 3.5 mm in from the board's top edge)
    l = l - box(BX + 6, gy(BY + BD - 0.5), -1, BX + 59, gy(BY + BD - 7.5), LID_T + 1)
    # vent grid over the SoC / active cooler
    for i in range(8):
        x = BX + 14 + i * 5
        l = l - box(x, gy(BY + 42), -1, x + 2.5, gy(BY + 10), LID_T + 1)
    return l


def write_stl(m, path, dx, dy):
    mesh = m.translate([dx, dy, 0]).to_mesh()
    v = np.asarray(mesh.vert_properties)[:, :3]
    tris = np.asarray(mesh.tri_verts)
    with open(path, "wb") as f:
        f.write(b"Pi 5 case - Ender Studio".ljust(80, b" "))
        f.write(struct.pack("<I", len(tris)))
        for a, b, c in tris:
            n = np.cross(v[b] - v[a], v[c] - v[a])
            n = n / (np.linalg.norm(n) or 1)
            f.write(struct.pack("<12fH", *n, *v[a], *v[b], *v[c], 0))
    return len(tris)


if __name__ == "__main__":
    t, l = tray(), lid()
    assert t.status().name == "NoError" and l.status().name == "NoError"
    # Side by side, centred on the 235 x 235 bed with a 10 mm gap.
    x0 = (235 - (OW * 2 + 10)) / 2
    y0 = (235 - OD) / 2
    print("tray", write_stl(t, "pi5_case_tray.stl", x0, y0), "triangles,",
          f"{OW:.0f} x {OD:.0f} x {OH:.1f} mm, volume {t.volume() / 1000:.1f} cm3")
    print("lid ", write_stl(l, "pi5_case_lid.stl", x0 + OW + 10, y0), "triangles,",
          f"volume {l.volume() / 1000:.1f} cm3")
