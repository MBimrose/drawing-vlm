from build123d import *

plate_length = 80.0
plate_width = 40.0
plate_thickness = 5.0
rib_height = 12.0
rib_thickness = 5.0
notch_radius = 4.0
notch_offset = 15.0
fillet_radius = 1.8
hole_diameter = 4.0
hole_spacing = 20.0

base = Box(plate_length, plate_width, plate_thickness)
base = fillet(base.edges().filter_by(Axis.Z), fillet_radius)

rib = Pos(0, plate_width/2 - rib_thickness/2, plate_thickness/2 + rib_height/2) * Box(plate_length, rib_thickness, rib_height)
rib = fillet(rib.edges().filter_by(Axis.X), fillet_radius)

result = base + rib

notch = Pos(0, -plate_width/2 + notch_offset, 0) * Rot(0, 90, 0) * Cylinder(notch_radius, plate_length)
result = result - notch

for x in [-hole_spacing/2, hole_spacing/2]:
    hole = Pos(x, plate_width/2 - rib_thickness/2, plate_thickness/2 + rib_height/2) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, plate_length)
    result = result - hole

part = result
part.name = "plate_with_rib_notch_and_holes"
export_step(part, "output.step")