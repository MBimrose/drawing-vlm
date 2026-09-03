from build123d import *

plate_length = 80.0
plate_width = 20.0
plate_thickness = 10.0
tab_length = 30.0
tab_width = 10.0
pocket_length = 20.0
pocket_width = 10.0
pocket_depth = 4.0
hole_diameter = 4.0
hole_spacing = 12.0
hole_count = 6
chamfer_size = 1.0

base = Box(plate_length, plate_width, plate_thickness)
tab = Pos(plate_length/2 + tab_length/2, 0, 0) * Box(tab_length, tab_width, plate_thickness)
result = base + tab

pocket = Pos(0, 0, plate_thickness/2 - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
result = result - pocket

for i in range(hole_count):
    x = (i - (hole_count - 1) / 2) * hole_spacing
    result = result - Pos(x, 0, 0) * Cylinder(hole_diameter/2, plate_thickness + 1)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "plate_with_tab_pocket_holes"
export_step(part, "output.step")