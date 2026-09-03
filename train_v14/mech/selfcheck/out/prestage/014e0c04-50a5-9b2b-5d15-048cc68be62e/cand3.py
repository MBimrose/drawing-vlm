from build123d import *

plate_length = 80.0
plate_width = 40.0
plate_thickness = 6.0
rib_height = 3.0
rib_width = 6.0
rib_length = plate_length - 10.0
notch_width = 12.0
notch_depth = 6.0
hole_diameter = 5.0
hole_spacing = 50.0
chamfer_size = 0.5

result = Box(plate_length, plate_width, plate_thickness)

notch = Pos(0, plate_width/2 - notch_depth/2, 0) * Box(notch_width, notch_depth, plate_thickness)
result = result - notch

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

rib = Pos(0, 0, plate_thickness/2 + rib_height/2) * Box(rib_width, rib_length, rib_height)
result = result + rib

for x in [-hole_spacing/2, hole_spacing/2]:
    hole = Pos(x, 0, 0) * Cylinder(hole_diameter/2, plate_thickness + rib_height + 10)
    result = result - hole

part = result
part.name = "plate_with_rib_notch_and_holes"
export_step(part, "output.step")