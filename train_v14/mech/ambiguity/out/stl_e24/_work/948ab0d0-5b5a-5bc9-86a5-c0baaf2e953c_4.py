from build123d import *

base_length = 80.0
base_width = 50.0
base_thickness = 8.0
slot_width = 20.0
slot_length = 40.0
hole_diameter = 4.0
hole_spacing = 40.0
chamfer_distance = 1.0

solid_body = Box(base_length, base_width, base_thickness)
solid_body = solid_body - Box(slot_width, slot_length, base_thickness)

for x, y in [(-hole_spacing/2, 0), (hole_spacing/2, 0)]:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, base_thickness)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_distance)

part = solid_body
part.name = "base_with_slot_and_holes"
export_step(part, "output.step")