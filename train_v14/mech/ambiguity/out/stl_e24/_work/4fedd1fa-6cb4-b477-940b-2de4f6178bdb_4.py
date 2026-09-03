from build123d import *

plate_length = 60.0
plate_width = 60.0
plate_thickness = 8.0
corner_chamfer = 2.0
central_hole_dia = 12.0
slot_length = 30.0
slot_width = 10.0
tab_length = 12.0
tab_width = 6.0
tab_thickness = 4.0
tab_overlap = 2.0

base = Box(plate_length, plate_width, plate_thickness)
base = chamfer(base.edges().filter_by(Axis.Z), corner_chamfer)
base = base - Cylinder(central_hole_dia/2, plate_thickness)
base = base - Box(slot_length, slot_width, plate_thickness)

tab_pos = plate_length/2 - tab_overlap + tab_length/2
tab = Pos(tab_pos, 0, 0) * Box(tab_length, tab_width, tab_thickness)
tab_mirror = Pos(-tab_pos, 0, 0) * Box(tab_length, tab_width, tab_thickness)

part = base + tab + tab_mirror
part.name = "plate_with_tabs"
export_step(part, "output.step")