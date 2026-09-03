from build123d import *

base_width = 60.0
top_width = 30.0
height = 70.0
thickness = 20.0
wall_thickness = 2.0
fillet_radius = 3.0
mount_hole_diameter = 5.0
mount_hole_spacing = 40.0
mount_hole_offset_y = 10.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((-base_width/2, 0), (base_width/2, 0))
            l2 = Line(l1@1, (top_width/2, height - 10))
            a1 = ThreePointArc(l2@1, (0, height), (-top_width/2, height - 10))
            l3 = Line(a1@1, l1@0)
        make_face()
    extrude(amount=thickness)

solid_body = p.part
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[bottom_face])

for x, y in [(-mount_hole_spacing/2, mount_hole_offset_y), (mount_hole_spacing/2, mount_hole_offset_y)]:
    solid_body = solid_body - Pos(x, y, thickness/2) * Cylinder(mount_hole_diameter/2, thickness + 10)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, fillet_radius)

part = solid_body
part.name = "tapered_hollow_block"
export_step(part, "output.step")