from build123d import *

outer_diameter = 40.0
inner_diameter = 20.0
length = 80.0
groove_width = 12.0
groove_depth = 5.0
groove_offset = 10.0
chamfer_size = 2.0
keyway_width = 6.0
keyway_depth = 4.0
mount_hole_diameter = 4.0
mount_hole_offset = 30.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0
groove_radius = outer_radius - groove_depth

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (outer_radius, 0))
            l2 = Line(l1@1, (outer_radius, groove_offset))
            l3 = Line(l2@1, (groove_radius, groove_offset))
            l4 = Line(l3@1, (groove_radius, groove_offset + groove_width))
            l5 = Line(l4@1, (outer_radius, groove_offset + groove_width))
            l6 = Line(l5@1, (outer_radius, length))
            l7 = Line(l6@1, (0, length))
            l8 = Line(l7@1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = solid_body - Pos(0, 0, length/2) * Cylinder(inner_radius, length)
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_size)
solid_body = solid_body - Pos(inner_radius - keyway_depth/2, 0, length/2) * Box(keyway_depth, keyway_width, length)
solid_body = solid_body - Pos(outer_radius, 0, mount_hole_offset) * Rot(0, 90, 0) * Cylinder(mount_hole_diameter/2, outer_diameter*2)

part = solid_body
part.name = "shaft_with_groove_keyway"
export_step(part, "output.step")