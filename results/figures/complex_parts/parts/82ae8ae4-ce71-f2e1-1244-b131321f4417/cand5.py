from build123d import *

outer_radius = 30.0
inner_radius = 10.0
block_height = 60.0
rib_height = 8.0
rib_width = 10.0
rib_position = 35.0
chamfer_size = 1.0
mount_hole_dia = 5.0
mount_hole_offset = 23.0
pocket_radius = 6.0
pocket_depth = 12.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (outer_radius, 0))
            l2 = Line(l1 @ 1, (outer_radius, rib_position))
            l3 = Line(l2 @ 1, (outer_radius + rib_height, rib_position))
            l4 = Line(l3 @ 1, (outer_radius + rib_height, rib_position + rib_width))
            l5 = Line(l4 @ 1, (outer_radius, rib_position + rib_width))
            l6 = Line(l5 @ 1, (outer_radius, block_height))
            l7 = Line(l6 @ 1, (0, block_height))
            l8 = Line(l7 @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

solid_body = solid_body - Cylinder(inner_radius, block_height)
solid_body = solid_body - Pos(0, 0, block_height - pocket_depth / 2) * Cylinder(pocket_radius, pocket_depth)
solid_body = solid_body - Pos(mount_hole_offset, 0, block_height / 2) * Cylinder(mount_hole_dia / 2, block_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "revolved_block_with_rib"
export_step(part, "output.step")