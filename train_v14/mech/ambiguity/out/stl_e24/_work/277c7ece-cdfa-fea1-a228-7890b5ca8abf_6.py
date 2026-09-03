from build123d import *

plate_width = 80.0
plate_length = 60.0
plate_thickness = 8.0
rib_height = 6.0
rib_thickness = 4.0
fillet_radius_outer = 2.0
fillet_radius_inner = 1.5
hole_diameter = 4.0
hole_spacing_x = 20.0
hole_spacing_y = 20.0
num_holes_x = 3
num_holes_y = 2

base = Box(plate_width, plate_length, plate_thickness)
base = fillet(base.edges().filter_by(Axis.Z), fillet_radius_outer)

rib_outer = Pos(0, 0, plate_thickness/2 + rib_height/2) * Box(plate_width, plate_length, rib_height)
rib_inner = Pos(0, 0, plate_thickness/2 + rib_height/2) * Box(plate_width - 2*rib_thickness, plate_length - 2*rib_thickness, rib_height)
rib = rib_outer - rib_inner
rib = fillet(rib.edges().filter_by(Axis.Z), fillet_radius_inner)

combined = base + rib

hole_r = hole_diameter / 2
hole_h = plate_thickness + rib_height + 10
for i in range(num_holes_x):
    for j in range(num_holes_y):
        x = (i - (num_holes_x - 1) / 2) * hole_spacing_x
        y = (j - (num_holes_y - 1) / 2) * hole_spacing_y
        combined = combined - Pos(x, y, 0) * Cylinder(hole_r, hole_h)

part = combined
part.name = "plate_with_rib_and_holes"
export_step(part, "output.step")