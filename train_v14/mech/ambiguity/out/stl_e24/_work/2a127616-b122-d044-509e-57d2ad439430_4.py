from build123d import *

outer_diameter = 60.0
wall_thickness = 5.0
length = 80.0
rib_width = 6.0
rib_height = 8.0
rib_count = 12
boss_diameter = 20.0
boss_length = 30.0
slot_width = 10.0
slot_depth = 3.0
chamfer_size = 1.0

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness
boss_radius = boss_diameter / 2.0

shell = Pos(0, 0, length/2) * (Cylinder(outer_radius, length) - Cylinder(inner_radius, length))

rib = Pos(outer_radius + rib_height/2.0, 0, length/2) * Box(rib_width, rib_height, length)
ribs = rib
for i in range(1, rib_count):
    ribs = ribs + Rot(0, 0, i * 360.0 / rib_count) * rib

boss = Pos(0, 0, -boss_length/2) * Cylinder(boss_radius, boss_length)
bottom_face = boss.faces().sort_by(Axis.Z)[0]
boss = chamfer(bottom_face.edges(), chamfer_size)

slot = Pos(outer_radius - slot_depth/2.0, 0, length/2.0) * Box(slot_width, slot_depth, length)

part = shell + ribs + boss - slot
part.name = "ribbed_shell_with_boss"
export_step(part, "output.step")