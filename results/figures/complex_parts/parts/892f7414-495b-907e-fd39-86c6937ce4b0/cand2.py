from build123d import *

arm_length = 80.0
arm_width = 30.0
arm_thickness = 10.0
hole_diameter = 10.0
slot_width = 4.0
slot_length = 15.0
slot_spacing = 6.0
num_slots = 3
chamfer_size = 0.3
rib_height = 3.0
rib_thickness = 2.0
rib_spacing = 8.0
rib_offset = 5.0
tab_width = 6.0
tab_height = 3.0
tab_offset = 10.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(arm_length, arm_width)
    extrude(amount=arm_thickness)

solid_body = p.part
solid_body = solid_body - Cylinder(hole_diameter/2, arm_thickness * 2)

slot_start_y = -arm_width/2 + slot_spacing + slot_width/2
for i in range(num_slots):
    y_pos = slot_start_y + i * slot_spacing
    solid_body = solid_body - Pos(-arm_length/2 + slot_length/2, y_pos, 0) * Box(slot_length, slot_width, arm_thickness * 2)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

rib_count = int((arm_width - 2 * rib_offset) / rib_spacing) + 1
for i in range(rib_count):
    y_pos = -arm_width/2 + rib_offset + i * rib_spacing
    solid_body = solid_body + Pos(-arm_length/2 + rib_offset + rib_height/2, y_pos, 0) * Box(rib_height, rib_thickness, arm_width - 2 * rib_offset)

solid_body = solid_body + Pos(-arm_length/2 + tab_offset + tab_width/2, 0, arm_thickness + tab_height/2) * Box(tab_width, tab_height, tab_height)

part = solid_body
part.name = "arm_with_slots_ribs_tab"
export_step(part, "output.step")