from build123d import *

# ----- dimensions (mm) -----
outer_dia = 80.0          # outer diameter of the ring
outer_r = outer_dia / 2.0
shell_thickness = 4.0     # thin shell wall
inner_r = outer_r - shell_thickness
axial_len = 20.0          # overall axial length of the ring
boss_dia = 12.0           # central boss diameter
boss_r = boss_dia / 2.0
boss_height = 8.0         # boss projection beyond the flange face
rib_width = 6.0           # radial rib width
rib_fillet_radius = 2.0   # rib / inner corner rounding
num_ribs = 4              # number of radial ribs

# ----- flange ring (thin shell, axis along X) -----
ring = Rot(0, 90, 0) * (Cylinder(outer_r, axial_len) - Cylinder(inner_r, axial_len))

# ----- central boss on the +X face -----
boss = Pos(axial_len / 2 + boss_height / 2, 0, 0) * Rot(0, 90, 0) * Cylinder(boss_r, boss_height)

# ----- radial ribs spanning the bore -----
rib_length = 2 * inner_r
rib = Box(axial_len, rib_length, rib_width)
rib = fillet(rib.edges().filter_by(Axis.X), rib_fillet_radius)

ribs = rib
for i in range(1, num_ribs):
    angle = 360.0 / num_ribs * i
    ribs = ribs + Rot(angle, 0, 0) * rib

# ----- assembly -----
part = ring + boss + ribs
part.name = "flanged_ring_with_ribs"
export_step(part, "output.step")