from build123d import *

bracket_length = 80.0
bracket_height = 40.0
bracket_thickness = 8.0
chamfer_distance = 2.0

solid_body = Box(bracket_length, bracket_thickness, bracket_height)
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
bottom_edges = bottom_face.edges()
solid_body = chamfer(bottom_edges, chamfer_distance)

part = solid_body
part.name = "bracket"
export_step(part, "output.step")