from build123d import *

block_width = 80.0
block_height = 60.0
block_thickness = 12.0
arc_radius = 50.0
slot_width = 10.0
slot_length = block_width - 6.0
slot_depth = 8.0
chamfer_distance = 2.0
mount_hole_diameter = 6.0
mount_hole_offset = 8.0
rib_width = 6.0
rib_height = 4.0
rib_length = block_width - 20.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((-block_width/2, -block_height/2), (block_width/2, -block_height/2))
            a1 = ThreePointArc(l1 @ 1, (block_width/2 + 5, 0), (block_width/2, block_height/2))
            l2 = Line(a1 @ 1, (-block_width/2, block_height/2))
            a2 = ThreePointArc(l2 @ 1, (-block_width/2 - 5, 0), (-block_width/2, -block_height/2))
        make_face()
    extrude(amount=block_thickness)

solid_body = p.part

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_distance)

solid_body = solid_body - Pos(0, 0, block_thickness - slot_depth/2) * Box(slot_length, slot_width, slot_depth)

hole_positions = [
    (-block_width/2 + mount_hole_offset, -block_height/2 + mount_hole_offset),
    (block_width/2 - mount_hole_offset, -block_height/2 + mount_hole_offset),
    (-block_width/2 + mount_hole_offset, block_height/2 - mount_hole_offset),
    (block_width/2 - mount_hole_offset, block_height/2 - mount_hole_offset),
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, block_thickness/2) * Cylinder(mount_hole_diameter/2, block_thickness)

solid_body = solid_body + Pos(0, 0, rib_height/2) * Box(rib_length, rib_width, rib_height)

part = solid_body
part.name = "block_with_rib"
export_step(part, "output.step")