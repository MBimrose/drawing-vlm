from build123d import *

base = Box(60, 40, 8)
rib = Pos(0, 0, 4) * Box(20, 10, 4)
solid_body = base + rib
hole = CounterSinkHole(2.5, 2.0, 2.0, 82)
solid_body = solid_body - hole
part = solid_body
part.name = "base_with_rib_and_csk_hole"
export_step(part, "output.step")