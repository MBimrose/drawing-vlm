from build123d import *

bracket_length = 80.0
bracket_width = 40.0
bracket_height = 30.0
round_end_diameter = 30.0
hole_diameter = 10.0
keyway_width = 6.0
keyway_depth = 4.0
keyway_length = 40.0
rib_width = 10.0
rib_thickness = 8.0
rib_height = 20.0
rib_offset = 10.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch() as s1:
        Rectangle(bracket_length, bracket_width)
    with BuildSketch(Plane.XY.offset(bracket_height)) as s2:
        Circle(round_end_diameter / 2)
    loft()

solid_body = p.part
solid_body = solid_body - Pos(0, 0, bracket_height / 2) * Cylinder(hole_diameter / 2, bracket_height)
solid_body = solid_body - Pos(0, 0, bracket_height / 2) * Box(keyway_width, keyway_depth, keyway_length)

rib_left = Pos(-bracket_length / 2 + rib_offset, 0, rib_height / 2) * Box(rib_width, rib_thickness, rib_height)
rib_right = Pos(bracket_length / 2 - rib_offset, 0, rib_height / 2) * Box(rib_width, rib_thickness, rib_height)
solid_body = solid_body + rib_left + rib_right

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "bracket"
export_step(part, "output.step")