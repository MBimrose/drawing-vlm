from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 5.0
rib_width = 10.0
rib_height = 2.0
recess_radius = 15.0
recess_depth = 2.0
hole_diameter = 5.0
hole_spacing_x = 20.0
hole_spacing_y = 30.0
hole_rows = 2
hole_cols = 4
chamfer_size = 0.5

base = Box(plate_length, plate_width, plate_thickness)
rib = Pos(0, 0, plate_thickness/2 + rib_height/2) * Box(plate_length, rib_width, rib_height)
result = base + rib

recess = Pos(0, 0, plate_thickness/2 + rib_height - recess_depth/2) * Cylinder(recess_radius, recess_depth)
result = result - recess

hole_h = plate_thickness + rib_height + 10
for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        y = (j - (hole_rows - 1) / 2) * hole_spacing_y
        result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, hole_h)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "plate_with_rib_recess_and_holes"
export_step(part, "output.step")