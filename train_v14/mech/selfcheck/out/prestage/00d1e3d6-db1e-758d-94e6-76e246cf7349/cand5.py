from build123d import *

plate_width = 80.0
plate_depth = 80.0
plate_thickness = 6.0
hole_diameter = 5.0
hole_spacing = 12.0
hole_count = 5
chamfer_size = 0.5

solid_body = Box(plate_width, plate_depth, plate_thickness)

for i in range(hole_count):
    x = (i - (hole_count - 1) / 2) * hole_spacing
    solid_body = solid_body - Pos(x, 0, 0) * Cylinder(hole_diameter / 2, plate_thickness + 3)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "plate_with_holes_and_chamfer"
export_step(part, "output.step")