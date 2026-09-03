from build123d import *
import math

outer_diameter = 30.0
outer_radius = outer_diameter / 2.0
length = 80.0
groove_depth = 2.0
groove_angle = 60.0
groove_width = 2 * groove_depth * math.tan(math.radians(groove_angle / 2.0))
groove_position = 50.0
set_screw_diameter = 2.5
set_screw_depth = 4.0
set_screw_position = 20.0
chamfer_size = 0.5
tab_width = 12.0
tab_thickness = 3.0
tab_height = 10.0

result = Cylinder(outer_radius, length)
result = chamfer(result.edges(), chamfer_size)

with BuildPart() as gp:
    with BuildSketch(Plane.YZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (groove_width / 2.0, -groove_depth))
            l2 = Line(l1 @ 1, (-groove_width / 2.0, -groove_depth))
            l3 = Line(l2 @ 1, (0, 0))
        make_face()
    extrude(amount=outer_radius * 2)
groove_solid = Pos(0, 0, groove_position - length / 2) * gp.part
result = result - groove_solid

hole_solid = Pos(outer_radius - set_screw_depth / 2, 0, set_screw_position) * Rot(0, 90, 0) * Cylinder(set_screw_diameter / 2, set_screw_depth)
result = result - hole_solid

tab_solid = Pos(outer_radius - tab_thickness / 2, 0, length / 2) * Box(tab_width, tab_thickness, tab_height)
result = result + tab_solid

part = result
part.name = "cylindrical_shaft_with_groove"
export_step(part, "output.step")