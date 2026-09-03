from build123d import *

block_length = 80.0
block_width = 50.0
block_height = 30.0
wall_thickness = 2.0
slot_length = 40.0
slot_depth = 15.0
slot_top_width = 20.0
slot_bottom_width = 40.0
fillet_radius = 1.0
mount_hole_diameter = 3.0
mount_hole_spacing_x = 30.0
mount_hole_spacing_y = 20.0
rib_height = 2.0
rib_width = 5.0
rib_spacing = 15.0

solid_body = Box(block_length, block_width, block_height)
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

with BuildPart() as slot_bp:
    with BuildSketch(Plane.XZ.offset(block_width/2)) as slot_sk:
        with BuildLine() as slot_line:
            Polyline(
                (-slot_bottom_width/2, -slot_depth/2),
                (slot_bottom_width/2, -slot_depth/2),
                (slot_top_width/2, slot_depth/2),
                (-slot_top_width/2, slot_depth/2),
                close=True
            )
        make_face()
    extrude(amount=-slot_depth)
solid_body = solid_body - slot_bp.part

hole_positions = [
    (-mount_hole_spacing_x/2, -mount_hole_spacing_y/2),
    (mount_hole_spacing_x/2, -mount_hole_spacing_y/2),
    (-mount_hole_spacing_x/2, mount_hole_spacing_y/2),
    (mount_hole_spacing_x/2, mount_hole_spacing_y/2),
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, block_width/2, y) * Rot(90, 0, 0) * Cylinder(mount_hole_diameter/2, block_width + 10)

rib_count = int((block_length - 2 * wall_thickness) // rib_spacing)
for i in range(rib_count):
    x_pos = -block_length/2 + wall_thickness + rib_spacing/2 + i * rib_spacing
    rib = Pos(x_pos, 0, block_height/2 + rib_height/2) * Box(rib_width, rib_width - 1, rib_height)
    solid_body = solid_body + rib

part = solid_body
part.name = "shelled_block_with_slot_ribs"
export_step(part, "output.step")