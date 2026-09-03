from build123d import *

width = 60.0
depth = 45.0
thickness = 5.0
corner_radius = 4.0
slot_length = 30.0
slot_width = 10.0
hole_diameter = 4.0
hole_spacing = 20.0
hole_offset_y = 15.0
chamfer_size = 0.8

solid_body = Box(width, depth, thickness)
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), corner_radius)

slot = Box(slot_length, slot_width, thickness)
solid_body = solid_body - slot

for x, y in [(-hole_spacing/2, -hole_offset_y), (hole_spacing/2, -hole_offset_y)]:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, thickness)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "plate_with_slot_and_holes"
export_step(part, "output.step")