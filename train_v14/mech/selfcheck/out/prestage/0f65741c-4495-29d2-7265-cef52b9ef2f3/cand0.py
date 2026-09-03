from build123d import *

plate_width = 80.0
plate_depth = 30.0
plate_thickness = 5.0
tab_radius = 10.0
tab_offset = 30.0
slot_width = 5.0
slot_length = 15.0
hole_diameter = 4.0
hole_spacing = 40.0
hole_offset_y = 5.0
chamfer_size = 1.0
fillet_radius = 1.0

base = Box(plate_width, plate_depth, plate_thickness)
left_tab = Pos(-tab_offset, plate_depth/2 - tab_radius/2, 0) * Cylinder(tab_radius, plate_thickness)
right_tab = Pos(tab_offset, plate_depth/2 - tab_radius/2, 0) * Cylinder(tab_radius, plate_thickness)
result = base + left_tab + right_tab

slot = Box(slot_width, slot_length, plate_thickness)
result = result - slot

for x, y in [(-hole_spacing/2, hole_offset_y), (hole_spacing/2, hole_offset_y)]:
    result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)
result = fillet(result.edges().sort_by(Axis.Z)[-1:], fillet_radius)

part = result
part.name = "plate_with_tabs"
export_step(part, "output.step")