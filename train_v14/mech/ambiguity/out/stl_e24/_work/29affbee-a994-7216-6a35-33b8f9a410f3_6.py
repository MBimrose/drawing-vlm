from build123d import *

handle_length = 80.0
outer_radius = 10.0
inner_radius = 4.0
wall_thickness = outer_radius - inner_radius
chamfer_size = 1.0
pocket_width = 12.0
pocket_height = 6.0
pocket_depth = 10.0
pocket_offset = 20.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (inner_radius, handle_length))
            l2 = Line(l1@1, (outer_radius, handle_length))
            l3 = Line(l2@1, (outer_radius, 0))
            l4 = Line(l3@1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

pocket = Pos(0, outer_radius - pocket_height/2, handle_length - pocket_offset) * Box(pocket_width, pocket_height, pocket_depth)
solid_body = solid_body - pocket

part = solid_body
part.name = "handle_with_pocket"
export_step(part, "output.step")