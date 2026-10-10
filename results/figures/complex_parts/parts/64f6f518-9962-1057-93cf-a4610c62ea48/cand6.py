from build123d import *

bracket_length = 45.0
circle_diameter = 10.0
rect_width = 30.0
rect_height = 6.0
hole_diameter = 5.0
hole_spacing = 15.0
chamfer_distance = 0.8
rib_thickness = 2.0
rib_height = 4.0
slot_width = 8.0
slot_length = 20.0

with BuildPart() as p:
    with BuildSketch() as s1:
        Circle(circle_diameter / 2)
    with BuildSketch(Plane.XY.offset(bracket_length)) as s2:
        Rectangle(rect_width, rect_height)
    loft()

solid_body = p.part

rib = Pos(0, 0, bracket_length / 2) * Box(rib_thickness, rib_height, bracket_length)
solid_body = solid_body + rib

for x in [-hole_spacing, 0, hole_spacing]:
    solid_body = solid_body - Pos(x, 0, bracket_length / 2) * Rot(90, 0, 0) * Cylinder(hole_diameter / 2, 20)

slot = Pos(rect_width / 2, 0, bracket_length / 2) * Box(slot_width, slot_length, bracket_length)
solid_body = solid_body - slot

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

part = solid_body
part.name = "bracket"
export_step(part, "output.step")