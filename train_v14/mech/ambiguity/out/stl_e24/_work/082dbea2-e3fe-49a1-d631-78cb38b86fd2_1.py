from build123d import *

with BuildPart() as p:
    Box(30, 20, 10)
solid = p.part
solid = solid - Cylinder(2.5, 10)
solid = fillet(solid.edges().filter_by(Axis.Z), 1)
part = solid
part.name = "filleted_box_with_hole"
export_step(part, "output.step")