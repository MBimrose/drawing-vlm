from build123d import *

plate_length = 80.0
plate_width = 20.0
plate_thickness = 8.0
tab_length = 20.0
tab_width = 12.0
slot_width = 2.0
slot_depth = 6.0
hole_diameter = 4.0
countersink_diameter = 6.0
countersink_angle = 82.0
chamfer_size = 0.2

base = Box(plate_length, plate_width, plate_thickness)
tab = Pos(plate_length/2 + tab_length/2, 0, 0) * Box(tab_length, tab_width, plate_thickness)
result = base + tab

slot_cut = Pos(plate_length/2 + tab_length/2, 0, 0) * Box(slot_width, slot_depth, plate_thickness)
result = result - slot_cut

hole_positions = [(-plate_length/3, -plate_width/4), (plate_length/3, -plate_width/4)]
for x, y in hole_positions:
    csk = Pos(x, y, plate_thickness/2) * CounterSinkHole(hole_diameter/2, countersink_diameter/2, plate_thickness, countersink_angle)
    result = result - csk

vertical_edges = result.edges().filter_by(Axis.Z)
result = chamfer(vertical_edges, chamfer_size)

part = result
part.name = "plate_with_tab_and_holes"
export_step(part, "output.step")