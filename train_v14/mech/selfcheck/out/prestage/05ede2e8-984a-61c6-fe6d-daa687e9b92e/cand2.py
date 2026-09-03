from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 5.0
rib_height = 2.0
rib_width = 4.0
hole_diameter = 4.0
hole_spacing_x = 15.0
hole_spacing_y = 15.0
hole_rows = 3
hole_cols = 4
fillet_radius = 0.8
central_hole_diameter = 8.0
boss_diameter = 10.0
boss_height = 2.0

result = Box(plate_length, plate_width, plate_thickness)
result = result - Cylinder(central_hole_diameter/2, plate_thickness)
result = result + Pos(0, 0, plate_thickness) * Box(plate_length - 10, rib_width, rib_height)
result = result + Pos(0, 0, plate_thickness) * Box(rib_width, plate_width - 10, rib_height)
result = result + Pos(0, 0, plate_thickness) * Cylinder(boss_diameter/2, boss_height)

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        y = (j - (hole_rows - 1) / 2) * hole_spacing_y
        result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness + rib_height + 10)

top_face = result.faces().sort_by(Axis.Z)[-1]
result = fillet(top_face.edges(), fillet_radius)

part = result
part.name = "plate_with_ribs_and_holes"
export_step(part, "output.step")