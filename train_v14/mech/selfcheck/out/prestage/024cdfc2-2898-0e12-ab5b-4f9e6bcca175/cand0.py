from build123d import *
import math

outer_radius = 30.0
inner_radius = 12.0
collar_length = 20.0
keyway_width = 6.0
keyway_depth = 4.0
fillet_radius = 2.0
central_hole_diameter = 10.0
mount_hole_diameter = 6.0
mount_hole_spacing = 40.0
rib_height = 3.0
rib_width = 8.0
rib_length = 12.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (outer_radius, 0))
            l2 = Line(l1@1, (outer_radius, collar_length))
            l3 = Line(l2@1, (inner_radius, collar_length))
            l4 = Line(l3@1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = fillet(solid_body.edges(), fillet_radius)

solid_body = solid_body - Pos(0, 0, collar_length/2) * Cylinder(central_hole_diameter/2, collar_length + 10)

keyway_box = Pos(outer_radius - keyway_depth/2, 0, collar_length/2) * Box(keyway_depth, keyway_width, collar_length)
solid_body = solid_body - keyway_box

for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    solid_body = solid_body - Pos(x, 0, collar_length/2) * Cylinder(mount_hole_diameter/2, collar_length + 10)

rib = Pos(outer_radius - rib_height/2, 0, 0) * Box(rib_width, rib_length, rib_height)
solid_body = solid_body + rib

part = solid_body
part.name = "collar_with_keyway"
export_step(part, "output.step")