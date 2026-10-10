from build123d import *

base_width = 70.0
base_length = 80.0
base_thickness = 10.0
boss_diameter = 30.0
boss_height = 20.0
shaft_diameter = 15.0
shaft_length = 60.0
slot_width = 12.0
slot_length = 20.0
slot_depth = 5.0
chamfer_distance = 1.0
mount_hole_diameter = 5.0
mount_hole_spacing = 30.0
rib_thickness = 3.0
rib_height = 5.0
rib_length = 50.0

base = Pos(0, 0, base_thickness/2) * Box(base_width, base_length, base_thickness)
boss = Pos(0, 0, base_thickness + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
shaft = Pos(0, 0, base_thickness + boss_height + shaft_length/2) * Cylinder(shaft_diameter/2, shaft_length)
rib = Pos(0, 0, base_thickness + rib_height/2) * Box(rib_length, rib_thickness, rib_height)

result = base + boss + shaft + rib

slot = Pos(0, 0, base_thickness + boss_height + shaft_length/2) * Box(shaft_diameter + 2*slot_depth, slot_width, slot_length)
result = result - slot

for x, y in [(-mount_hole_spacing/2, -mount_hole_spacing/2),
             (mount_hole_spacing/2, -mount_hole_spacing/2),
             (-mount_hole_spacing/2, mount_hole_spacing/2),
             (mount_hole_spacing/2, mount_hole_spacing/2)]:
    result = result - Pos(x, y, base_thickness/2) * Cylinder(mount_hole_diameter/2, base_thickness + 1)

bottom_face = result.faces().sort_by(Axis.Z)[0]
result = chamfer(bottom_face.edges(), chamfer_distance)

part = result
part.name = "base_with_boss_shaft_rib"
export_step(part, "output.step")