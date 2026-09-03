from build123d import *

plate_width = 50
plate_depth = 50
plate_thickness = 8
central_hole_diameter = 12
chamfer_size = 2

solid_body = Box(plate_width, plate_depth, plate_thickness)
solid_body = solid_body - Cylinder(central_hole_diameter / 2, plate_thickness)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "plate_with_hole_and_chamfer"
export_step(part, "output.step")