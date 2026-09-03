from build123d import *

with BuildPart() as p:
    Box(20, 20, 10)
    
solid_body = p.part
solid_body = solid_body - Pos(0, 0, 2.5) * Cylinder(2.5, 5)

part = solid_body
part.name = "box_with_hole"
export_step(part, "output.step")