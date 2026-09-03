from build123d import *

total_height = 80.0
base_radius = 15.0
top_radius = 30.0
wall_thickness = 3.0
base_chamfer = 1.0
mount_hole_diameter = 5.0
mount_hole_depth = 10.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (base_radius, 0))
            l2 = Line(l1 @ 1, (base_radius, total_height * 0.2))
            l3 = Line(l2 @ 1, (top_radius, total_height))
            l4 = Line(l3 @ 1, (0, total_height))
            l5 = Line(l4 @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
bottom_edges = bottom_face.edges()
solid_body = chamfer(bottom_edges, base_chamfer)

solid_body = solid_body - Pos(0, 0, total_height - mount_hole_depth / 2) * Cylinder(mount_hole_diameter / 2, mount_hole_depth)

part = solid_body
part.name = "hollow_cone_with_mount_hole"
export_step(part, "output.step")