from build123d import *

outer_width = 80.0
outer_height = 50.0
thickness = 20.0
wall_thickness = 3.0
corner_radius = 5.0
hole_diameter = 6.0
hole_offset_y = 20.0
slot_width = 12.0
slot_depth = 6.0

inner_width = outer_width - 2 * wall_thickness
inner_height = outer_height - 2 * wall_thickness

solid_body = Box(outer_width, outer_height, thickness)
solid_body = solid_body - Box(inner_width, inner_height, thickness)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, corner_radius)

for y in [hole_offset_y, -hole_offset_y]:
    solid_body = solid_body - Pos(0, y, 0) * Cylinder(hole_diameter / 2, thickness)

slot_y_top = outer_height / 2 - slot_depth / 2
slot_y_bottom = -outer_height / 2 + slot_depth / 2
for y in [slot_y_top, slot_y_bottom]:
    solid_body = solid_body - Pos(0, y, 0) * Box(slot_width, slot_depth, thickness)

part = solid_body
part.name = "hollow_frame_with_holes_and_slots"
export_step(part, "output.step")