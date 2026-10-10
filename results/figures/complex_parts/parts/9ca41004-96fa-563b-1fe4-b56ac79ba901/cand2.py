from build123d import *

plate_width = 70.0
plate_length = 80.0
plate_thickness = 10.0
boss_diameter = 30.0
boss_height = 20.0
shaft_diameter = 15.0
shaft_length = 70.0
slot_width = 12.0
slot_length = 20.0
slot_offset_from_base = 50.0
mount_hole_diameter = 5.0
mount_hole_spacing = 30.0
chamfer_size = 1.0
rib_thickness = 3.0
rib_height = 5.0
rib_width = 40.0

result = Box(plate_width, plate_length, plate_thickness)
result = result + Pos(0, 0, plate_thickness/2 + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
result = result + Pos(0, 0, plate_thickness/2 + boss_height + shaft_length/2) * Cylinder(shaft_diameter/2, shaft_length)
result = result + Pos(0, 0, plate_thickness/2 + rib_height/2) * Box(rib_width, rib_thickness, rib_height)

slot_z = plate_thickness/2 + slot_offset_from_base + slot_length/2
result = result - Pos(0, 0, slot_z) * Box(shaft_diameter, slot_width, slot_length)

for x, y in [(-mount_hole_spacing/2, -mount_hole_spacing/2),
             (mount_hole_spacing/2, -mount_hole_spacing/2),
             (-mount_hole_spacing/2, mount_hole_spacing/2),
             (mount_hole_spacing/2, mount_hole_spacing/2)]:
    result = result - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, plate_thickness)

bottom_face = result.faces().sort_by(Axis.Z)[0]
result = chamfer(bottom_face.edges(), chamfer_size)

part = result
part.name = "plate_with_boss_shaft_and_rib"
export_step(part, "output.step")