from build123d import *

jaw_length = 80.0
jaw_width = 30.0
jaw_thickness = 10.0
rib_height = 2.0
rib_width = 3.0
rib_spacing = 5.0
hole_diameter = 10.0
slot_width = 4.0
slot_length = 15.0
slot_spacing = 8.0
chamfer_size = 0.3

solid_body = Box(jaw_length, jaw_width, jaw_thickness)
solid_body = chamfer(solid_body.edges(), chamfer_size)

rib_count = int((jaw_length - rib_spacing) // (rib_width + rib_spacing))
for i in range(rib_count):
    x_pos = -jaw_length/2 + rib_spacing + i*(rib_width + rib_spacing) + rib_width/2
    rib = Pos(x_pos, 0, jaw_thickness/2 + rib_height/2) * Box(rib_width, rib_height, rib_height)
    solid_body = solid_body + rib

for i in range(rib_count):
    x_pos = -jaw_length/2 + rib_spacing + i*(rib_width + rib_spacing) + rib_width/2
    rib = Pos(x_pos, 0, -jaw_thickness/2 - rib_height/2) * Box(rib_width, rib_height, rib_height)
    solid_body = solid_body + rib

solid_body = solid_body - Cylinder(hole_diameter/2, jaw_thickness + 2)

slot_count = int((jaw_width - slot_spacing) // (slot_width + slot_spacing))
for i in range(slot_count):
    y_pos = -jaw_width/2 + slot_spacing + i*(slot_width + slot_spacing) + slot_width/2
    slot = Pos(-jaw_length/2 + jaw_thickness/2, y_pos, 0) * Box(jaw_thickness, slot_width, slot_length)
    solid_body = solid_body - slot

part = solid_body
part.name = "jaw_with_ribs_and_slots"
export_step(part, "output.step")