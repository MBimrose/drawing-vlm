from build123d import *

plate_width = 50
plate_length = 50
plate_thickness = 8
hole_diameter = 12
chamfer_distance = 2

solid_body = Box(plate_width, plate_length, plate_thickness)
solid_body = solid_body - Cylinder(hole_diameter / 2, plate_thickness)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_distance)

part = solid_body
part.name = "chamfered_plate"
export_step(part, "output.step")