from build123d import *

base = Box(80, 8, 40)
bottom_face = base.faces().sort_by(Axis.Z)[0]
bottom_edges = bottom_face.edges()
base = chamfer(bottom_edges, 2)

part = base
part.name = "chamfered_box"
export_step(part, "output.step")