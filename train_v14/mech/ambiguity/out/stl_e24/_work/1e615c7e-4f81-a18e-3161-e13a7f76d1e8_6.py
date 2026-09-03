from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 6.0
tab_length = 30.0
tab_width = 15.0
hole_diameter = 12.0
rib_width = 30.0
rib_length = 50.0
rib_height = 4.0
rib_offset_x = 10.0
fillet_radius = 2.0

base_plate = Box(plate_length, plate_width, plate_thickness)
tab = Pos(plate_length/2 + tab_length/2, 0, 0) * Box(tab_length, tab_width, plate_thickness)
result = base_plate + tab

hole = Pos(plate_length/3, 0, 0) * Cylinder(hole_diameter/2, plate_thickness + 2)
result = result - hole

rib = Pos(rib_offset_x, 0, plate_thickness/2 + rib_height/2) * Box(rib_width, rib_length, rib_height)
result = result + rib

result = fillet(result.edges().filter_by(Axis.Z), fillet_radius)

part = result
part.name = "plate_with_tab_rib_and_hole"
export_step(part, "output.step")