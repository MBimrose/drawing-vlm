from build123d import *

block_length = 80.0
block_width = 50.0
block_thickness = 8.0
rib_height = 3.0
rib_width = 2.0
notch_width = 6.0
notch_depth = 10.0
notch_offset = 5.0
chamfer_distance = 1.0
hole_diameter = 4.0
countersink_diameter = 8.0
countersink_angle = 90.0
countersink_depth = 2.0

base = Pos(0, 0, block_thickness/2) * Box(block_length, block_width, block_thickness)
vertical_edges = base.edges().filter_by(Axis.Z)
base = chamfer(vertical_edges, chamfer_distance)

notch_x = block_length/2 - notch_offset - notch_width/2
notch_y = block_width/2 - notch_depth/2
notch = Pos(notch_x, notch_y, 0) * Box(notch_width, notch_depth, block_thickness)
base = base - notch

hole_x = block_length/4
hole_y = block_width/4
hole = Pos(hole_x, hole_y, block_thickness) * CounterSinkHole(hole_diameter/2, countersink_diameter/2, block_thickness, countersink_angle)
base = base - hole

rib = Pos(0, 0, block_thickness) * Box(block_length - 2*rib_width, block_width - 2*rib_width, rib_height)
result = base + rib

part = result
part.name = "chamfered_block_with_rib"
export_step(part, "output.step")