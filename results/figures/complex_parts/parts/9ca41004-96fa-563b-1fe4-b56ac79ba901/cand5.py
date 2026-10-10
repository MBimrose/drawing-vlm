from build123d import *

base_width = 70.0
base_length = 80.0
base_thickness = 10.0
boss_diameter = 30.0
boss_height = 20.0
step_diameter = 15.0
step_height = 20.0
rod_diameter = 12.0
rod_length = 60.0
slot_width = 12.0
slot_length = 20.0
slot_depth = 2.0
chamfer_size = 1.0
mount_hole_dia = 5.0
mount_hole_spacing = 30.0
rib_thickness = 3.0
rib_height = 3.0
rib_offset = 10.0

result = Pos(0, 0, base_thickness/2) * Box(base_width, base_length, base_thickness)
result = result + Pos(0, 0, base_thickness + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
result = result + Pos(0, 0, base_thickness + boss_height + step_height/2) * Cylinder(step_diameter/2, step_height)
result = result + Pos(0, 0, base_thickness + boss_height + step_height + rod_length/2) * Cylinder(rod_diameter/2, rod_length)

slot_center_z = base_thickness + boss_height + step_height + rod_length/2
result = result - Pos(0, 0, slot_center_z) * Box(rod_diameter + 2*slot_depth, slot_width, slot_length)

for x, y in [(-mount_hole_spacing/2, -mount_hole_spacing/2),
             (mount_hole_spacing/2, -mount_hole_spacing/2),
             (-mount_hole_spacing/2, mount_hole_spacing/2),
             (mount_hole_spacing/2, mount_hole_spacing/2)]:
    result = result - Pos(x, y, base_thickness/2) * Cylinder(mount_hole_dia/2, base_thickness)

rib_length = base_width - 2 * rib_offset
result = result + Pos(0, 0, base_thickness + rib_height/2) * Box(rib_length, rib_thickness, rib_height)

bottom_face = result.faces().sort_by(Axis.Z)[0]
result = chamfer(bottom_face.edges(), chamfer_size)

part = result
part.name = "stepped_boss_with_rod"
export_step(part, "output.step")