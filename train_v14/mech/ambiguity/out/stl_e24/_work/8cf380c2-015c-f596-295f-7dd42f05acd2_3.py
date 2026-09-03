from build123d import *

jaw_length = 80.0
jaw_width = 30.0
jaw_thickness = 10.0
rib_length = 50.0
rib_width = 6.0
rib_height = 4.0
pocket_width = 15.0
pocket_depth = 3.0
slot_width = 8.0
slot_height = 8.0
slot_depth = 12.0
hole_diameter = 5.0
hole_offset_x = 20.0
hole_offset_y = 15.0
chamfer_size = 0.8
back_slot_length = 50.0
back_slot_width = 4.0
back_slot_depth = 5.0

result = Box(jaw_length, jaw_width, jaw_thickness)
result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)
result = result + Pos(0, 0, jaw_thickness/2 + rib_height/2) * Box(rib_length, rib_width, rib_height)
result = result - Pos(0, 0, jaw_thickness/2 - pocket_depth/2) * Box(pocket_width, jaw_thickness, pocket_depth)
result = result - Pos(0, jaw_width/2 - slot_depth/2, 0) * Box(slot_width, slot_depth, slot_height)
result = result - Pos(0, -jaw_width/2 + back_slot_depth/2, 0) * Box(back_slot_length, back_slot_depth, back_slot_width)
result = result - Pos(hole_offset_x - jaw_length/2, hole_offset_y - jaw_width/2, 0) * Cylinder(hole_diameter/2, jaw_thickness + rib_height + 2)

part = result
part.name = "jaw_with_rib_and_slots"
export_step(part, "output.step")