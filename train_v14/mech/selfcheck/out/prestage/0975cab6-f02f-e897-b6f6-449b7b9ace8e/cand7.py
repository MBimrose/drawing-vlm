from build123d import *

plate_length = 80.0
plate_width = 40.0
plate_thickness = 4.0
tab_width = 8.0
tab_notch_width = 4.0
tab_notch_depth = 2.0
pocket_length = 30.0
pocket_width = 15.0
pocket_depth = 2.0
hole_diameter = 4.0
hole_spacing = 25.0
counterbore_diameter = 6.0
counterbore_depth = 1.0
fillet_radius = 0.5

base = Box(plate_length, plate_width, plate_thickness)
tab = Pos(0, plate_width/2 + tab_width/2, 0) * Box(plate_length, tab_width, plate_thickness)
notch = Pos(plate_length/2 - tab_notch_width/2, plate_width/2 + tab_width/2, 0) * Box(tab_notch_width, tab_notch_depth, plate_thickness)
tab = tab - notch
result = base + tab

pocket = Pos(0, 0, plate_thickness/2 - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
result = result - pocket

for x in [-hole_spacing/2, hole_spacing/2]:
    cbore = Pos(x, 0, plate_thickness/2 - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)
    hole = Pos(x, 0, 0) * Cylinder(hole_diameter/2, plate_thickness)
    result = result - cbore - hole

result = fillet(result.edges().filter_by(Axis.Z), fillet_radius)

part = result
part.name = "plate_with_tab"
export_step(part, "output.step")