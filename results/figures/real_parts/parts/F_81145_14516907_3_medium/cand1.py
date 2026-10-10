from build123d import *

outer_diameter = 80.0
inner_diameter = 30.0
collar_length = 40.0
step_count = 4
step_height = collar_length / step_count
taper_angle = 10.0
shaft_diameter = inner_diameter * 0.5
set_screw_diameter = 5.0
set_screw_offset = 10.0
chamfer_size = 1.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0
shaft_radius = shaft_diameter / 2.0
set_screw_radius = set_screw_diameter / 2.0

with BuildPart() as p:
    with BuildSketch(Plane.XY) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (outer_radius, 0))
            l2 = Line(l1 @ 1, (outer_radius, step_height))
            l3 = Line(l2 @ 1, (outer_radius * 0.8, step_height * 2))
            l4 = Line(l3 @ 1, (outer_radius * 0.6, step_height * 3))
            l5 = Line(l4 @ 1, (outer_radius * 0.4, collar_length))
            l6 = Line(l5 @ 1, (0, collar_length))
            l7 = Line(l6 @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.Y)

solid_body = p.part
solid_body = solid_body + Pos(0, collar_length / 2, 0) * Rot(90, 0, 0) * Cylinder(shaft_radius, collar_length)
solid_body = solid_body - Pos(0, collar_length / 2, 0) * Rot(90, 0, 0) * Cylinder(set_screw_radius, collar_length)
solid_body = solid_body - Pos(set_screw_offset, collar_length / 2, 0) * Rot(90, 0, 0) * Cylinder(set_screw_radius, collar_length)

part = solid_body
part.name = "stepped_collar"
export_step(part, "output.step")