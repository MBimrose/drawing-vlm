from build123d import *

base = Box(50, 80, 30)
part = chamfer(base.edges(), 1)
part.name = "chamfered_box"
export_step(part, "output.step")