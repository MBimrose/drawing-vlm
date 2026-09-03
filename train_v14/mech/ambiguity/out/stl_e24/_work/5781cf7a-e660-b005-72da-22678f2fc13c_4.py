from build123d import *
import math

block_length = 80.0
block_width = 50.0
block_height = 30.0
wall_thickness = 2.0
slot_bottom_width = 20.0
slot_top_width = 40.0
slot_depth = block_height
draft_angle_deg = 45.0
fillet_radius = 1.0
rib_width = 5.0
rib_height = 4.0
rib_spacing = 15.0
rib_count = int((block_length - 2 * wall_thickness) // rib_spacing)

solid_body = Box(block_length, block_width, block_height)
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

with BuildPart() as slot_bp:
    with BuildSketch(Plane.XY.offset(-block_height/2)) as slot_sk:
        Rectangle(slot_bottom_width, block_width - 2 * wall_thickness)
    extrude(amount=slot_depth, taper=draft_angle_deg)
solid_body = solid_body - slot_bp.part

for i in range(rib_count):
    x = (i - (rib_count - 1) / 2) * rib_spacing
    rib = Pos(x, 0, block_height/2 + wall_thickness/2) * Box(rib_width, rib_height, wall_thickness)
    solid_body = solid_body + rib

part = solid_body
part.name = "shelled_block_with_slot_and_ribs"
export_step(part, "output.step")