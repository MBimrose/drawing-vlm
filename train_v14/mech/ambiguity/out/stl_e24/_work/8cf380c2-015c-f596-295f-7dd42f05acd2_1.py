from build123d import *

jaw_length = 80.0
jaw_width = 30.0
jaw_thickness = 10.0
slot_width = 8.0
slot_depth = 12.0
hole_diameter = 5.0
hole_depth = 8.0
hole_offset_x = 20.0
hole_offset_y = 0.0
chamfer_size = 0.8
rib_height = 4.0
rib_width = 6.0
rib_length = 50.0
pocket_width = 15.0
pocket_height = 10.0
pocket_depth = 3.0
pocket_offset_y = -8.0

result = Box(jaw_length, jaw_width, jaw_thickness)
result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

slot = Pos(0, jaw_width/2 - slot_depth/2, 0) * Box(slot_width, slot_depth, slot_depth)
result = result - slot

hole = Pos(hole_offset_x - jaw_length/2, hole_offset_y, jaw_thickness/2 - hole_depth/2) * Cylinder(hole_diameter/2, hole_depth)
result = result - hole

rib = Pos(0, 0, jaw_thickness/2 + rib_height/2) * Box(rib_length, rib_width, rib_height)
result = result + rib

pocket = Pos(0, -jaw_width/2 + pocket_depth/2, 0) * Box(pocket_width, pocket_depth, pocket_height)
result = result - pocket

part = result
part.name = "jaw_with_slot_hole_rib_pocket"
export_step(part, "output.step")