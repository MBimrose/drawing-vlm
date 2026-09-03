from build123d import *

plate_length = 80.0
plate_width = 40.0
plate_thickness = 5.0
boss_diameter = 20.0
boss_height = 10.0
hole_diameter = 4.0
hole_spacing_x = 15.0
hole_spacing_y = 12.0
hole_rows = 2
hole_cols = 4
fillet_radius = 1.5
rib_thickness = 2.0
rib_height = 2.0
rib_offset = 5.0

base = Box(plate_length, plate_width, plate_thickness)
base = fillet(base.edges().filter_by(Axis.Z), fillet_radius)

boss = Pos(0, 0, plate_thickness/2 + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
result = base + boss

rib = Pos(0, -plate_width/2 + rib_offset + rib_thickness/2, -plate_thickness/2 - rib_height/2) * Box(plate_length - 2*rib_offset, rib_thickness, rib_height)
result = result + rib

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        y = (j - (hole_rows - 1) / 2) * hole_spacing_y
        result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, 100)

part = result
part.name = "plate_with_boss_rib_and_holes"
export_step(part, "output.step")