from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 8.0
pocket_margin = 10.0
pocket_depth = 4.0
central_hole_dia = 12.0
mount_hole_dia = 6.0
mount_hole_spacing = 30.0
mount_hole_offset_y = 10.0
slot_length = 40.0
slot_width = 4.0
slot_offset_y = -20.0
chamfer_size = 1.0
fillet_radius = 0.5
boss_dia = 15.0
boss_height = 5.0

result = Box(plate_length, plate_width, plate_thickness)
result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

pocket_w = plate_length - 2 * pocket_margin
pocket_h = plate_width - 2 * pocket_margin
result = result - Pos(0, 0, plate_thickness/2 - pocket_depth/2) * Box(pocket_w, pocket_h, pocket_depth)

result = result - Cylinder(central_hole_dia/2, plate_thickness + 1)

for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    result = result - Pos(x, mount_hole_offset_y, 0) * Cylinder(mount_hole_dia/2, plate_thickness + 1)

result = result - Pos(0, slot_offset_y, 0) * Box(slot_length, slot_width, plate_thickness + 1)

result = result + Pos(0, 0, plate_thickness/2 + boss_height/2) * Cylinder(boss_dia/2, boss_height)

result = fillet(result.edges().filter_by(Axis.Z), fillet_radius)

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), 0.5)

part = result
part.name = "plate_with_pocket_holes_and_boss"
export_step(part, "output.step")