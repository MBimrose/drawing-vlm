from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 5.0
rib_height = 2.0
rib_width = 4.0
rib_margin = 5.0
central_hole_diameter = 8.0
array_hole_diameter = 4.0
array_rows = 3
array_cols = 4
array_spacing_x = 15.0
array_spacing_y = 15.0
fillet_radius = 0.8

base = Box(plate_length, plate_width, plate_thickness)
rib1 = Pos(0, 0, plate_thickness) * Box(plate_length - 2 * rib_margin, rib_width, rib_height)
rib2 = Pos(0, 0, plate_thickness) * Box(rib_width, plate_width - 2 * rib_margin, rib_height)

solid_body = base + rib1 + rib2

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = fillet(top_face.edges(), fillet_radius)

hole_depth = plate_thickness + rib_height + 10
solid_body = solid_body - Cylinder(central_hole_diameter / 2, hole_depth)

for i in range(array_cols):
    for j in range(array_rows):
        x = (i - (array_cols - 1) / 2) * array_spacing_x
        y = (j - (array_rows - 1) / 2) * array_spacing_y
        solid_body = solid_body - Pos(x, y, 0) * Cylinder(array_hole_diameter / 2, hole_depth)

part = solid_body
part.name = "plate_with_ribs_and_holes"
export_step(part, "output.step")