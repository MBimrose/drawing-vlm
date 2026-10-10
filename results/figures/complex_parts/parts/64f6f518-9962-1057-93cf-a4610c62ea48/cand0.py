from build123d import *

arm_length = 80.0
circle_diameter = 15.0
rect_width = 30.0
rect_height = 10.0
fillet_radius = 2.0
hole_diameter = 5.0
hole_spacing = 20.0
rib_width = 5.0
rib_height = 3.0
pocket_width = 12.0
pocket_height = 6.0
pocket_depth = 4.0

with BuildPart() as p:
    with BuildSketch() as s1:
        Circle(circle_diameter / 2)
    with BuildSketch(Plane.XY.offset(arm_length)) as s2:
        Rectangle(rect_width, rect_height)
    loft()

solid_body = p.part
solid_body = fillet(solid_body.edges(), fillet_radius)

rib = Pos(0, 0, arm_length / 2) * Box(rib_width, rib_height, arm_length)
solid_body = solid_body + rib

pocket = Pos(0, 0, arm_length - pocket_depth / 2) * Box(pocket_width, pocket_height, pocket_depth)
solid_body = solid_body - pocket

for x in [-hole_spacing, 0, hole_spacing]:
    hole = Pos(x, 0, arm_length / 2) * Rot(90, 0, 0) * Cylinder(hole_diameter / 2, arm_length)
    solid_body = solid_body - hole

part = solid_body
part.name = "lofted_arm_with_rib_pocket_holes"
export_step(part, "output.step")