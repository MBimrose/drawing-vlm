from build123d import *

rod_length = 60.0
rod_radius = 5.0
hole_diameter = 6.0
hole_depth = 35.0
tab_width = 12.0
tab_height = 8.0
tab_thickness = 4.0
slot_width = 6.0
slot_length = 10.0
slot_depth = 4.0
chamfer_size = 0.8

rod = Pos(rod_length/2, 0, 0) * Rot(0, 90, 0) * Cylinder(rod_radius, rod_length)
tab = Pos(rod_length, 0, 0) * Box(tab_thickness, tab_width, tab_height)
result = rod + tab

hole = Pos(rod_length - hole_depth/2, 0, 0) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, hole_depth)
result = result - hole

slot = Pos(rod_length + tab_thickness/2 - slot_depth/2, 0, 0) * Box(slot_depth, slot_width, slot_length)
result = result - slot

part = result
part.name = "rod_with_tab"
export_step(part, "output.step")