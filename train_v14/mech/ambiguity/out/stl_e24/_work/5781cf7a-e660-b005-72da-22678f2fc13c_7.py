from build123d import *

block_length = 80.0
block_width = 50.0
block_height = 30.0
wall_thickness = 2.0
slot_width_bottom = 20.0
slot_width_top = 10.0
slot_length = block_length - 2 * wall_thickness
fillet_radius = 1.0
hole_diameter = 4.0
hole_offset_x = 15.0
rib_width = 5.0
rib_height = 4.0
rib_spacing = 15.0
rib_count = int((block_length - 20) / rib_spacing) + 1

solid_body = Box(block_length, block_width, block_height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

with BuildPart() as slot_bp:
    with BuildSketch(Plane.XY.offset(-block_height/2)) as slot_sk:
        with BuildLine() as slot_line:
            Polyline((-slot_width_bottom/2, -slot_length/2), (slot_width_bottom/2, -slot_length/2),
                     (slot_width_top/2, slot_length/2), (-slot_width_top/2, slot_length/2), close=True)
        make_face()
    extrude(amount=block_height)
solid_body = solid_body - slot_bp.part

solid_body = solid_body - Pos(hole_offset_x, 0, 0) * Cylinder(hole_diameter/2, block_height)

for i in range(rib_count):
    x_pos = -block_length/2 + 10 + i * rib_spacing
    rib = Pos(x_pos, 0, block_height/2 + wall_thickness/2) * Box(rib_width, rib_height, wall_thickness)
    solid_body = solid_body + rib

part = solid_body
part.name = "shelled_block_with_slot_hole_ribs"
export_step(part, "output.step")