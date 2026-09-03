from build123d import *

rod_length = 80.0
rod_diameter = 20.0
rod_radius = rod_diameter / 2.0
hole_diameter = 8.0
hole_radius = hole_diameter / 2.0
pocket_width = 12.0
pocket_height = 10.0
pocket_depth = 6.0
pocket_offset = 30.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (rod_radius, 0))
            l2 = Line(l1 @ 1, (rod_radius, rod_length))
            l3 = Line(l2 @ 1, (0, rod_length))
            l4 = Line(l3 @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = solid_body - Pos(0, 0, rod_length / 2) * Cylinder(hole_radius, rod_length)
pocket_box = Pos(0, rod_radius - pocket_depth / 2, pocket_offset + pocket_height / 2) * Box(pocket_width, pocket_depth, pocket_height)
solid_body = solid_body - pocket_box
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "rod_with_pocket"
export_step(part, "output.step")