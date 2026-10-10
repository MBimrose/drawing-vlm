from build123d import *

plate_length = 80.0
plate_width = 70.0
plate_thickness = 10.0
boss_diameter = 30.0
boss_height = 20.0
step_diameter = 15.0
step_height = 20.0
slot_width = 12.0
slot_length = 60.0
slot_depth = 20.0
chamfer_distance = 1.0
mount_hole_dia = 5.0
mount_hole_spacing = 30.0
rib_thickness = 3.0
rib_height = 5.0

result = Box(plate_width, plate_length, plate_thickness)
result = result + Pos(0, 0, plate_thickness/2 + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
result = result + Pos(0, 0, plate_thickness/2 + boss_height + step_height/2) * Cylinder(step_diameter/2, step_height)
result = result + Pos(0, 0, plate_thickness/2 + boss_height + step_height + step_height/2) * Cylinder(step_diameter/2, step_height)
result = result + Pos(0, 0, plate_thickness/2 + rib_height/2) * Box(plate_width - 20, rib_thickness, rib_height)

slot_box = Pos(0, 0, plate_thickness/2 + boss_height + step_height - slot_depth/2) * Box(slot_length, slot_width, slot_depth)
result = result - slot_box

for x, y in [(-mount_hole_spacing/2, -mount_hole_spacing/2),
             (mount_hole_spacing/2, -mount_hole_spacing/2),
             (-mount_hole_spacing/2, mount_hole_spacing/2),
             (mount_hole_spacing/2, mount_hole_spacing/2)]:
    result = result - Pos(x, y, 0) * Cylinder(mount_hole_dia/2, plate_thickness + 1)

bottom_face = result.faces().sort_by(Axis.Z)[0]
result = chamfer(bottom_face.edges(), chamfer_distance)

part = result
part.name = "plate_with_boss_and_slot"
export_step(part, "output.step")