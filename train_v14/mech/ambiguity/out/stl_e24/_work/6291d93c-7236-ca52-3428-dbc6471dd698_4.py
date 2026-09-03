from build123d import *
import math

base_length = 80.0
base_width = 50.0
base_thickness = 8.0
rib_height = 3.0
rib_offset = 2.0
slot_width = 6.0
slot_length = 10.0
slot_offset_x = 10.0
slot_offset_y = 5.0
hole_diameter = 4.0
hole_countersink_diameter = 8.0
hole_countersink_depth = 2.5
hole_offset_x = 10.0
hole_offset_y = 10.0
chamfer_distance = 1.0

result = Box(base_length, base_width, base_thickness)

rib = Pos(0, 0, base_thickness/2) * Box(base_length - 2*rib_offset, base_width - 2*rib_offset, rib_height)
result = result + rib

slot = Pos(base_length/2 - slot_offset_x, base_width/2 - slot_offset_y, -base_thickness/4) * Box(slot_width, slot_length, base_thickness/2)
result = result - slot

csk = Pos(hole_offset_x, hole_offset_y, base_thickness/2) * CounterSinkHole(hole_diameter/2, hole_countersink_diameter/2, hole_countersink_depth, 90)
result = result - csk

vertical_edges = result.edges().filter_by(Axis.Z)
result = chamfer(vertical_edges, chamfer_distance)

part = result
part.name = "base_plate_with_rib"
export_step(part, "output.step")