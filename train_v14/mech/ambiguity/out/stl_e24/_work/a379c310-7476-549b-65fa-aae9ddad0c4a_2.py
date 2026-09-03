from build123d import *

lever_length = 80.0
lever_width = 20.0
lever_thickness = 8.0
tab_length = 15.0
tab_width = 12.0
slot_width = 6.0
slot_depth = 4.0
hole_diameter = 4.0
countersink_diameter = 7.0
countersink_angle = 82.0
chamfer_distance = 1.0

base = Box(lever_length, lever_width, lever_thickness)
tab = Pos(lever_length/2 + tab_length/2, 0, 0) * Box(tab_length, tab_width, lever_thickness)
result = base + tab

slot = Pos(lever_length/2 + tab_length/2, 0, 0) * Box(slot_depth, slot_width, lever_thickness + 0.01)
result = result - slot

hole1 = Pos(-lever_length/3, 0, lever_thickness/2) * CounterSinkHole(hole_diameter/2, countersink_diameter/2, lever_thickness, countersink_angle)
hole2 = Pos(lever_length/3, 0, lever_thickness/2) * CounterSinkHole(hole_diameter/2, countersink_diameter/2, lever_thickness, countersink_angle)
result = result - hole1 - hole2

part = result
part.name = "lever_with_tab"
export_step(part, "output.step")