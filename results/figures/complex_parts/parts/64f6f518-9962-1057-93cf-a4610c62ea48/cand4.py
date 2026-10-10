from build123d import *

bracket_height = 45.0
bracket_thickness = 10.0
bracket_length = 30.0
taper_length = 15.0
hole_diameter = 5.0
hole_spacing = 15.0
hole_count = 3

with BuildPart() as p:
    with BuildSketch() as s1:
        Circle(bracket_thickness / 2)
    with BuildSketch(Plane.XY.offset(bracket_height)) as s2:
        with BuildLine() as bl:
            Polyline(
                (-bracket_thickness / 2, -bracket_thickness / 2),
                (bracket_length, -bracket_thickness / 2),
                (bracket_length, bracket_thickness / 2),
                (-bracket_thickness / 2, bracket_thickness / 2),
                close=True
            )
        make_face()
    loft()

solid_body = p.part

for i in range(hole_count):
    x = (i - (hole_count - 1) / 2) * hole_spacing
    solid_body = solid_body - Pos(x, 0, bracket_height / 2) * Rot(90, 0, 0) * Cylinder(hole_diameter / 2, bracket_thickness * 2)

part = solid_body
part.name = "bracket"
export_step(part, "output.step")