from build123d import *

block_length = 80.0
block_width = 60.0
block_thickness = 15.0
groove_width = 5.0
groove_depth = 4.0
hole_diameter = 5.0
hole_offset_x = 20.0
hole_offset_y = 15.0
rib_height = 3.0
rib_thickness = 4.0
chamfer_size = 1.0
slot_length = 30.0
slot_width = 10.0

result = Box(block_length, block_width, block_thickness)

groove_cut = Pos(0, 0, block_thickness/2 - groove_depth/2) * Box(block_length - 2*groove_width, block_width - 2*groove_width, groove_depth)
result = result - groove_cut

rib = Pos(0, 0, block_thickness/2 - rib_height/2) * Box(rib_thickness, block_width - 2*groove_width, rib_height)
result = result + rib

for x, y in [(hole_offset_x, hole_offset_y), (-hole_offset_x, hole_offset_y), (hole_offset_x, -hole_offset_y), (-hole_offset_x, -hole_offset_y)]:
    result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, block_thickness)

slot_cut = Box(slot_length, slot_width, block_thickness)
result = result - slot_cut

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_size)

part = result
part.name = "grooved_block_with_rib"
export_step(part, "output.step")