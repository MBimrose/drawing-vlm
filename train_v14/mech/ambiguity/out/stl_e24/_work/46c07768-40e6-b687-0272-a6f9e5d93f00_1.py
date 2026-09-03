from build123d import *

plate_length = 80.0
plate_width = 40.0
plate_thickness = 5.0
slot_width = 20.0
slot_length = 30.0
slot_radius = slot_width / 2.0
hole_diameter = 10.0
hole_spacing = 60.0
rib_height = 3.0
rib_width = 5.0
rib_offset = 25.0
chamfer_size = 1.0

result = Box(plate_length, plate_width, plate_thickness)
result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

# Slot: rectangular middle + two semicircular ends
slot_rect = Box(slot_width, slot_length - slot_width, plate_thickness)
slot_end1 = Pos(0, (slot_length - slot_width) / 2, 0) * Cylinder(slot_radius, plate_thickness)
slot_end2 = Pos(0, -(slot_length - slot_width) / 2, 0) * Cylinder(slot_radius, plate_thickness)
result = result - slot_rect - slot_end1 - slot_end2

# Through holes
for x in [-hole_spacing / 2, hole_spacing / 2]:
    result = result - Pos(x, 0, 0) * Cylinder(hole_diameter / 2, plate_thickness)

# Ribs on underside
rib_z = -plate_thickness / 2 + rib_height / 2
for x in [-rib_offset, rib_offset]:
    result = result + Pos(x, 0, rib_z) * Box(rib_width, plate_width - 10, rib_height)

part = result
part.name = "plate_with_slot_holes_and_ribs"
export_step(part, "output.step")