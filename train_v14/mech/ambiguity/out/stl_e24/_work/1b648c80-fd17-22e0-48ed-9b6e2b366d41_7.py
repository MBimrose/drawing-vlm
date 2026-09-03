from build123d import *

outer_diameter = 40.0
inner_diameter = 20.0
length = 70.0
key_width = 8.0
key_depth = 5.0
chamfer_size = 2.0
mount_hole_diameter = 4.0
mount_hole_offset = 10.0
groove_width = 15.0
groove_depth = 5.0
groove_offset = 10.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0
wall_thickness = outer_radius - inner_radius

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (outer_radius, 0))
            l2 = Line(l1 @ 1, (outer_radius, groove_offset))
            l3 = Line(l2 @ 1, (outer_radius - groove_depth, groove_offset))
            l4 = Line(l3 @ 1, (outer_radius - groove_depth, groove_offset + groove_width))
            l5 = Line(l4 @ 1, (outer_radius, groove_offset + groove_width))
            l6 = Line(l5 @ 1, (outer_radius, length))
            l7 = Line(l6 @ 1, (0, length))
            l8 = Line(l7 @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_size)

solid_body = solid_body - Pos(0, 0, length / 2) * Cylinder(inner_radius, length)

solid_body = solid_body - Pos(inner_radius - key_depth / 2.0, 0, length / 2) * Box(key_depth, key_width, length)

hole_z = length / 2.0
solid_body = solid_body - Pos(outer_radius - wall_thickness / 2.0, 0, hole_z) * Rot(0, 90, 0) * Cylinder(mount_hole_diameter / 2.0, outer_diameter)

part = solid_body
part.name = "revolved_shaft_with_groove"
export_step(part, "output.step")