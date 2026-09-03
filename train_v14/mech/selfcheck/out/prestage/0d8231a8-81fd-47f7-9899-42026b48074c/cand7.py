from build123d import *

base = Pos(0, 0, 15) * Box(50, 80, 30)
part = chamfer(base.edges(), 1)
part.name = "chamfered_box"
export_step(part, "output.step")