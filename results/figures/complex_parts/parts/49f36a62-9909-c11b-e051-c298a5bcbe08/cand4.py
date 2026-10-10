from build123d import *

inner_radius = 10.0
wall_thickness = 9.0
outer_radius = inner_radius + wall_thickness
height = 15.0
groove_width = 2.0
groove_depth = 1.0
chamfer_size = 0.5
rib_thickness = 1.0
rib_height = 2.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (inner_radius, height))
            l2 = Line(l1 @ 1, (outer_radius, height))
            l3 = Line(l2 @ 1, (outer_radius, 0))
            l4 = Line(l3 @ 1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

groove_r = outer_radius - groove_width / 2
groove_cyl = Pos(0, 0, height - groove_depth / 2) * Cylinder(groove_r, groove_depth)
solid_body = solid_body - groove_cyl

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

rib = Pos(0, 0, height + rib_height / 2) * Box(rib_thickness, outer_radius * 2, rib_height)
solid_body = solid_body + rib

part = solid_body
part.name = "revolved_ring_with_groove_and_rib"
export_step(part, "output.step")