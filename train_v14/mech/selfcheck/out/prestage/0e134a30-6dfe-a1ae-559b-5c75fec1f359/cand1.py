from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 15.0
rib_length = 60.0
rib_width = 40.0
rib_height = 5.0
pocket_margin = 5.0
pocket_depth = 4.0
slot_length = 30.0
slot_width = 10.0
hole_diameter = 5.0
hole_offset_x = 20.0
hole_offset_y = 15.0
chamfer_size = 0.8

result = Box(plate_length, plate_width, plate_thickness)
result = result + Pos(0, 0, plate_thickness/2 + rib_height/2) * Box(rib_length, rib_width, rib_height)
result = result - Pos(0, 0, plate_thickness/2 + rib_height - pocket_depth/2) * Box(plate_length - 2*pocket_margin, plate_width - 2*pocket_margin, pocket_depth)
result = result - Box(slot_length, slot_width, plate_thickness + rib_height)

hole_positions = [
    (hole_offset_x, hole_offset_y),
    (-hole_offset_x, hole_offset_y),
    (hole_offset_x, -hole_offset_y),
    (-hole_offset_x, -hole_offset_y)
]
for x, y in hole_positions:
    result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness + rib_height)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "plate_with_rib_pocket_slot_holes"
export_step(part, "output.step")