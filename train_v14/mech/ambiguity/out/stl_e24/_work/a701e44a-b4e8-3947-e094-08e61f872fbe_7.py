from build123d import *

leg_length = 70.0
leg_width = 20.0
thickness = 8.0
fillet_radius = 4.0
mount_hole_dia = 5.0
mount_hole_offset = 30.0
relief_radius = 6.0
relief_depth = 2.0
rib_width = 6.0
rib_height = 12.0
rib_spacing = 10.0
rib_thickness = 2.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (leg_length, 0))
            l2 = Line(l1 @ 1, (leg_length, leg_length))
            l3 = Line(l2 @ 1, (leg_length - leg_width, leg_length))
            l4 = Line(l3 @ 1, (leg_length - leg_width, leg_width))
            l5 = Line(l4 @ 1, (0, leg_width))
            l6 = Line(l5 @ 1, (0, 0))
        make_face()
    extrude(amount=thickness)

solid_body = p.part

vertical_edges = solid_body.edges().filter_by(Axis.Z)
outer_edges = [e for e in vertical_edges if e.center().X > leg_length - leg_width - 0.01]
solid_body = fillet(outer_edges, fillet_radius)

hole_x = leg_length - leg_width / 2
hole_y = leg_length - mount_hole_offset
solid_body = solid_body - Pos(hole_x, hole_y, thickness / 2) * Cylinder(mount_hole_dia / 2, thickness)

relief_x = leg_length - leg_width / 2
relief_y = leg_length - leg_width / 2
solid_body = solid_body - Pos(relief_x, relief_y, thickness - relief_depth / 2) * Cylinder(relief_radius, relief_depth)

rib_count = int((leg_length - leg_width) // rib_spacing)
for i in range(rib_count):
    rib_x = leg_width / 2 + i * rib_spacing
    rib_y = leg_width / 2
    solid_body = solid_body + Pos(rib_x, rib_y, rib_thickness / 2) * Box(rib_width, rib_height, rib_thickness)

part = solid_body
part.name = "L_bracket_with_ribs"
export_step(part, "output.step")