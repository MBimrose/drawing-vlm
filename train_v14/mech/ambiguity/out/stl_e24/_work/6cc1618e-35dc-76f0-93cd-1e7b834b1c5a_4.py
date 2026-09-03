from build123d import *

outer_radius = 30
inner_radius = 20
length = 80
groove_depth = 2
groove_start = 30
groove_end = 50
set_screw_diameter = 5
set_screw_offset = 20
set_screw_depth = 8
chamfer_size = 1

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((outer_radius, 0), (outer_radius, length))
            l2 = Line(l1@1, (inner_radius, length))
            l3 = Line(l2@1, (inner_radius, groove_end))
            l4 = Line(l3@1, (inner_radius + groove_depth, groove_end))
            l5 = Line(l4@1, (inner_radius + groove_depth, groove_start))
            l6 = Line(l5@1, (inner_radius, groove_start))
            l7 = Line(l6@1, (inner_radius, 0))
            l8 = Line(l7@1, (outer_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
top_edges = solid_body.edges().sort_by(Axis.Z)[-2:]
solid_body = chamfer(top_edges, chamfer_size)

hole = Pos(set_screw_offset, set_screw_depth/2, length - set_screw_offset) * Rot(90, 0, 0) * Cylinder(set_screw_diameter/2, set_screw_depth)
solid_body = solid_body - hole

part = solid_body
part.name = "revolved_groove_with_set_screw"
export_step(part, "output.step")