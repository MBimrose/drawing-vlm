from build123d import *

plate_length = 80.0
plate_width = 30.0
plate_thickness = 5.0
tab_radius = 10.0
slot_width = 5.0
slot_length = 15.0
slot_offset_y = -5.0
hole_diameter = 4.0
hole_offset_x = 20.0
hole_offset_y = 10.0
fillet_radius = 1.0
chamfer_distance = 1.0

base = Box(plate_length, plate_width, plate_thickness)
left_tab = Pos(-plate_length/2 + tab_radius, plate_width/2 - tab_radius, 0) * Cylinder(tab_radius, plate_thickness)
right_tab = Pos(plate_length/2 - tab_radius, plate_width/2 - tab_radius, 0) * Cylinder(tab_radius, plate_thickness)
result = base + left_tab + right_tab

slot = Pos(0, slot_offset_y, 0) * Box(slot_width, slot_length, plate_thickness)
result = result - slot

for x, y in [(-hole_offset_x, hole_offset_y), (hole_offset_x, hole_offset_y)]:
    result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_distance)
top_edges = result.edges().sort_by(Axis.Z)[-1:]
result = fillet(top_edges, fillet_radius)

part = result
part.name = "plate_with_tabs"
export_step(part, "output.step")