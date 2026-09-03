from build123d import *

block_length = 80.0
block_width = 60.0
block_thickness = 12.0
corner_radius = 30.0
chamfer_distance = 2.0
hole_diameter = 6.0
hole_edge_margin = 8.0
rib_width = 12.0
rib_height = 4.0
rib_spacing = 20.0
pocket_depth = 8.0
pocket_width = 10.0
pocket_length = block_length - 2 * hole_edge_margin

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((-block_length/2, -block_width/2), (block_length/2, -block_width/2))
            a1 = ThreePointArc(l1@1, (block_length/2 + corner_radius/2, 0), (block_length/2, block_width/2))
            l2 = Line(a1@1, (-block_length/2, block_width/2))
            a2 = ThreePointArc(l2@1, (-block_length/2 - corner_radius/2, 0), (-block_length/2, -block_width/2))
        make_face()
    extrude(amount=block_thickness)

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_distance)

hole_x = block_length/2 - hole_edge_margin
hole_y = block_width/2 - hole_edge_margin
for x, y in [(hole_x, hole_y), (-hole_x, hole_y), (-hole_x, -hole_y), (hole_x, -hole_y)]:
    solid_body = solid_body - Pos(x, y, block_thickness/2) * Cylinder(hole_diameter/2, block_thickness)

for x, y in [(-rib_spacing/2, 0), (rib_spacing/2, 0)]:
    solid_body = solid_body + Pos(x, y, rib_height/2) * Box(rib_width, rib_width, rib_height)

solid_body = solid_body - Pos(0, 0, block_thickness - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)

part = solid_body
part.name = "block_with_arcs_holes_ribs_pocket"
export_step(part, "output.step")