from build123d import *

total_height = 80.0
base_radius = 15.0
top_radius = 30.0
wall_thickness = 3.0
base_fillet_radius = 2.0
pocket_width = 20.0
pocket_height = 10.0
pocket_depth = 5.0
pocket_offset_z = 40.0

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
solid_body = chamfer(bottom_edges, base_fillet_radius)

pocket = Pos(top_radius - pocket_depth / 2, 0, pocket_offset_z) * Box(pocket_depth, pocket_width, pocket_height)
solid_body = solid_body - pocket

part = solid_body
part.name = "revolved_shell_with_pocket"
export_step(part, "output.step")