from build123d import *

plate_length = 100.0
plate_width = 70.0
plate_thickness = 8.0
boss_radius = 20.0
boss_height = 6.0
hole_diameter = 6.0
hole_spacing_x = 20.0
hole_spacing_y = 20.0
hole_rows = 3
hole_cols = 4
edge_margin = 10.0
rib_width = 8.0
rib_height = 4.0
chamfer_dist = 0.5

result = Box(plate_length, plate_width, plate_thickness)
result = result + Pos(0, 0, plate_thickness/2) * Cylinder(boss_radius, boss_height)

rib_offset_x = plate_length/2 - edge_margin - rib_width/2
rib1 = Pos(-rib_offset_x, 0, plate_thickness/2) * Box(rib_width, plate_width - 2*edge_margin, rib_height)
rib2 = Pos(rib_offset_x, 0, plate_thickness/2) * Box(rib_width, plate_width - 2*edge_margin, rib_height)
result = result + rib1 + rib2

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols-1)/2) * hole_spacing_x
        y = (j - (hole_rows-1)/2) * hole_spacing_y
        result = result - Pos(x, y, plate_thickness/2) * Cylinder(hole_diameter/2, 30)

result = chamfer(result.edges(), chamfer_dist)

part = result
part.name = "plate_with_boss_ribs_and_holes"
export_step(part, "output.step")