from build123d import *

plate_length = 80.0
plate_width = 40.0
plate_thickness = 8.0
central_hole_dia = 20.0
groove_width = 4.0
groove_depth = 2.0
slot_width = 8.0
slot_length = 20.0
slot_offset = 20.0
chamfer_size = 1.0
mount_hole_dia = 4.0
mount_hole_offset = 12.0
rib_width = 6.0
rib_height = 4.0
rib_spacing = 40.0

result = Box(plate_length, plate_width, plate_thickness)
result = result - Cylinder(central_hole_dia/2, plate_thickness)

groove_outer = Cylinder(central_hole_dia/2 + groove_width, groove_depth)
groove_inner = Cylinder(central_hole_dia/2, groove_depth)
groove = groove_outer - groove_inner
groove = Pos(0, 0, plate_thickness/2 - groove_depth/2) * groove
result = result - groove

for x in [-slot_offset, slot_offset]:
    result = result - Pos(x, 0, 0) * Box(slot_length, slot_width, plate_thickness)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

for y in [-plate_width/2 + mount_hole_offset, plate_width/2 - mount_hole_offset]:
    result = result - Pos(0, y, 0) * Rot(0, 90, 0) * Cylinder(mount_hole_dia/2, plate_length)

for x in [-rib_spacing/2, rib_spacing/2]:
    result = result + Pos(x, 0, plate_thickness + rib_height/2) * Box(rib_width, plate_width - 2*mount_hole_offset, rib_height)

part = result
part.name = "plate_with_groove_slots_ribs"
export_step(part, "output.step")