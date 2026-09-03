from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 15.0
pocket_depth = 4.0
pocket_margin = 5.0
fillet_radius = 2.0
hole_diameter = 5.0
hole_offset_x = 20.0
hole_offset_y = 15.0
rib_width = 5.0
rib_height = 3.0
rib_spacing = 15.0
slot_width = 10.0
slot_length = 30.0

solid_body = Box(plate_length, plate_width, plate_thickness)

pocket_w = plate_length - 2 * pocket_margin
pocket_h = plate_width - 2 * pocket_margin
pocket_box = Pos(0, 0, plate_thickness/2 - pocket_depth/2) * Box(pocket_w, pocket_h, pocket_depth)
solid_body = solid_body - pocket_box

pocket_edges = [e for e in solid_body.edges().filter_by(Axis.Z) if e.center().Z > 0]
solid_body = fillet(pocket_edges, fillet_radius)

hole_positions = [
    (hole_offset_x, hole_offset_y),
    (-hole_offset_x, hole_offset_y),
    (hole_offset_x, -hole_offset_y),
    (-hole_offset_x, -hole_offset_y),
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness)

solid_body = solid_body - Box(slot_length, slot_width, plate_thickness)

rib_count_x = int((plate_length - 2 * pocket_margin) // rib_spacing) + 1
rib_start_x = -(plate_length/2 - pocket_margin) + rib_spacing/2
rib_positions = [(rib_start_x + i * rib_spacing, 0) for i in range(rib_count_x)]
for x, y in rib_positions:
    solid_body = solid_body + Pos(x, y, -plate_thickness/2 + rib_height/2) * Box(rib_width, rib_width, rib_height)

part = solid_body
part.name = "plate_with_pocket_holes_slot_ribs"
export_step(part, "output.step")