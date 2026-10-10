from build123d import *

plate_width = 70.0
plate_length = 80.0
plate_thickness = 10.0
boss_diameter = 30.0
boss_height = 20.0
step_diameter = 15.0
step_height = 20.0
rod_diameter = 12.0
rod_length = 50.0
slot_width = 12.0
slot_length = 20.0
slot_offset_from_end = 10.0
chamfer_distance = 1.0
mount_hole_diameter = 5.0
mount_hole_spacing = 30.0
rib_width = 50.0
rib_thickness = 3.0
rib_height = 5.0

base = Pos(0, 0, plate_thickness/2) * Box(plate_width, plate_length, plate_thickness)
boss = Pos(0, 0, plate_thickness + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
step = Pos(0, 0, plate_thickness + boss_height + step_height/2) * Cylinder(step_diameter/2, step_height)
rod = Pos(0, 0, plate_thickness + boss_height + step_height + rod_length/2) * Cylinder(rod_diameter/2, rod_length)
rib = Pos(0, 0, plate_thickness + rib_height/2) * Box(rib_width, rib_thickness, rib_height)

result = base + boss + step + rod + rib

slot_center_z = plate_thickness + boss_height + step_height + rod_length - slot_offset_from_end - slot_length/2
slot = Pos(0, 0, slot_center_z) * Box(rod_diameter + 2, slot_width, slot_length)
result = result - slot

for x, y in [(-mount_hole_spacing/2, -mount_hole_spacing/2),
             (mount_hole_spacing/2, -mount_hole_spacing/2),
             (-mount_hole_spacing/2, mount_hole_spacing/2),
             (mount_hole_spacing/2, mount_hole_spacing/2)]:
    result = result - Pos(x, y, plate_thickness/2) * Cylinder(mount_hole_diameter/2, plate_thickness)

bottom_face = result.faces().sort_by(Axis.Z)[0]
result = chamfer(bottom_face.edges(), chamfer_distance)

part = result
part.name = "plate_with_boss_step_rod"
export_step(part, "output.step")