from build123d import *

base_width = 80
base_height = 40
base_thickness = 8

solid_body = Box(base_width, base_thickness, base_height)
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
bottom_edges = bottom_face.edges()
solid_body = chamfer(bottom_edges, 2)

part = solid_body
part.name = "chamfered_box"
export_step(part, "output.step")