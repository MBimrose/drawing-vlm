from build123d import *

housing_width = 80
housing_depth = 50
housing_height = 30
wall_thickness = 2
rib_height = 4
rib_thickness = 2

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(housing_width, housing_depth)
    extrude(amount=housing_height)

solid_body = p.part
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[bottom_face])

rib = Pos(0, 0, -rib_height/2) * Box(housing_width - 2*wall_thickness, rib_thickness, rib_height)
solid_body = solid_body + rib

part = solid_body
part.name = "housing_with_rib"
export_step(part, "output.step")