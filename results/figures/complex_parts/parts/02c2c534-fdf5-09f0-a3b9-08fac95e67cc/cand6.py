from build123d import *

hub_radius = 10.0
hub_length = 10.0
shaft_max_radius = 15.0
shaft_min_radius = 5.0
shaft_length = 60.0
keyway_width = 4.0
keyway_depth = 3.0
chamfer_size = 1.0
hole_diameter = 4.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (hub_radius, 0))
            l2 = Line(l1 @ 1, (hub_radius, hub_length))
            l3 = Line(l2 @ 1, (shaft_max_radius, hub_length + shaft_length * 0.25))
            l4 = Line(l3 @ 1, (shaft_min_radius, hub_length + shaft_length))
            l5 = Line(l4 @ 1, (0, hub_length + shaft_length))
            l6 = Line(l5 @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = solid_body - Cylinder(hole_diameter / 2, 200)
solid_body = solid_body - Pos(0, 0, (hub_length + shaft_length) / 2) * Box(keyway_width, keyway_depth, hub_length + shaft_length)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "shaft_with_keyway"
export_step(part, "output.step")