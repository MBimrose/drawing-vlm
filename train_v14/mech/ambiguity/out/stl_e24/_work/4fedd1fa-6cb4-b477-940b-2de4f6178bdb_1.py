from build123d import *

plate_length = 60.0
plate_width = 60.0
plate_thickness = 8.0
central_hole_diameter = 12.0
slot_length = 30.0
slot_width = 10.0
chamfer_distance = 2.0
tab_length = 8.0
tab_width = 6.0
tab_thickness = 4.0

base = Box(plate_length, plate_width, plate_thickness)
base = chamfer(base.edges().filter_by(Axis.Z), chamfer_distance)
base = base - Cylinder(central_hole_diameter/2, plate_thickness)
base = base - Box(slot_length, slot_width, plate_thickness)

left_tab = Pos(-plate_length/2 - tab_length/2, 0, 0) * Box(tab_length, tab_width, tab_thickness)
right_tab = Pos(plate_length/2 + tab_length/2, 0, 0) * Box(tab_length, tab_width, tab_thickness)

part = base + left_tab + right_tab
part.name = "plate_with_tabs"
export_step(part, "output.step")