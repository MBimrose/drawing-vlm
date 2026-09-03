from build123d import *

base_radius = 15.0
base_height = 15.0
cone_height = 65.0
cone_top_radius = 30.0
wall_thickness = 3.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (base_radius, 0))
            l2 = Line(l1@1, (base_radius, base_height))
            l3 = Line(l2@1, (cone_top_radius, base_height + cone_height))
            l4 = Line(l3@1, (0, base_height + cone_height))
            l5 = Line(l4@1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
bottom_edges = bottom_face.edges()
solid_body = chamfer(bottom_edges, chamfer_size)

part = solid_body
part.name = "hollow_cone_with_base"
export_step(part, "output.step")