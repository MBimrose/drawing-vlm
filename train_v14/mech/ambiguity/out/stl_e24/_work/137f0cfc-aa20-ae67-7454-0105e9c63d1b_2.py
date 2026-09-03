from build123d import *

plate_width = 80.0
plate_height = 60.0
plate_thickness = 5.0
cutout_diameter = 30.0
hole_diameter = 10.0
hole_spacing = 30.0
fillet_radius = 1.0
rib_width = 10.0
rib_height = 2.0
tab_width = 20.0
tab_height = 15.0

result = Box(plate_width, plate_height, plate_thickness)

top_face = result.faces().sort_by(Axis.Z)[-1]
result = fillet(top_face.edges(), fillet_radius)

result = result - Cylinder(cutout_diameter/2, plate_thickness)

for x in [-hole_spacing/2, hole_spacing/2]:
    result = result - Pos(x, 0, 0) * Cylinder(hole_diameter/2, plate_thickness)

rib = Pos(0, 0, -plate_thickness/2 - rib_height/2) * Box(rib_width, plate_height - 2*tab_height, rib_height)
result = result + rib

tab = Pos(0, plate_height/2 + tab_height/2, 0) * Box(tab_width, tab_height, plate_thickness)
result = result + tab

part = result
part.name = "plate_with_rib_and_tab"
export_step(part, "output.step")