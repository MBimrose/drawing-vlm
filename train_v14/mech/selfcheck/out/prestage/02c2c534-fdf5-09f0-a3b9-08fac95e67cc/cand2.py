from build123d import *
import math

hub_radius = 10.0
hub_length = 10.0
shaft_length = 60.0
shaft_end_radius = 5.0
keyway_width = 4.0
keyway_depth = 2.0
keyway_length = 30.0
mount_hole_diameter = 4.0
mount_hole_offset = 15.0
fillet_radius = 2.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((hub_radius, 0), (hub_radius, hub_length))
            l2 = Line(l1@1, (shaft_end_radius, hub_length + shaft_length))
            l3 = Line(l2@1, (0, hub_length + shaft_length))
            l4 = Line(l3@1, (hub_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = solid_body - Cylinder(mount_hole_diameter/2, 200)
keyway_box = Pos(shaft_end_radius - keyway_depth/2, 0, hub_length + shaft_length/2) * Box(keyway_depth, keyway_width, keyway_length)
solid_body = solid_body - keyway_box

part = solid_body
part.name = "hub_shaft_with_keyway"
export_step(part, "output.step")