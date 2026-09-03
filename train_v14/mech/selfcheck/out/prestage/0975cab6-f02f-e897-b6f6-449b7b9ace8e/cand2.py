from build123d import *

plate_length = 80.0
plate_width = 40.0
plate_thickness = 4.0
tab_length = 20.0
tab_width = 8.0
pocket_length = 30.0
pocket_width = 15.0
pocket_depth = 2.0
hole_diameter = 4.0
hole_spacing = 25.0
fillet_radius = 0.5

base_plate = Box(plate_length, plate_width, plate_thickness)
tab = Pos(plate_length/2 - tab_length/2, 0, 0) * Box(tab_length, tab_width, plate_thickness)
combined = base_plate + tab

pocket = Pos(0, 0, plate_thickness/2 - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
combined = combined - pocket

for x in [-hole_spacing/2, hole_spacing/2]:
    combined = combined - Pos(x, 0, 0) * Cylinder(hole_diameter/2, plate_thickness + 1)

combined = fillet(combined.edges().filter_by(Axis.Z), fillet_radius)

part = combined
part.name = "plate_with_tab_pocket_holes"
export_step(part, "output.step")