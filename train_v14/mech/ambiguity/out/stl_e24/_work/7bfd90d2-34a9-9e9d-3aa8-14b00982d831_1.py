from build123d import *

outer_radius = 30.0
inner_radius = 8.0
collar_length = 20.0
keyway_width = 6.0
keyway_depth = 4.0
keyway_length = 12.0
set_screw_diameter = 4.0
set_screw_depth = 8.0
set_screw_offset = 5.0
fillet_radius = 1.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, -collar_length/2), (outer_radius, -collar_length/2))
            l2 = Line(l1@1, (outer_radius, collar_length/2))
            l3 = Line(l2@1, (inner_radius, collar_length/2))
            l4 = Line(l3@1, (inner_radius, -collar_length/2))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = fillet(solid_body.edges(), fillet_radius)

keyway = Pos(outer_radius - keyway_depth/2, 0, -keyway_length/2) * Box(keyway_width, keyway_depth, keyway_length)
solid_body = solid_body - keyway

hole1 = Pos(outer_radius - set_screw_depth/2, set_screw_offset, 0) * Rot(90, 0, 0) * Cylinder(set_screw_diameter/2, set_screw_depth)
solid_body = solid_body - hole1

hole2 = Pos(outer_radius - set_screw_depth/2, -set_screw_offset, 0) * Rot(90, 0, 0) * Cylinder(set_screw_diameter/2, set_screw_depth)
solid_body = solid_body - hole2

part = solid_body
part.name = "collar_with_keyway_and_set_screws"
export_step(part, "output.step")