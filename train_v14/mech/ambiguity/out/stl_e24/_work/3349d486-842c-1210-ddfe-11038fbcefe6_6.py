from build123d import *

total_length = 80.0
base_radius = 15.0
wall_thickness = 3.0
inner_radius = base_radius - wall_thickness
flare_extra = 5.0
flare_length = 20.0
set_screw_diameter = 4.0
set_screw_depth = 8.0
chamfer_size = 1.0
groove_radius = inner_radius - 1.0
groove_depth = 5.0
groove_position = 30.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (base_radius, 0))
            l2 = Line(l1 @ 1, (base_radius, total_length - flare_length))
            l3 = Line(l2 @ 1, (base_radius + flare_extra, total_length))
            l4 = Line(l3 @ 1, (0, total_length))
            l5 = Line(l4 @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

groove = Pos(0, 0, groove_position) * Cylinder(groove_radius, groove_depth)
solid_body = solid_body - groove

set_screw = Pos(base_radius + set_screw_depth / 2, 0, total_length / 2) * Rot(0, 90, 0) * Cylinder(set_screw_diameter / 2, set_screw_depth)
solid_body = solid_body - set_screw

top_edges = solid_body.edges().sort_by(Axis.Z)[-1:]
bottom_edges = solid_body.edges().sort_by(Axis.Z)[:1]
solid_body = chamfer(top_edges + bottom_edges, chamfer_size)

part = solid_body
part.name = "revolved_flared_shell"
export_step(part, "output.step")