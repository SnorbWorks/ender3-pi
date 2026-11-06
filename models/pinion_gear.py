"""13-tooth spur pinion for the jukebox: mates with a 48-tooth, 64 mm gear.

Those numbers fit 20 diametral pitch (module 1.27 mm): 48T outside diameter
(48 + 2) / 20 = 2.50" = 63.5 mm, 13T outside diameter (13 + 2) / 20 = 0.75".
Centre distance (48 + 13) / 2 / 20 = 1.525" = 38.74 mm.

1" long: 0.5" of teeth on top of a plain 0.5" hub at the gear's outside
diameter, 5 mm bore (printed slightly over size; PETG holes shrink).

The teeth are cut the way a hob cuts them: a straight-sided rack is rolled
around the blank and subtracted at every step.  That gives true involute
flanks and the undercut a 13-tooth gear needs, so it meshes with a standard
48T gear.  The pressure angle of the old gear isn't known, so both common
ones are written: 20 deg (modern) and 14.5 deg (older machinery).

Run with ../.cadvenv/bin/python pinion_gear.py
"""

import math
import struct
import numpy as np
from manifold3d import CrossSection, Manifold

IN = 25.4
DP = 20                       # diametral pitch (teeth per inch of pitch dia.)
M = IN / DP                   # module, mm
N = 13
R = M * N / 2                 # pitch radius 8.255
RO = R + M                    # outside radius 9.525 (0.75" OD)
TEETH_L = 0.5 * IN            # toothed length
HUB_L = 0.5 * IN              # plain hub length
BORE = 5.2                    # 5 mm shaft; printed holes come out ~0.1-0.2 small
BACKLASH = 0.15               # mm thinner teeth: room for print tolerance
SEG = 192


def rack_tooth(pa):
    """One rack tooth (cuts one tooth space), pitch line at y = R, tip down."""
    t = math.tan(pa)
    half = math.pi * M / 4 + BACKLASH / 2          # half width at the pitch line
    y_tip = R - 1.25 * M                           # cuts down to the root circle
    y_top = R + 1.6 * M                            # well past the outside dia.
    return [(-(half - 1.25 * M * t), y_tip), ((half - 1.25 * M * t), y_tip),
            ((half + 1.6 * M * t), y_top), (-(half + 1.6 * M * t), y_top)]


def tooth_space(pa, steps=400, sweep=1.1):
    """Everything the rack tooth sweeps through while rolling on the pitch
    circle: the gear rotates by th, the rack slides -R*th along its pitch line."""
    base = rack_tooth(pa)
    shapes = []
    for th in np.linspace(-sweep, sweep, steps):
        c, s = math.cos(-th), math.sin(-th)
        pts = [((x - R * th) * c - y * s, (x - R * th) * s + y * c) for x, y in base]
        shapes.append(CrossSection([pts]))
    return _union(shapes)


def _union(shapes):
    while len(shapes) > 1:
        shapes = [shapes[i] + shapes[i + 1] if i + 1 < len(shapes) else shapes[i]
                  for i in range(0, len(shapes), 2)]
    return shapes[0]


def gear_profile(pa):
    space = tooth_space(pa)
    blank = CrossSection.circle(RO, SEG)
    cuts = [space.rotate(360.0 * k / N) for k in range(N)]
    return blank - _union(cuts)


def pinion(pa):
    hub = Manifold.cylinder(HUB_L, RO, RO, SEG)
    teeth = gear_profile(pa).extrude(TEETH_L).translate([0, 0, HUB_L])
    # small chamfer on the hub's bottom edge against elephant's foot
    ch = 0.6
    cone = Manifold.cylinder(ch, RO - ch, RO, SEG)
    hub = (hub - Manifold.cylinder(ch, RO + 1, RO + 1, SEG)) + cone
    bore = Manifold.cylinder(TEETH_L + HUB_L + 2, BORE / 2, BORE / 2, 64).translate([0, 0, -1])
    return (hub + teeth) - bore


def write_stl(m, path, dx, dy):
    mesh = m.translate([dx, dy, 0]).to_mesh()
    v = np.asarray(mesh.vert_properties)[:, :3]
    tris = np.asarray(mesh.tri_verts)
    with open(path, "wb") as f:
        f.write(b"13T 20DP pinion - Ender Studio".ljust(80, b" "))
        f.write(struct.pack("<I", len(tris)))
        for a, b, c in tris:
            n = np.cross(v[b] - v[a], v[c] - v[a])
            n = n / (np.linalg.norm(n) or 1)
            f.write(struct.pack("<12fH", *n, *v[a], *v[b], *v[c], 0))
    return len(tris)


if __name__ == "__main__":
    for deg, name in ((20, "pinion13_20dp_pa20.stl"), (14.5, "pinion13_20dp_pa14.5.stl")):
        g = pinion(math.radians(deg))
        assert g.status().name == "NoError", g.status()
        prof = gear_profile(math.radians(deg))
        rs = [math.hypot(x, y) for poly in prof.to_polygons() for x, y in poly]
        print(f"{name}: {write_stl(g, name, 117.5, 117.5)} triangles, "
              f"OD {2 * max(rs):.2f} mm, root dia {2 * min(rs):.2f} mm, "
              f"volume {g.volume() / 1000:.2f} cm3")
