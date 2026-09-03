from build123d import *

arm_length = 80.0
arm_width = 20.0
arm_thickness = 12.0
groove_width = 12.0
groove_depth = 6.0
groove_length = 60.0
fillet_radius = 2.0
hole_diameter = 6.4
hole_spacing_x = 30.0
hole_spacing_y = 10.0
rib_width = 6.0
rib_height = 4.0
rib_offset = 5.0
slot_width = 4.0
slot_length = 40.0
slot_offset = 8.0

solid_body = Box(arm_length, arm_width, arm_thickness)

groove = Pos(0, 0, arm_thickness - groove_depth/2) * Box(groove_length, groove_width, groove_depth)
solid_body = solid_body - groove

solid_body = fillet(solid_body.edges(), fillet_radius)

hole_positions = [
    (-hole_spacing_x/2, -hole_spacing_y/2),
    (hole_spacing_x/2, -hole_spacing_y/2),
    (-hole_spacing_x/2, hole_spacing_y/2),
    (hole_spacing_x/2, hole_spacing_y/2),
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, arm_thickness * 2)

rib = Pos(0, arm_width/2 - rib_offset, rib_height/2) * Box(rib_width, rib_height, rib_height)
solid_body = solid_body + rib

slot = Pos(0, arm_width/2 - slot_offset, 0) * Box(slot_length, slot_width, arm_thickness * 2)
solid_body = solid_body - slot

part = solid_body
part.name = "arm_with_groove_rib_slot"
export_step(part, "output.step")